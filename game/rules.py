class Rules:
    @staticmethod
    def is_legal_move(board, x, y):
        """Check if a move is legal."""
        if board[y][x] != 0:  # Check if position is occupied
            return False
        # Add more rule checks (e.g., Ko rule)
        return True

    @staticmethod
    def check_capture(board, x, y):
        """Check if a move results in a capture."""
        # Placeholder for detailed capture logic
        pass
