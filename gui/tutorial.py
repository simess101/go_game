class Tutorial:
    def __init__(self, gui):
        self.gui = gui
        self.steps = [
            "Welcome to Go! Let's learn the basics.",
            "This is the board. Black moves first.",
            "Try placing your first stone on the board."
        ]
        self.current_step = 0

    def next_step(self):
        if self.current_step < len(self.steps):
            print(self.steps[self.current_step])
            self.current_step += 1
        else:
            print("Tutorial complete!")
