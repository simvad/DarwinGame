class Bot:
    def __init__(self):
        self.successful_moves = []
        
    def get_move(self, history, opponent_history, round_number):
        if not opponent_history:
            return 2
        
        if len(history) > 0 and len(opponent_history) > 0:
            last_sum = history[-1] + opponent_history[-1]
            if last_sum <= 5:
                self.successful_moves.append(history[-1])
                
        if self.successful_moves:
            import random
            return random.choice(self.successful_moves)
        return 2
        
    def reset(self):
        self.successful_moves = []