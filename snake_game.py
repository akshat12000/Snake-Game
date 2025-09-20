import time
import threading
from score_manager import ScoreManager
from snake import Snake
from food import Food
from game_display import GameDisplay
from sound_manager import SoundManager

# Auto-update system imports with fallbacks
try:
    from version_manager import VersionManager
    from simple_update_checker import SimpleUpdateChecker
    UPDATE_SYSTEM_AVAILABLE = True
except ImportError:
    print("Update system not available - running without auto-updates")
    VersionManager = None
    SimpleUpdateChecker = None
    UPDATE_SYSTEM_AVAILABLE = False

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
        self.sound_manager = SoundManager()
        
        # Initialize update system
        self.version_manager = VersionManager() if VersionManager else None
        self.update_checker = SimpleUpdateChecker() if SimpleUpdateChecker else None
        
        # Check for updates in background after game starts
        if UPDATE_SYSTEM_AVAILABLE and self.update_checker:
            self.schedule_update_check()
        self.score_manager = None
        self.sound_manager = None

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

    def schedule_update_check(self):
        """Schedule background update check after game starts"""
        if self.update_checker:
            self.update_checker.background_update_check()
    
    def manual_update_check(self):
        """Allow user to manually check for updates"""
        if not UPDATE_SYSTEM_AVAILABLE:
            print("Update system not available")
            return
        
        if self.update_checker:
            self.update_checker.manual_update_check()
        else:
            print("❌ Update checker not initialized")

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
        
        # Add manual update check (F5 key)
        if UPDATE_SYSTEM_AVAILABLE:
            self.display.window.onkey(self.manual_update_check, "F5")
        
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

# Game version info display
def show_version_info():
    """Display version information at startup"""
    if UPDATE_SYSTEM_AVAILABLE and VersionManager:
        vm = VersionManager()
        version_info = vm.get_full_version_info()
        print(f"\n🐍 Snake Game v{version_info['version']} (Build {version_info['build']})")
        print(f"📅 Release: {version_info['release_date']}")
        print("🎮 Press F5 during gameplay to check for updates\n")
    else:
        print("\n🐍 Snake Game v1.0.0")
        print("🎮 Classic Snake Game with Professional Features\n")

if __name__ == "__main__":
    show_version_info()
    
    # Create and run game
    game = SnakeGame()
    game.run_game()
