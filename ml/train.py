import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from stable_baselines3 import PPO
from ml.go_env import GoEnv
from model import GoAIModel

# Initialize the board size
board_size = 9  # Change this to 13 or 19 for larger boards

# Initialize the Go environment
env = GoEnv(board_size)

# Initialize the AI model with the environment and board size
go_ai = GoAIModel(env, board_size)

# Train the model
timesteps = 100000  # Adjust the number of timesteps as needed
print(f"Training for {timesteps} timesteps...")
go_ai.train(timesteps=timesteps)

# Save the trained model
model_path = "go_ai_model"
go_ai.save(model_path)
print(f"Model saved to {model_path}")
