from stable_baselines3 import PPO
import numpy as np

class GoAIModel:
    def __init__(self, env, board_size):
        """Initialize the model with a given environment and board size."""
        self.model = PPO("MlpPolicy", env, verbose=1)
        self.board_size = board_size

    def train(self, timesteps=10000):
        """Train the model."""
        self.model.learn(total_timesteps=timesteps)

    def save(self, path="go_ai_model"):
        """Save the trained model."""
        self.model.save(path)

    def load(self, path="go_ai_model"):
        """Load a pre-trained model."""
        self.model = PPO.load(path)

    def predict(self, state):
        """Predict the next move based on the current state."""
        valid_moves = []
        for x in range(self.board_size):
            for y in range(self.board_size):
                if state[y][x] == 0:  # Empty position
                    valid_moves.append((x, y))

        if not valid_moves:  # No valid moves left
            print("AI decided to pass. No valid moves available.")
            return None

        # Evaluate valid moves
        best_action = None
        highest_score = -float('inf')

        print("AI is evaluating moves...")
        for x, y in valid_moves:
            action = x * self.board_size + y

            # Evaluate move using simple heuristics
            score = self.evaluate_move(state, x, y)
            print(f"Evaluated move ({x}, {y}): Score = {score}")

            if score > highest_score:
                highest_score = score
                best_action = action

        # Pass if no move scores higher than a threshold
        if highest_score <= 0:
            print("AI passed. No beneficial move found.")
            return None

        best_x, best_y = divmod(best_action, self.board_size)
        print(f"AI chose move ({best_x}, {best_y}) with score {highest_score}")
        return best_action


    def evaluate_move(self, state, x, y):
        """Evaluate the quality of a move using simple heuristics."""
        simulated_state = state.copy()
        simulated_state[y][x] = 2  # AI is player 2 (White)

        # Calculate heuristics
        liberty_count = self.count_liberties(simulated_state, x, y)
        capture_score = self.count_captures(simulated_state, x, y)
        self_capture_penalty = -10 if self.would_self_capture(simulated_state, x, y) else 0

        # Log evaluation details
        print(f"Move ({x}, {y}): Liberties = {liberty_count}, Captures = {capture_score}, Self-Capture Penalty = {self_capture_penalty}")
        return liberty_count + capture_score + self_capture_penalty


    def count_liberties(self, state, x, y):
        """Count the number of liberties (empty adjacent spaces) for a move."""
        liberties = 0
        for nx, ny in self.get_neighbors(x, y):
            if state[ny][nx] == 0:  # Empty space
                liberties += 1
        return liberties

    def count_captures(self, state, x, y):
        """Count the number of opponent stones that would be captured by a move."""
        captures = 0
        opponent = 1  # Black is opponent
        for nx, ny in self.get_neighbors(x, y):
            if state[ny][nx] == opponent and not self.has_liberties(state, nx, ny):
                captures += 1
        return captures

    def would_self_capture(self, state, x, y):
        """Check if a move would result in self-capture."""
        simulated_state = state.copy()
        simulated_state[y][x] = 2  # AI places a stone
        return not self.has_liberties(simulated_state, x, y)

    def get_neighbors(self, x, y):
        """Get valid neighbors of a position."""
        neighbors = []
        if x > 0:
            neighbors.append((x - 1, y))
        if x < self.board_size - 1:
            neighbors.append((x + 1, y))
        if y > 0:
            neighbors.append((x, y - 1))
        if y < self.board_size - 1:
            neighbors.append((x, y + 1))
        return neighbors

    def has_liberties(self, state, x, y):
        """Check if a stone or group has liberties."""
        visited = set()
        stack = [(x, y)]
        color = state[y][x]

        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))

            for nx, ny in self.get_neighbors(cx, cy):
                if state[ny][nx] == 0:  # Liberty found
                    return True
                if state[ny][nx] == color:
                    stack.append((nx, ny))

        return False





# Test the trained model
if __name__ == "__main__":
    from ml.go_env import GoEnv
    from stable_baselines3.common.vec_env import DummyVecEnv

    # Create environment and load model
    env = DummyVecEnv([lambda: GoEnv(board_size=9)])
    go_ai = GoAIModel(env)
    go_ai.load("go_ai_model")

    # Test prediction
    state = env.reset()
    action = go_ai.predict(state)
    print(f"AI predicted action: {action}")
