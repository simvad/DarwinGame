class Bot:
    def get_move(self, history, opponent_history, round_number):
        # Tries to maximize points by playing 3 when it thinks it can
        if not opponent_history or opponent_history[-1] <= 2:
            return 3
        return 2
        
    def reset(self):
        pass