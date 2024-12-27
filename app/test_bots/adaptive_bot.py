class Bot:
    def __init__(self):
        self.opponent_tendencies = {1: 0, 2: 0, 3: 0}
        
    def get_move(self, history, opponent_history, round_number):
        if opponent_history:
            self.opponent_tendencies[opponent_history[-1]] += 1
            most_likely = max(self.opponent_tendencies, key=self.opponent_tendencies.get)
            # Choose the largest number that won't exceed sum of 5
            return min(5 - most_likely, 3)
        return 2  # Default first move
        
    def reset(self):
        self.opponent_tendencies = {1: 0, 2: 0, 3: 0}