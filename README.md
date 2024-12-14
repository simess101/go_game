# Go Game with AI

This project implements a simplified Go game environment with a graphical user interface (GUI) and provides tools to train an AI agent using Reinforcement Learning (RL) and Imitation Learning (IL). 

The AI leverages `stable-baselines3` for RL algorithms (like PPO) and the `imitation` library for behavior cloning from demonstration data.

## Features
- **GUI:** A Tkinter-based interface (`board_gui.py`) for playing a 9x9 Go game.
- **Environment:** A custom `GoEnv` integrated with Gym for RL training.
- **AI Training:** Scripts to:
  - Train from scratch using PPO (`train.py`).
  - Imitation learning using demonstration data (`imitation_train.py`).
  - Fine-tune a behavior-cloned policy with PPO (`ppo_finetune.py`).


## Requirements

- Python 3.8+
- `numpy`, `gym`, `stable-baselines3`, `imitation`, `Pillow`
- `tkinter` (built-in on many systems, else install via system package manager)

Install requirements:
<pre> pip install -r requirements.txt </pre>

If tkinter is missing on Linux:
<pre> ```bash sudo apt-get install python3-tk``` </pre>
On Windows, tkinter should be included with standard Python installations.

## Running the Project
1. Ensure Directory Structure:
You should be in the go_game directory where main.py is located.

<pre>```bash cd C:\Users\Shane\Desktop\go_game```</pre>

2. Launch the GUI:
<pre>```bash python main.py```</pre>

This opens a 9x9 Go board GUI. The default AI model attempts to load go_ai_model.zip or go_bc_policy.zip from the ml folder. If you have not trained a model yet, the AI will not have a policy loaded and will effectively play random or pass.

3. Playing the Game:

* Left-click on the board intersections to place stones.
* Use the "Pass" button if you have no move.
* Use the "End Game" button to calculate the score and save the recorded game as demonstrations (demos.npz in ml/data).
* Use "Restart" to start a new game.

## Training the AI
1. PPO Training from Scratch

Use train.py to train a PPO model without demonstrations:

<pre>```bash cd ml
python train.py```</pre>
This will interact with the environment (self-play) and train go_ai_model.zip.

2. Collecting Demonstrations
Play a game via the GUI (python main.py) and end the game. This saves (state, action) pairs as demos.npz in ml/data. These demonstrations can then be used for imitation learning.

3. Imitation Learning with imitation_train.py
After collecting demonstrations:

<pre>```bash cd ml
python imitation_train.py```</pre>

This will load data/demos.npz, perform Behavior Cloning (BC), and save go_bc_policy

4. Fine-Tuning with PPO (ppo_finetune.py)
Now that you have a BC-trained policy, you can further improve it with PPO:

<pre>```bash cd ml
python ppo_finetune.py```</pre>

This loads go_bc_policy into a PPO model, improves it, and saves go_ai_model.zip.

## Using the Trained Model in the GUI
Once you have go_ai_model.zip (or go_bc_policy.zip):

* Ensure it is located in ml directory.
* Run python main.py from the go_game directory.
* The GUI will load the model, and the AI will play according to the trained policy.


## Troubleshooting
* If the AI model is not found, ensure you run main.py from go_game directory.
* Check that go_ai_model.zip or go_bc_policy.zip exists in ml.
* If paths are incorrect, print os.getcwd() and adjust your paths or your working directory accordingly.

## Further Improvements
* Expand the rule checks in rules.py.
* Implement a more sophisticated scoring and territory calculation.
* Increase the board size to 13x13 or 19x19 (may require adjusting timesteps for training).
* Integrate GAIL or other IL algorithms to improve from human-like play.