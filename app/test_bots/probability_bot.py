class Bot:
    def get_move(self, history, opponent_history, round_number):
        import random
        
        if not opponent_history:
            return 2
            
        # Calculate probability distribution based on opponent's history
        total = len(opponent_history)
        probs = {
            1: opponent_history.count(1) / total,
            2: opponent_history.count(2) / total,
            3: opponent_history.count(3) / total
        }
        
        # Choose move based on expected value
        expected_values = {
            1: 1,  # Always safe
            2: 2 * (probs[1] + probs[2] + 0.5 * probs[3]),
            3: 3 * (probs[1] + 0.6 * probs[2])
        }
        
        return max(expected_values, key=expected_values.get)
        
    def reset(self):
        pass