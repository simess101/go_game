import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

import numpy as np
from stable_baselines3 import PPO
from ml.go_env import GoEnv

from imitation.algorithms.bc import BC
from imitation.data.types import Trajectory
from imitation.data import rollout

# Load your demonstration data
data_path = "data/demos.npz"
if not os.path.exists(data_path):
    raise FileNotFoundError("No demos.npz file found. Play a game first to generate demonstrations.")

data = np.load(data_path)
states = data["states"]    # shape: (num_steps, board_size, board_size)
actions = data["actions"]  # shape: (num_steps,)

if len(states) == 0 or len(actions) == 0:
    raise ValueError("The demonstrations file is empty. Play a game with moves before ending it.")

# Ensure we have one more observation than actions
if len(states) == len(actions):
    # Remove the last action to meet the requirement obs = acts + 1
    actions = actions[:-1]

if len(states) != len(actions) + 1:
    raise ValueError(
        f"Number of states must be exactly one more than number of actions. "
        f"states: {len(states)}, actions: {len(actions)}"
    )

# Create infos as empty dictionaries, one per action
infos = [{} for _ in range(len(actions))]

# Construct a single trajectory
trajectory = Trajectory(
    obs=states,
    acts=actions,
    infos=infos,
    terminal=True
)

demonstrations = rollout.flatten_trajectories([trajectory])

# Initialize environment and a dummy PPO model (just for policy initialization)
board_size = 9
env = GoEnv(board_size=board_size)
model = PPO("MlpPolicy", env, verbose=1)

# Create a random generator for BC
rng = np.random.default_rng()

# Use the policy's observation and action space instead of the env's
bc_trainer = BC(
    observation_space=model.policy.observation_space,
    action_space=model.policy.action_space,
    demonstrations=demonstrations,
    policy=model.policy,
    rng=rng
)

# Train the policy using Behavior Cloning
print("Starting Behavior Cloning training...")
bc_trainer.train(n_epochs=50)
print("BC training completed.")

# Save the BC-initialized policy
policy_save_path = "go_bc_policy"
bc_trainer.policy.save(policy_save_path)
print(f"Policy saved to {policy_save_path}")
