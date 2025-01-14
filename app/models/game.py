from dataclasses import dataclass, field
from typing import Dict, List, Optional
import secrets
from datetime import datetime
import threading
from collections import defaultdict
import random
import time
from .bot import BotValidator, BotRunner
from .database import db, StoredGame, StoredBot, StoredInvite, Admin

@dataclass
class Invite:
    code: str
    game_id: str
    used: bool = False
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Game:
    id: str
    title: str
    min_rounds: int
    max_rounds: int
    min_turns: int
    max_turns: int
    bots: Dict[str, dict] = field(default_factory=dict)  # name -> {code, class, runner}
    started: bool = False
    current_round: int = 0
    round_results: List[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

class GameManager:
    def __init__(self):
        self.games: Dict[str, Game] = {}
        self._load_active_games()
    
    def _load_active_games(self):
        """Load any non-started games from database into memory on startup."""
        stored_games = StoredGame.query.filter_by(started=False).all()
        for stored_game in stored_games:
            game = Game(
                id=stored_game.game_id,
                title=stored_game.title,
                min_rounds=stored_game.min_rounds,
                max_rounds=stored_game.max_rounds,
                min_turns=stored_game.min_turns,
                max_turns=stored_game.max_turns
            )
            # Load submitted bots for this game
            stored_bots = StoredBot.query.filter_by(game_id=stored_game.game_id).all()
            for bot in stored_bots:
                # Create bot instance
                validator = BotValidator()
                safe_env = validator.create_safe_environment()
                locals_dict = {}
                exec(bot.code, safe_env, locals_dict)
                bot_class = locals_dict.get('Bot')
                
                game.bots[bot.name] = {
                    'code': bot.code,
                    'class': bot_class,
                    'runner': BotRunner(bot_class)
                }
            
            self.games[stored_game.game_id] = game

    def create_game(self, title: str, min_rounds: int, max_rounds: int,
                   min_turns: int, max_turns: int, admin_id: int) -> str:
        """Create a new game and store it both in memory and database."""
        game_id = secrets.token_urlsafe(16)
        
        # Store in database
        stored_game = StoredGame(
            game_id=game_id,
            title=title,
            min_rounds=min_rounds,
            max_rounds=max_rounds,
            min_turns=min_turns,
            max_turns=max_turns,
            created_by=admin_id
        )
        db.session.add(stored_game)
        db.session.commit()
        
        # Store in memory for active games
        self.games[game_id] = Game(
            id=game_id,
            title=title,
            min_rounds=min_rounds,
            max_rounds=max_rounds,
            min_turns=min_turns,
            max_turns=max_turns
        )
        return game_id

    def get_game(self, game_id: str) -> Optional[Game]:
        """Get game from memory or database."""
        return self.games.get(game_id)

    def create_invite(self, game_id: str) -> str:
        """Create a new invite code for a game."""
        game = self.get_game(game_id)
        if not game:
            raise ValueError("Game not found")
            
        invite_code = secrets.token_urlsafe(16)
        
        # Store in database
        stored_invite = StoredInvite(
            code=invite_code,
            game_id=game_id
        )
        db.session.add(stored_invite)
        db.session.commit()
        
        return invite_code
    
    def get_invite(self, invite_code: str) -> Optional[StoredInvite]:
        """Get invite from database."""
        return StoredInvite.query.filter_by(code=invite_code).first()

    def submit_bot(self, invite_code: str, bot_name: str, bot_code: str) -> bool:
        """Submit a new bot using an invite code."""
        stored_invite = StoredInvite.query.filter_by(code=invite_code).first()
        if not stored_invite or stored_invite.used:
            return False
            
        game = self.get_game(stored_invite.game_id)
        if not game or game.started:
            return False
            
        # Validate bot code
        validator = BotValidator()
        if not validator.validate_source(bot_code):
            raise ValueError(validator.violations)
            
        # Create bot instance
        safe_env = validator.create_safe_environment()
        locals_dict = {}
        exec(bot_code, safe_env, locals_dict)
        bot_class = locals_dict.get('Bot')
        
        if not bot_class or not validator.validate_bot_class(bot_class):
            raise ValueError(validator.violations)
            
        # Store in database
        stored_bot = StoredBot(
            game_id=stored_invite.game_id,
            name=bot_name,
            code=bot_code
        )
        db.session.add(stored_bot)
        
        # Mark invite as used
        stored_invite.used = True
        db.session.commit()
        
        # Store in memory for active game
        game.bots[bot_name] = {
            'code': bot_code,
            'class': bot_class,
            'runner': BotRunner(bot_class)
        }
        
        return True

    def play_next_round(self, game_id: str) -> bool:
        """Play the next round of the game."""
        game = self.get_game(game_id)
        if not game or len(game.bots) < 2:
            return False

        # Initialize game state if this is the first round
        if not game.started:
            game.started = True
            game.round_results = []
            game.current_round = 0
            
            # Update database
            stored_game = StoredGame.query.filter_by(game_id=game_id).first()
            if stored_game:
                stored_game.started = True
                db.session.commit()

        # Get or initialize cumulative scores
        cumulative_scores = defaultdict(int)
        if game.round_results:
            cumulative_scores.update(game.round_results[-1]['cumulative_scores'])

        # Play the round
        round_results = self._play_round(game, cumulative_scores)
        
        # Update cumulative scores with new round results
        for bot, score in round_results['scores'].items():
            cumulative_scores[bot] += score
        
        # Include both round scores and cumulative scores
        round_results['cumulative_scores'] = dict(cumulative_scores)
        game.round_results.append(round_results)
        game.current_round += 1
        
        return True

    def _play_round(self, game: Game, cumulative_scores: dict) -> dict:
        """Play a single round of the game."""
        num_turns = random.randint(game.min_turns, game.max_turns)
        
        # Reset all bots for new round
        for bot_info in game.bots.values():
            bot_info['runner'].reset()
            
        # Create weighted population pool based on cumulative scores
        total_score = sum(cumulative_scores.values()) or len(game.bots)  # Use equal weights if no scores yet
        population_pool = []
        for bot_name in game.bots.keys():
            # Calculate number of copies based on score share (minimum 1)
            score = cumulative_scores[bot_name] or 1
            copies = max(1, int((score / total_score) * 100))
            population_pool.extend([bot_name] * copies)
        
        # Create bot pairs from weighted pool
        pairs = []
        total_pairs = len(game.bots) * 2  # Keep same total number of games
        for _ in range(total_pairs):
            if len(population_pool) < 2:  # Replenish pool if needed
                population_pool = [bot for bot_name in game.bots.keys()
                                 for bot in [bot_name] * max(1, int((cumulative_scores[bot_name] or 1) / total_score * 100))]
            bot1 = random.choice(population_pool)
            bot2 = random.choice(population_pool)  # Allow self-pairing
            pairs.append((bot1, bot2))
            
        # Play all pairs
        results = defaultdict(int)
        pair_results = []
        
        for bot1_name, bot2_name in pairs:
            bot1 = game.bots[bot1_name]['runner']
            bot2 = game.bots[bot2_name]['runner']
            
            pair_score = {'bot1': bot1_name, 'bot2': bot2_name, 'turns': []}
            
            for turn in range(num_turns):
                try:
                    move1 = bot1.execute_move(turn)
                    move2 = bot2.execute_move(turn)
                    
                    if move1 + move2 <= 5:
                        results[bot1_name] += move1
                        results[bot2_name] += move2
                        
                    pair_score['turns'].append({
                        'move1': move1,
                        'move2': move2,
                        'valid': move1 + move2 <= 5
                    })
                    
                except Exception as e:
                    print(f"Error in turn {turn}: {str(e)}")
                    
            pair_results.append(pair_score)
            
        return {
            'scores': dict(results),
            'pairs': pair_results
        }
game_manager = None

def init_game_manager():
    global game_manager
    game_manager = GameManager()

__all__ = ['Game', 'Invite', 'GameManager', 'game_manager', 'init_game_manager']
