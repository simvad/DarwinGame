class Bot:
    def __init__(self):
        self.consecutive_success = 0
        
    def get_move(self, history, opponent_history, round_number):
        if history and opponent_history:
            last_sum = history[-1] + opponent_history[-1]
            if last_sum <= 5:
                self.consecutive_success += 1
            else:
                self.consecutive_success = 0
        
        # Increase aggression with successive successful moves
        if self.consecutive_success >= 2:
            return 3
        elif self.consecutive_success == 1:
            return 2
        return 1
        
    def reset(self):
        self.consecutive_success = 0
