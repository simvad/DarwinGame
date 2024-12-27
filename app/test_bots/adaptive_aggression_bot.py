class Bot:
    def __init__(self):
        self.opponent_aggressive_count = 0
        self.total_moves = 0
        
    def get_move(self, history, opponent_history, round_number):
        if opponent_history:
            self.total_moves += 1
            if opponent_history[-1] == 3:
                self.opponent_aggressive_count += 1
                
            aggression_ratio = self.opponent_aggressive_count / self.total_moves
            
            if aggression_ratio > 0.4:  # Opponent is aggressive
                return 1
            elif aggression_ratio < 0.2:  # Opponent is conservative
                return 3
                
        # Play aggressive early in each round
        if len(history) < 2:
            return 3
        return 2
        
    def reset(self):
        self.opponent_aggressive_count = 0
        self.total_moves = 0
