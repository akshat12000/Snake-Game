import turtle
import time
from snake import Snake
from food import Food
from game_display import GameDisplay

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
        if self.snake.get_position()[0] > self.BOUNDARY or self.snake.get_position()[0] < -self.BOUNDARY or self.snake.get_position()[1] > self.BOUNDARY or self.snake.get_position()[1] < -self.BOUNDARY:
            print("Game Over!")
            return True

        if self.snake.head.distance(self.food.get_food()) < 20:
            print("Yum! Food eaten.")
            self.score += 1
            self.display.update_score(self.score)
            self.snake.add_segment()
            self.food.relocate(self.BOUNDARY)

        return False

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

        # Create score display
        self.display.create_score_display()
        self.display.update_score(self.score) # Initial score display
        
        # Set up controls
        self.display.setup_controls(self.go_up, self.go_down, self.go_left, self.go_right)
        
        # Start the game loop
        self.game_loop()

        # Show beautiful game over screen
        self.display.show_game_over(self.score)

if __name__ == "__main__":
    game = SnakeGame()
    game.run_game()
