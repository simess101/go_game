import numpy as np
import gym
from gym import spaces
from game.board import Board


class GoEnv(gym.Env):
    """Custom environment for training an AI to play Go."""
    def __init__(self, board_size=9):
        super(GoEnv, self).__init__()
        self.board_size = board_size
        self.board = Board(board_size)
        self.action_space = spaces.Discrete(board_size * board_size)  # Possible moves
        self.observation_space = spaces.Box(
            low=0, high=2, shape=(board_size, board_size), dtype=np.int32
        )
        self.current_player = 1  # Black starts

    def reset(self):
        """Reset the environment to its initial state."""
        self.board.reset_board()
        self.current_player = 1
        return self.board.get_board_state()

    def step(self, action):
        """Take a step in the environment."""
        x, y = divmod(action, self.board_size)

        # Handle invalid moves
        if not self.board.place_stone(x, y):
            return self.board.get_board_state(), -1, True, {}  # Penalty for invalid moves

        # Check for game end condition
        done = np.all(self.board.get_board_state() != 0)  # Full board ends the game
        reward = self.calculate_reward()

        # Switch player
        self.current_player = 3 - self.current_player
        return self.board.get_board_state(), reward, done, {}

    def calculate_reward(self):
        """Calculate reward for the current player."""
        black_score, white_score = self.board.calculate_score()
        return black_score - white_score if self.current_player == 1 else white_score - black_score

    def render(self, mode="human"):
        """Render the board state."""
        print(self.board.get_board_state())
