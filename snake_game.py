import time
import tkinter as tk
from tkinter import messagebox
from score_manager import ScoreManager
from snake import Snake
from food import Food
from game_display import GameDisplay
from sound_manager import SoundManager
from update_system import UpdateChecker

class SnakeGame:
    def __init__(self):
         # Initialize constants
        self.GAME_SPEED = 0.1
        self.BOUNDARY = 290
        
        # Initialize game state
        self.score = 0
        
        # Initialize game objects
        self.snake = None
        self.food = None
        self.display = None
        self.score_manager = None
        self.sound_manager = None
        
        # Update system (separate from game)
        self.update_checker = UpdateChecker()
    
    def show_main_menu(self):
        """Show main menu with Play Game and Check Updates options"""
        root = tk.Tk()
        root.title("Snake Game")
        root.geometry("350x300")  # Made taller to fit all buttons
        root.resizable(False, False)
        
        # Center the window
        root.eval('tk::PlaceWindow . center')
        
        menu_frame = tk.Frame(root, padx=30, pady=30)
        menu_frame.pack(expand=True, fill='both')
        
        title_label = tk.Label(menu_frame, text="🐍 Snake Game", font=("Arial", 20, "bold"))
        title_label.pack(pady=(0, 30))
        
        play_button = tk.Button(menu_frame, text="Play Game", font=("Arial", 12), 
                               width=18, height=2, command=lambda: self.start_game(root))
        play_button.pack(pady=8)
        
        update_button = tk.Button(menu_frame, text="Check for Updates", font=("Arial", 12),
                                 width=18, height=2, command=self.check_updates)
        update_button.pack(pady=8)
        
        quit_button = tk.Button(menu_frame, text="Quit", font=("Arial", 12),
                               width=18, height=2, command=root.quit)
        quit_button.pack(pady=8)
        
        root.mainloop()
        
        # Safely destroy the window
        try:
            root.destroy()
        except tk.TclError:
            # Window was already destroyed
            pass
    
    def start_game(self, menu_window):
        """Start the actual game"""
        menu_window.destroy()
        self.run_game()
        # After game ends, show main menu again
        self.show_main_menu()
    
    def check_updates(self):
        """Check for updates (separate from game logic)"""
        self.update_checker.check_and_prompt_for_updates()

    def go_up(self):
        """Change snake direction to up"""
        self.snake.change_direction("north")
    
    def go_down(self):
        """Change snake direction to down"""
        self.snake.change_direction("south")
    
    def go_left(self):
        """Change snake direction to left"""
        self.snake.change_direction("west")
    
    def go_right(self):
        """Change snake direction to right"""
        self.snake.change_direction("east")

    def check_collisions(self):
        """Check for collisions with boundaries and food"""
        # Check boundary collision
        if self.snake.get_position()[0] > self.BOUNDARY or self.snake.get_position()[0] < -self.BOUNDARY or self.snake.get_position()[1] > self.BOUNDARY or self.snake.get_position()[1] < -self.BOUNDARY:
            print("Game Over!")
            self.sound_manager.play_game_over_sound()
            return True
        
        # Check self-collision
        if self.snake.check_self_collision():
            print("Game Over! You ran into yourself.")
            self.sound_manager.play_game_over_sound()
            return True

        # Check food collision
        if self.snake.head.distance(self.food.get_food()) < 20:
            print("Yum! Food eaten.")
            self.sound_manager.play_eat_sound()
            self.score += 1
            self.display.update_score(self.score)
            self.snake.add_segment()
            self.food.relocate(self.BOUNDARY)
            self.update_game_speed()

        return False
    
    def update_game_speed(self):
        """Increase speed based on score"""
        # Start at 0.1, get 10% faster every 5 points
        self.GAME_SPEED = max(0.03, 0.1 - (self.score // 5) * 0.01)

    def game_loop(self):
        """Main game loop"""
        while True:
            head_x, head_y = self.snake.get_position()

            self.snake.move()
            self.snake.move_body(head_x, head_y)

            if self.check_collisions():
                break

            time.sleep(self.GAME_SPEED)
            self.display.update()

    def run_game(self):
        """Set up and run the game"""

        # Set up display, snake, and food
        self.display = GameDisplay()
        self.display.setup_screen()
        
        self.snake = Snake()
        self.food = Food()
        self.score_manager = ScoreManager()
        self.sound_manager = SoundManager()

        # Create score display
        self.display.create_score_display()
        self.display.create_high_score_display()
        self.display.update_score(self.score) # Initial score display
        self.display.update_high_score_display(self.score_manager.get_high_score()) # Initial high score display

        # Set up controls
        self.display.setup_controls(self.go_up, self.go_down, self.go_left, self.go_right)
        
        # Start the game loop
        self.game_loop()

        is_new_record = self.score_manager.save_high_score(self.score)

        # Add this celebration sound for new records!
        if is_new_record:
            self.sound_manager.play_new_record_sound()

        # Show beautiful game over screen
        self.display.show_game_over(self.score, self.score_manager.get_high_score(), is_new_record)

        # Cleanup sound system
        self.sound_manager.cleanup()

if __name__ == "__main__":
    game = SnakeGame()
    game.show_main_menu()
