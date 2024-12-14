import numpy as np


class Board:
    def __init__(self, size=9):
        self.size = size
        self.board = np.zeros((self.size, self.size), dtype=int)  # 0: empty, 1: black, 2: white
        self.current_player = 1  # Black starts
        self.captured_black = 0  # Captured black stones by White
        self.captured_white = 0  # Captured white stones by Black
        self.previous_states = []  # For enforcing the Ko rule

    def place_stone(self, x, y):
        """Attempt to place a stone. Returns True if successful."""
        if self.board[y][x] != 0:  # Position already occupied
            return False

        # Temporarily place the stone
        self.board[y][x] = self.current_player

        # Check if it captures opponent stones
        captured_any = self.capture_stones(x, y)

        # Check for suicide rule (no liberties after placement)
        group = self.get_group(x, y)
        if not captured_any and not self.has_liberties(group):
            self.board[y][x] = 0  # Undo the move
            return False

        # Prevent Ko: Check if this move repeats a previous board state
        if self.is_ko():
            self.board[y][x] = 0
            return False

        # Save the current state for Ko rule enforcement
        self.previous_states.append(self.board.copy())

        # Switch player
        self.current_player = 3 - self.current_player
        return True


    def get_board_state(self):
        """Return the current board state."""
        return self.board.copy()

    def get_group(self, x, y):
        """Get the group of connected stones starting from (x, y)."""
        color = self.board[y][x]
        visited = set()
        group = []
        stack = [(x, y)]

        while stack:
            cx, cy = stack.pop()
            if (cx, cy) not in visited:
                visited.add((cx, cy))
                group.append((cx, cy))

                for nx, ny in self.get_neighbors(cx, cy):
                    if self.board[ny][nx] == color:
                        stack.append((nx, ny))
        return group

    def has_liberties(self, group):
        """Check if a group of stones has liberties (empty adjacent spaces)."""
        for x, y in group:
            for nx, ny in self.get_neighbors(x, y):
                if self.board[ny][nx] == 0:  # Empty space
                    return True
        return False

    def capture_stones(self, x, y):
        """Check and capture opponent stones with no liberties."""
        opponent = 3 - self.current_player
        captured = []

        for nx, ny in self.get_neighbors(x, y):
            if self.board[ny][nx] == opponent:
                group = self.get_group(nx, ny)
                if not self.has_liberties(group):
                    captured.extend(group)

        # Remove captured stones
        for cx, cy in captured:
            self.board[cy][cx] = 0
            if opponent == 1:
                self.captured_black += 1
            else:
                self.captured_white += 1

        return len(captured) > 0  # Return True if any stones were captured


    def is_ko(self):
        """Check if the current board state repeats a previous state."""
        return any(np.array_equal(self.board, state) for state in self.previous_states)

    def get_territory(self, x, y):
        """Determine the owner of a territory starting at (x, y)."""
        queue = [(x, y)]
        visited = set()
        territory = []
        borders = set()

        while queue:
            cx, cy = queue.pop(0)
            if (cx, cy) not in visited:
                visited.add((cx, cy))
                territory.append((cx, cy))

                for nx, ny in self.get_neighbors(cx, cy):
                    if self.board[ny][nx] == 0:
                        queue.append((nx, ny))
                    else:
                        borders.add(self.board[ny][nx])

        # Determine owner
        if len(borders) == 1:
            owner = borders.pop()
        else:
            owner = 0  # Neutral territory
        return territory, owner

    def calculate_score(self):
        """Calculate the score for both players."""
        visited = set()
        black_territory = 0
        white_territory = 0

        for y in range(self.size):
            for x in range(self.size):
                if (x, y) not in visited and self.board[y][x] == 0:
                    territory, owner = self.get_territory(x, y)
                    visited.update(territory)
                    if owner == 1:
                        black_territory += len(territory)
                    elif owner == 2:
                        white_territory += len(territory)

        # Add captured stones to the score
        black_score = black_territory + self.captured_white
        white_score = white_territory + self.captured_black
        return black_score, white_score

    def get_neighbors(self, x, y):
        """Get all valid neighbors of a position (x, y)."""
        neighbors = []
        if x > 0:
            neighbors.append((x - 1, y))
        if x < self.size - 1:
            neighbors.append((x + 1, y))
        if y > 0:
            neighbors.append((x, y - 1))
        if y < self.size - 1:
            neighbors.append((x, y + 1))
        return neighbors

    def reset_board(self):
        """Reset the board to its initial state."""
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.current_player = 1
        self.captured_black = 0
        self.captured_white = 0
        self.previous_states = []
