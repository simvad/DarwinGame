class Bot:
    def __init__(self):
        self.pattern = [1, 2, 2, 1, 3]
        self.index = 0
        
    def get_move(self, history, opponent_history, round_number):
        move = self.pattern[self.index]
        self.index = (self.index + 1) % len(self.pattern)
        return move
        
    def reset(self):
        self.index = 0
