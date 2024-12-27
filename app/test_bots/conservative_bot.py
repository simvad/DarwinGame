class Bot:
    def get_move(self, history, opponent_history, round_number):
        # Always plays 1 or 2 to ensure points are scored
        if not opponent_history or opponent_history[-1] <= 2:
            return 2
        return 1
        
    def reset(self):
        pass