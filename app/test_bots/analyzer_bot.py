class Bot:
    def __init__(self):
        self.opponent_plays = []
        
    def get_move(self, history, opponent_history, round_number):
        if opponent_history:
            self.opponent_plays.append(opponent_history[-1])
            
            # Calculate opponent's tendencies
            if len(self.opponent_plays) >= 3:
                recent_plays = self.opponent_plays[-3:]
                if sum(x == 2 for x in recent_plays) >= 2:  # They like playing 2
                    return 3
                if sum(x == 1 for x in recent_plays) >= 2:  # They like playing 1
                    return 3
                if sum(x == 3 for x in recent_plays) >= 2:  # They like playing 3
                    return 1
        
        # Default to alternating between 2 and 3
        return 3 if len(history) % 2 == 0 else 2
        
    def reset(self):
        self.opponent_plays = []
