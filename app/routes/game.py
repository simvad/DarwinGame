from flask import Blueprint, render_template, jsonify, request, Response, session, redirect, url_for, current_app
from app.models.game import game_manager
from app.models.database import Admin, StoredGame, db
import json
import time

game_bp = Blueprint('game', __name__)

@game_bp.route('/test/create')
def create_test_game():
    # Create a test game
    game_id = game_manager.create_game(
        title="Test Game",
        min_rounds=3,
        max_rounds=5,
        min_turns=3,
        max_turns=5,
        admin_id=1  # Default test admin
    )
    
    # Add test bots
    test_bots = {
        "RandomBot": """
class Bot:
    def get_move(self, history, opponent_history, round_number):
        import random
        return random.randint(1, 3)
    
    def reset(self):
        pass
""",
        "ConstantBot": """
class Bot:
    def get_move(self, history, opponent_history, round_number):
        return 2
    
    def reset(self):
        pass
"""
    }
    
    # Create invites and submit bots
    for bot_name, bot_code in test_bots.items():
        invite_code = game_manager.create_invite(game_id)
        game_manager.submit_bot(invite_code, bot_name, bot_code)
    
    return redirect(url_for('game.view_game', game_id=game_id))

@game_bp.route('/test')
def test_page():
    return render_template('test.html')

@game_bp.route('/')
def home():
    if current_app.config.get('TESTING'):
        # In test mode, redirect to the test game
        from app.models.game import game_manager
        # Get first game since in test mode we only have one game
        game_id = next(iter(game_manager.games.keys()))
        return redirect(url_for('game.view_game', game_id=game_id))
    else:
        # Normal production behavior
        if 'admin_id' in session:
            admin = Admin.query.get(session['admin_id'])
            if admin:
                return redirect(url_for('admin.admin'))
        return render_template('home.html')

@game_bp.route('/submit/<invite_code>')
def submit_page(invite_code):
    invite = game_manager.get_invite(invite_code)  # Need to add this method to GameManager
    if not invite or invite.used:
        return "Invalid or used invite code", 404
        
    game = game_manager.get_game(invite.game_id)
    if not game or game.started:
        return "Game not found or already started", 404
        
    return render_template('submit.html', 
                         invite_code=invite_code,
                         game_title=game.title)

@game_bp.route('/submit/<invite_code>', methods=['POST'])
def submit_bot(invite_code):
    try:
        if not request.is_json:
            return jsonify({
                'success': False, 
                'error_type': 'format',
                'errors': 'Invalid request format. Please submit the form properly.'
            }), 400

        data = request.get_json()
        
        if 'bot_name' not in data or 'bot_code' not in data:
            return jsonify({
                'success': False,
                'error_type': 'missing_fields',
                'errors': 'Missing required fields. Please provide both bot name and code.'
            }), 400

        success = game_manager.submit_bot(
            invite_code,
            data['bot_name'],
            data['bot_code']
        )
        return jsonify({'success': success})
    except ValueError as e:
        return jsonify({
            'success': False,
            'error_type': 'validation',
            'errors': str(e)
        })
    except Exception as e:
        print(f"Error submitting bot: {str(e)}")  # Log the error server-side
        return jsonify({
            'success': False,
            'error_type': 'unexpected',
            'errors': str(e)
        }), 500

@game_bp.route('/game/<game_id>')
def view_game(game_id):
    game = game_manager.get_game(game_id)
    if not game:
        return "Game not found", 404
    return render_template('game.html', game=game)

@game_bp.route('/game/next_round/<game_id>', methods=['POST'])
def next_round(game_id):
    game = game_manager.get_game(game_id)
    if not game:
        return jsonify({'success': False, 'error': 'Game not found'}), 404
    
    success = game_manager.play_next_round(game_id)
    return jsonify({'success': success})

@game_bp.route('/game/status/<game_id>')
def game_status(game_id):
    def generate():
        game = game_manager.get_game(game_id)
        if not game:
            return
            
        last_round = -1
        
        # Send initial state if game has already started
        if game.started and len(game.round_results) > 0:
            data = {
                'round': 0,
                'results': game.round_results[0]
            }
            yield f"data: {json.dumps(data)}\n\n"
            last_round = 0
        else:
            last_round = -1
        
        # Then enter update loop for subsequent rounds
        while True:
            if game.started and last_round + 1 < len(game.round_results):
                last_round += 1
                data = {
                    'round': last_round,
                    'results': game.round_results[last_round]
                }
                yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.1)
            
    return Response(generate(), mimetype='text/event-stream')
