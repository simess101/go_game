import tkinter as tk
from game.board import Board
from ml.model import GoAIModel
from ml.go_env import GoEnv


class GoGameGUI:
    def __init__(self, board_size=9):
        self.board_size = board_size
        self.board = Board(board_size)
        self.cell_size = 450 // (board_size - 1)
        self.margin = self.cell_size // 2

        # Initialize the Go environment and AI
        self.env = GoEnv(board_size)
        self.ai = GoAIModel(self.env, board_size)  # Pass board_size to the model
        self.ai.load("go_ai_model")  # Load the trained model

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

    def draw_grid(self):
        """Draw the board grid with a margin for border stones."""
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
        """Handle user clicks to place stones."""
        x = round((event.x - self.margin) / self.cell_size)
        y = round((event.y - self.margin) / self.cell_size)

        print(f"Player clicked at ({x}, {y}). Current player: {'Black' if self.board.current_player == 1 else 'White'}")

        # Player's move
        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            if self.board.place_stone(x, y):  # Only proceed if the player's move is valid
                print(f"Player placed a stone at ({x}, {y}).")
                self.draw_stones()
                self.update_turn_indicator()
                self.consecutive_passes = 0  # Reset consecutive passes

                # AI's move
                self.make_ai_move()
            else:
                print(f"Invalid move by Player at ({x}, {y}). Stone not placed.")

    def player_pass(self):
        """Handle the player passing their turn."""
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
        """Handle AI's turn."""
        print(f"AI's turn. Current player: {'Black' if self.board.current_player == 1 else 'White'}")
        state = self.board.get_board_state()
        action = self.ai.predict(state)  # Get AI's action

        if action is None:  # AI decides to pass
            print("AI passed its turn.")
            self.consecutive_passes += 1
            self.board.current_player = 1  # Switch back to Black's turn
            self.update_turn_indicator()
        else:
            ai_x, ai_y = divmod(action, self.board_size)
            if self.board.place_stone(ai_x, ai_y):  # Ensure the AI's move is valid
                print(f"AI placed a stone at ({ai_x}, {ai_y}).")
                self.draw_stones()
                self.update_turn_indicator()
                self.consecutive_passes = 0  # Reset consecutive passes
            else:
                print(f"AI tried to place an invalid stone at ({ai_x}, {ai_y}). Passing turn.")
                self.consecutive_passes += 1
                self.board.current_player = 1  # Switch back to Black's turn
                self.update_turn_indicator()

        # Check if both players passed
        if self.consecutive_passes >= 2:
            self.end_game()

    def restart_game(self):
        """Restart the game by resetting the board and variables."""
        print("Game restarted.")
        self.board.reset_board()
        self.consecutive_passes = 0
        self.board.current_player = 1  # Reset to Black's turn
        self.canvas.delete("stones")  # Clear all stones from the board
        self.draw_grid()  # Redraw the grid
        self.update_turn_indicator()

    def draw_stones(self):
        """Render stones on the intersections of the grid."""
        self.canvas.delete("stones")  # Clear old stones
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
                        outline="black",  # Add border for better visibility
                        tags="stones",
                    )

    def update_turn_indicator(self):
        """Update the turn indicator and print the current player's turn."""
        if self.board.current_player == 1:
            self.turn_label.config(text="Turn: Black (Place Black Stone)", fg="black")
            print("It's Black's turn.")
        else:
            self.turn_label.config(text="Turn: White (Place White Stone)", fg="white")
            print("It's White's turn.")

    def end_game(self):
        """Calculate and display the final scores."""
        black_score, white_score = self.board.calculate_score()
        winner = "Black" if black_score > white_score else "White"

        # Track wins for AI and player
        if winner == "Black":
            self.player_wins += 1
        else:
            self.ai_wins += 1

        print(f"Game Over! Black: {black_score}, White: {white_score}. Winner: {winner}")
        print(f"Player Wins: {self.player_wins}, AI Wins: {self.ai_wins}")
        print(f"Captured by AI: {self.board.captured_white}, Captured by Player: {self.board.captured_black}")

        # Display the results on the board
        message = f"Game Over!\nBlack: {black_score}\nWhite: {white_score}\nWinner: {winner}"
        self.canvas.create_text(
            225 + self.margin,
            225 + self.margin,
            text=message,
            fill="red",
            font=("Helvetica", 16),
            tags="stones",
        )

    def run(self):
        """Run the main Tkinter event loop."""
        self.window.mainloop()


# Run the GUI (for testing purposes)
if __name__ == "__main__":
    gui = GoGameGUI(board_size=9)
    gui.run()
