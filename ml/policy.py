import random


class GoPolicy:
    def __init__(self, board_size=9):
        self.board_size = board_size

    def choose_action(self, state):
        """Select a random valid action."""
        empty_positions = [
            (x, y)
            for x in range(self.board_size)
            for y in range(self.board_size)
            if state[y][x] == 0
        ]
        if not empty_positions:
            return None  # No valid moves left
        return random.choice(empty_positions)
