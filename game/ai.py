import numpy as np

class GoAI:
    def __init__(self, board_size=9):
        self.board_size = board_size

    def suggest_move(self, board):
        """Suggest an optimal move given the current board state."""
        empty_positions = np.argwhere(board == 0)
        if len(empty_positions) == 0:
            return None  # No moves available
        return empty_positions[np.random.choice(len(empty_positions))]
