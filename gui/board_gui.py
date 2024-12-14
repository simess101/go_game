import tkinter as tk
import numpy as np
import os
from game.board import Board
from ml.model import GoAIModel
from ml.go_env import GoEnv

class GoGameGUI:
    def __init__(self, board_size=9):
        self.board_size = board_size
        self.board = Board(board_size)
        self.cell_size = 450 // (board_size - 1)
        self.margin = self.cell_size // 2

        # Paths to the model and data files
        # Since board_gui.py is in gui/ and files are in ml/, we go up one directory (..) and into ml/
        self.model_path = "../go_game/ml/go_ai_model"
        self.bc_policy_path = "../ml/go_bc_policy"
        self.demos_path = "../ml/data/demos.npz"

        # Initialize the Go environment and AI
        self.env = GoEnv(board_size)
        self.ai = GoAIModel(self.env, board_size)

        # Debug prints for paths
        print("Current working directory:", os.getcwd())
        print("Attempting to load model from:", os.path.abspath(self.model_path + ".zip"))

        # Load the model
        if os.path.exists(self.model_path + ".zip"):
            print("Found go_ai_model.zip, loading...")
            self.ai.load(self.model_path)
        elif os.path.exists(self.bc_policy_path + ".zip"):
            print("Found go_bc_policy.zip, loading...")
            self.ai.load(self.bc_policy_path)
        else:
            print("No trained model found. Ensure that go_ai_model.zip or go_bc_policy.zip exists in the ml folder.")

        # Initialize the GUI
        self.window = tk.Tk()
        self.window.title("Go Game")
        self.canvas = tk.Canvas(
            self.window,
            width=450 + self.cell_size,
            height=450 + self.cell_size,
            bg="tan",
        )
        self.canvas.pack()
        self.draw_grid()
        self.canvas.bind("<Button-1>", self.handle_click)

        # Add turn indicator
        self.turn_label = tk.Label(self.window, text="", font=("Helvetica", 14))
        self.turn_label.pack(anchor="ne")
        self.update_turn_indicator()

        # Add a pass button for the player
        pass_button = tk.Button(self.window, text="Pass", command=self.player_pass)
        pass_button.pack()

        # Add a restart button for the game
        restart_button = tk.Button(self.window, text="Restart", command=self.restart_game)
        restart_button.pack()

        # Track consecutive passes
        self.consecutive_passes = 0

        # Add end game button
        end_button = tk.Button(self.window, text="End Game", command=self.end_game)
        end_button.pack()

        # Track game statistics
        self.ai_wins = 0
        self.player_wins = 0

        # Ensure the data directory exists
        demos_dir = os.path.dirname(self.demos_path)
        if not os.path.exists(demos_dir):
            os.makedirs(demos_dir)

        # Lists to store states and actions for demonstrations
        self.recorded_states = []
        self.recorded_actions = []

    def draw_grid(self):
        for i in range(self.board_size):
            # Draw vertical lines
            self.canvas.create_line(
                self.margin + i * self.cell_size,
                self.margin,
                self.margin + i * self.cell_size,
                450 + self.margin,
                fill="black",
            )
            # Draw horizontal lines
            self.canvas.create_line(
                self.margin,
                self.margin + i * self.cell_size,
                450 + self.margin,
                self.margin + i * self.cell_size,
                fill="black",
            )

        # Draw the right and bottom border lines explicitly
        self.canvas.create_line(
            self.margin + (self.board_size - 1) * self.cell_size,
            self.margin,
            self.margin + (self.board_size - 1) * self.cell_size,
            450 + self.margin,
            fill="black",
        )
        self.canvas.create_line(
            self.margin,
            self.margin + (self.board_size - 1) * self.cell_size,
            450 + self.margin,
            self.margin + (self.board_size - 1) * self.cell_size,
            fill="black",
        )

    def handle_click(self, event):
        x = round((event.x - self.margin) / self.cell_size)
        y = round((event.y - self.margin) / self.cell_size)

        print(f"Player clicked at ({x}, {y}). Current player: {'Black' if self.board.current_player == 1 else 'White'}")

        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            current_state = self.board.get_board_state().copy()
            chosen_action = x * self.board_size + y

            if self.board.place_stone(x, y):  # Only proceed if player's move is valid
                print(f"Player placed a stone at ({x}, {y}).")

                # Record the demonstration (state before placing and the chosen action)
                self.recorded_states.append(current_state)
                self.recorded_actions.append(chosen_action)

                self.draw_stones()
                self.update_turn_indicator()
                self.consecutive_passes = 0  # Reset consecutive passes

                # AI's move
                self.make_ai_move()
            else:
                print(f"Invalid move by Player at ({x}, {y}). Stone not placed.")

    def player_pass(self):
        print("Player passed their turn.")
        self.consecutive_passes += 1
        self.update_turn_indicator()

        # Check if both players passed
        if self.consecutive_passes >= 2:
            self.end_game()
            return

        # AI's move
        self.make_ai_move()

    def make_ai_move(self):
        print(f"AI's turn. Current player: {'Black' if self.board.current_player == 1 else 'White'}")
        current_state = self.board.get_board_state().copy()
        action = self.ai.predict(current_state)  # Get AI's action

        if action is None:  # AI decides to pass
            print("AI passed its turn.")
            self.consecutive_passes += 1
            self.board.current_player = 1  # Switch back to Black
            self.update_turn_indicator()
        else:
            ai_x, ai_y = divmod(action, self.board_size)
            if self.board.place_stone(ai_x, ai_y):  # Ensure AI's move is valid
                print(f"AI placed a stone at ({ai_x}, {ai_y}).")

                # Record the demonstration for AI move
                self.recorded_states.append(current_state)
                self.recorded_actions.append(action)

                self.draw_stones()
                self.update_turn_indicator()
                self.consecutive_passes = 0
            else:
                print(f"AI tried an invalid move at ({ai_x}, {ai_y}). Passing turn.")
                self.consecutive_passes += 1
                self.board.current_player = 1
                self.update_turn_indicator()

        # Check if both players passed
        if self.consecutive_passes >= 2:
            self.end_game()

    def restart_game(self):
        print("Game restarted.")
        self.board.reset_board()
        self.consecutive_passes = 0
        self.board.current_player = 1
        self.canvas.delete("stones")  # Clear stones
        self.draw_grid()
        self.update_turn_indicator()
        # Clear recorded states and actions for a fresh game
        self.recorded_states = []
        self.recorded_actions = []

    def draw_stones(self):
        self.canvas.delete("stones")
        for x in range(self.board_size):
            for y in range(self.board_size):
                if self.board.board[y][x] == 1:  # Black stone
                    self.canvas.create_oval(
                        self.margin + x * self.cell_size - 15,
                        self.margin + y * self.cell_size - 15,
                        self.margin + x * self.cell_size + 15,
                        self.margin + y * self.cell_size + 15,
                        fill="black",
                        tags="stones",
                    )
                elif self.board.board[y][x] == 2:  # White stone
                    self.canvas.create_oval(
                        self.margin + x * self.cell_size - 15,
                        self.margin + y * self.cell_size - 15,
                        self.margin + x * self.cell_size + 15,
                        self.margin + y * self.cell_size + 15,
                        fill="white",
                        outline="black",
                        tags="stones",
                    )

    def update_turn_indicator(self):
        if self.board.current_player == 1:
            self.turn_label.config(text="Turn: Black (Place Black Stone)", fg="black")
            print("It's Black's turn.")
        else:
            self.turn_label.config(text="Turn: White (Place White Stone)", fg="white")
            print("It's White's turn.")

    def end_game(self):
        black_score, white_score = self.board.calculate_score()
        winner = "Black" if black_score > white_score else "White"

        if winner == "Black":
            self.player_wins += 1
        else:
            self.ai_wins += 1

        print(f"Game Over! Black: {black_score}, White: {white_score}. Winner: {winner}")
        print(f"Player Wins: {self.player_wins}, AI Wins: {self.ai_wins}")
        print(f"Captured by AI: {self.board.captured_white}, Captured by Player: {self.board.captured_black}")

        message = f"Game Over!\nBlack: {black_score}\nWhite: {white_score}\nWinner: {winner}"
        self.canvas.create_text(
            225 + self.margin,
            225 + self.margin,
            text=message,
            fill="red",
            font=("Helvetica", 16),
            tags="stones",
        )

        # Save demonstrations to ../ml/data/demos.npz
        if self.recorded_states and self.recorded_actions:
            np.savez(self.demos_path, states=np.array(self.recorded_states), actions=np.array(self.recorded_actions))
            print(f"Demonstrations saved to {self.demos_path}")

    def run(self):
        self.window.mainloop()


# Run the GUI (for testing purposes)
if __name__ == "__main__":
    gui = GoGameGUI(board_size=9)
    gui.run()
