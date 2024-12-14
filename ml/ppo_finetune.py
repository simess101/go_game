import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from stable_baselines3 import PPO
from ml.go_env import GoEnv

board_size = 9
env = GoEnv(board_size=board_size)

# Initialize a PPO model
model = PPO("MlpPolicy", env, verbose=1)

# Load the BC-trained weights into the PPO model's policy
model.policy.load("go_bc_policy")

# Now continue training with PPO
timesteps = 100000  # Adjust this as desired
print(f"Continuing training for {timesteps} timesteps using PPO...")
model.learn(total_timesteps=timesteps)

# Save the refined model
model_path = "go_ai_model"
model.save(model_path)
print(f"Refined model saved to {model_path}")
