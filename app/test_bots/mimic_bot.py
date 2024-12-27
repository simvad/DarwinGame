class Bot:
    def __init__(self):
        self.last_successful = 2
        
    def get_move(self, history, opponent_history, round_number):
        if opponent_history:
            # Copy opponent's last move if it would have been successful
            if opponent_history[-1] <= 3:
                potential_sum = opponent_history[-1] + self.last_successful
                if potential_sum <= 5:
                    self.last_successful = opponent_history[-1]
                    return opponent_history[-1]
        return 2
        
    def reset(self):
        self.last_successful = 2