class Bot:
    def get_move(self, history, opponent_history, round_number):
        # If opponent has played 2 twice in a row, exploit with 3
        if len(opponent_history) >= 2 and opponent_history[-1] == 2 and opponent_history[-2] == 2:
            return 3
        # If opponent just played 3, play safe with 1
        elif opponent_history and opponent_history[-1] == 3:
            return 1
        # Otherwise play 2
        return 2
        
    def reset(self):
        pass
