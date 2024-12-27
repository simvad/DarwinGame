class Bot:
    def __init__(self):
        self.phase = 'bait'
        self.bait_count = 0
        
    def get_move(self, history, opponent_history, round_number):
        if self.phase == 'bait':
            self.bait_count += 1
            if self.bait_count >= 2:
                self.phase = 'trap'
            return 1  # Bait with safe plays
            
        if self.phase == 'trap':
            self.phase = 'bait'
            self.bait_count = 0
            return 3  # Spring the trap
            
        return 2
        
    def reset(self):
        self.phase = 'bait'
        self.bait_count = 0
