class Bot:
    def __init__(self):
        self.successful_gambits = {1: 0, 2: 0, 3: 0}
        
    def get_move(self, history, opponent_history, round_number):
        if history and opponent_history:
            last_sum = history[-1] + opponent_history[-1]
            if last_sum <= 5:
                self.successful_gambits[history[-1]] += 1
        
        # Play most successful move, weighted by points
        if sum(self.successful_gambits.values()) > 0:
            weighted_scores = {
                move: (count * move) 
                for move, count in self.successful_gambits.items()
            }
            return max(weighted_scores, key=weighted_scores.get)
            
        # Start aggressive
        return 3
        
    def reset(self):
        self.successful_gambits = {1: 0, 2: 0, 3: 0}
