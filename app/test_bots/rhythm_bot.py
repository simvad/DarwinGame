class Bot:
    def __init__(self):
        self.turn_count = 0
        
    def get_move(self, history, opponent_history, round_number):
        self.turn_count += 1
        # Play a rhythm of 3,1,3,1 to maximize points while staying unpredictable
        if self.turn_count % 2 == 0:
            return 1
        return 3
        
    def reset(self):
        self.turn_count = 0
