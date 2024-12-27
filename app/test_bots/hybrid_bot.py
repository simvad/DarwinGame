class Bot:
    def __init__(self):
        self.phase = 'explore'
        self.successful_pairs = []
        
    def get_move(self, history, opponent_history, round_number):
        if not opponent_history:
            return 2
            
        if len(history) > 0 and len(opponent_history) > 0:
            last_pair = (history[-1], opponent_history[-1])
            last_sum = sum(last_pair)
            if last_sum <= 5:
                self.successful_pairs.append(last_pair)
        
        if round_number < 33:  # Exploration phase
            import random
            return random.randint(1, 3)
        elif round_number < 66:  # Exploitation phase
            if self.successful_pairs:
                successful_move = max(move for move, _ in self.successful_pairs)
                return min(successful_move, 3)
            return 2
        else:  # Conservative phase
            return min(3, 5 - (opponent_history[-1] if opponent_history else 2))
        
    def reset(self):
        pass
