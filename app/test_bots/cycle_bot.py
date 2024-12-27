class Bot:
    def __init__(self):
        self.cycles = [
            [3,1,3,1],  # Aggressive cycle
            [2,2,3,1],  # Balanced cycle
            [1,2,2,1]   # Conservative cycle
        ]
        self.current_cycle = 0
        self.position = 0
        
    def get_move(self, history, opponent_history, round_number):
        if opponent_history:
            # Switch cycles based on opponent's last move
            if opponent_history[-1] == 3:
                self.current_cycle = 2  # Use conservative cycle
            elif opponent_history[-1] == 1:
                self.current_cycle = 0  # Use aggressive cycle
            else:
                self.current_cycle = 1  # Use balanced cycle
                
        move = self.cycles[self.current_cycle][self.position]
        self.position = (self.position + 1) % len(self.cycles[self.current_cycle])
        return move
        
    def reset(self):
        self.current_cycle = 0
        self.position = 0
