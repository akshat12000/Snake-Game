import time
import tkinter as tk
from tkinter import messagebox, simpledialog
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
        self.is_paused = False
        self.player_name = ""
        
        # Initialize game objects
        self.snake = None
        self.food = None
        self.display = None
        self.score_manager = None
        self.sound_manager = None
        
        # Update system (separate from game)
        self.update_checker = UpdateChecker()
    
    def reset_game_state(self):
        """Reset all game state for a fresh start"""
        self.score = 0
        self.is_paused = False
        
        # Clean up previous game objects more carefully
        if self.display and hasattr(self.display, 'window') and self.display.window:
            try:
                # Clear the screen instead of closing it
                self.display.window.clear()
                # Hide any remaining turtles
                for turtle_obj in self.display.window.turtles():
                    turtle_obj.hideturtle()
                    turtle_obj.clear()
            except:
                try:
                    self.display.window.bye()
                except:
                    pass
        
        if self.sound_manager:
            try:
                self.sound_manager.cleanup()
            except:
                pass
        
        # Reset game objects to None
        self.snake = None
        self.food = None
        self.display = None
        self.score_manager = None
        self.sound_manager = None
    
    def show_main_menu(self):
        """Show main menu with Play Game and Check Updates options"""
        root = tk.Tk()
        root.title("Snake Game")
        root.geometry("350x400")  # Made taller to fit instructions
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
        
        # Add instructions for new features
        instructions_frame = tk.Frame(menu_frame)
        instructions_frame.pack(pady=(20, 0))
        
        instructions_label = tk.Label(instructions_frame, text="New Features:", 
                                    font=("Arial", 10, "bold"), fg="blue")
        instructions_label.pack()
        
        feature1_label = tk.Label(instructions_frame, text="• Enter your name before playing", 
                                font=("Arial", 8), fg="gray")
        feature1_label.pack()
        
        feature2_label = tk.Label(instructions_frame, text="• Press SPACE to pause/resume game", 
                                font=("Arial", 8), fg="gray")
        feature2_label.pack()
        
        feature3_label = tk.Label(instructions_frame, text="• Special scoring for Pramita (+2 points)", 
                                font=("Arial", 8), fg="gray")
        feature3_label.pack()
        
        root.mainloop()
        
        # Safely destroy the window
        try:
            root.destroy()
        except tk.TclError:
            # Window was already destroyed
            pass
    
    def start_game(self, menu_window):
        """Start the actual game after getting player name"""
        menu_window.destroy()
        
        # Reset game state for a fresh start
        self.reset_game_state()
        
        # Add a small delay to ensure cleanup is complete
        import time
        time.sleep(0.1)
        
        self.get_player_name()
        
        try:
            self.run_game()
        except Exception as e:
            print(f"Error during game: {e}")
            import traceback
            traceback.print_exc()
            
        # After game ends, show main menu again
        self.show_main_menu()
    
    def get_player_name(self):
        """Get player name before starting the game"""
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        name = simpledialog.askstring(
            "Player Name", 
            "Enter your name:",
            parent=root
        )
        
        if name and name.strip():
            self.player_name = name.strip()
        else:
            self.player_name = "Anonymous"
        
        root.destroy()
        print(f"Welcome, {self.player_name}!")
    
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
    
    def toggle_pause(self):
        """Toggle game pause state"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            print("Game Paused! Press SPACE to resume.")
            self.display.show_pause_message()
        else:
            print("Game Resumed!")
            self.display.hide_pause_message()

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
            
            # Special scoring for Pramita (case insensitive)
            if self.player_name.lower() == "pramita":
                self.score += 2
                print(f"Special scoring for {self.player_name}! +2 points")
            else:
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
            if not self.is_paused:
                head_x, head_y = self.snake.get_position()

                self.snake.move()
                self.snake.move_body(head_x, head_y)

                if self.check_collisions():
                    break

            time.sleep(self.GAME_SPEED)
            self.display.update()

    def run_game(self):
        """Set up and run the game"""
        print("🐍 Starting game setup...")

        # Set up display, snake, and food
        print("Creating display...")
        self.display = GameDisplay()
        self.display.setup_screen()
        
        print("Creating snake...")
        self.snake = Snake()
        print("Creating food...")
        self.food = Food()
        print("Creating score manager...")
        self.score_manager = ScoreManager()
        print("Creating sound manager...")
        self.sound_manager = SoundManager()

        # Create score display
        print("Setting up UI...")
        self.display.create_score_display()
        self.display.create_high_score_display()
        self.display.update_score(self.score) # Initial score display
        self.display.update_high_score_display(self.score_manager.get_high_score()) # Initial high score display

        # Set up controls
        print("Setting up controls...")
        self.display.setup_controls(self.go_up, self.go_down, self.go_left, self.go_right, self.toggle_pause)
        
        print("Starting game loop...")
        # Start the game loop
        self.game_loop()

        is_new_record = self.score_manager.save_high_score(self.score)

        # Add this celebration sound for new records!
        if is_new_record:
            self.sound_manager.play_new_record_sound()

        # Show beautiful game over screen
        self.display.show_game_over(self.score, self.score_manager.get_high_score(), is_new_record)

        # Cleanup sound system
        if self.sound_manager:
            self.sound_manager.cleanup()
        
        # Cleanup display properly
        if self.display and hasattr(self.display, 'window') and self.display.window:
            try:
                # The window will be closed by exitonclick in show_game_over
                pass
            except:
                pass

if __name__ == "__main__":
    game = SnakeGame()
    game.show_main_menu()
