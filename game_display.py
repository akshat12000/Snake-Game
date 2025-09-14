import turtle
from score_manager import ScoreManager

class GameDisplay:
    def __init__(self, width=600, height=600):
        self.WINDOW_WIDTH = width
        self.WINDOW_HEIGHT = height
        self.window = None
        self.score_display = None
        
    def setup_screen(self):
        """Create and configure the game window"""
        self.window = turtle.Screen()
        self.window.title("Snake Game")
        self.window.bgcolor("white")
        self.window.setup(width=self.WINDOW_WIDTH, height=self.WINDOW_HEIGHT)
        self.window.tracer(0)
        return self.window
    
    def get_height(self):
        """Return the window height"""
        return self.WINDOW_HEIGHT

    def get_width(self):
        """Return the window width"""
        return self.WINDOW_WIDTH
    
    def create_score_display(self):
        """Create a score display turtle"""
        self.score_display = turtle.Turtle()
        self.score_display.hideturtle()
        self.score_display.penup()
        self.score_display.color("black")
        self.score_display.goto(-280, 260)
        
    def update_score(self, score):
        """Update the score display"""
        if self.score_display:
            self.score_display.clear()
            self.score_display.write(f"Score: {score}", font=("Arial", 14, "normal"))
    
    def create_high_score_display(self):
        """Create a high score display turtle"""
        self.high_score_display = turtle.Turtle()
        self.high_score_display.hideturtle()
        self.high_score_display.penup()
        self.high_score_display.color("gray")
        self.high_score_display.goto(-280, 230)

    def update_high_score_display(self, high_score):
        """Update the high score display"""
        if hasattr(self, 'high_score_display'):
            self.high_score_display.clear()
            self.high_score_display.write(f"High Score: {high_score}", font=("Arial", 12, "normal"))

    def show_game_over(self, final_score, high_score, is_new_record):
        """Display game over message on the game screen"""
        # Game over title
        game_over_display = turtle.Turtle()
        game_over_display.hideturtle()
        game_over_display.penup()
        game_over_display.color("red")
        game_over_display.goto(0, 100)  # Higher position
        game_over_display.write("GAME OVER!", align="center", font=("Arial", 24, "bold"))

        # New high score celebration (if applicable)
        if is_new_record:
            new_record_display = turtle.Turtle()
            new_record_display.hideturtle()
            new_record_display.penup()
            new_record_display.color("gold")
            new_record_display.goto(0, 60)  # Below game over title
            new_record_display.write("🏆 NEW HIGH SCORE! 🏆", align="center", font=("Arial", 16, "bold"))
            
            # Final score (for new record)
            score_display = turtle.Turtle()
            score_display.hideturtle()
            score_display.penup()
            score_display.color("black")
            score_display.goto(0, 20)  # Below celebration
            score_display.write(f"New Record: {final_score}", align="center", font=("Arial", 18, "bold"))
            
        else:
            # Final score (normal)
            score_display = turtle.Turtle()
            score_display.hideturtle()
            score_display.penup()
            score_display.color("black")
            score_display.goto(0, 40)  # Below game over
            score_display.write(f"Final Score: {final_score}", align="center", font=("Arial", 16, "normal"))
            
            # High score display (only if not new record)
            high_score_display = turtle.Turtle()
            high_score_display.hideturtle()
            high_score_display.penup()
            high_score_display.color("blue")
            high_score_display.goto(0, 10)  # Below final score
            high_score_display.write(f"High Score: {high_score}", align="center", font=("Arial", 14, "normal"))
        
        # Instructions
        instruction_display = turtle.Turtle()
        instruction_display.hideturtle()
        instruction_display.penup()
        instruction_display.color("gray")
        instruction_display.goto(0, -40)  # Bottom
        instruction_display.write("Click anywhere to exit", align="center", font=("Arial", 12, "normal"))
        
        self.window.update()
        self.window.exitonclick()
    
    def setup_controls(self, up_func, down_func, left_func, right_func):
        """Set up keyboard controls"""
        self.window.listen()
        self.window.onkey(up_func, "Up")
        self.window.onkey(down_func, "Down")
        self.window.onkey(left_func, "Left")
        self.window.onkey(right_func, "Right")
    
    def update(self):
        """Update the display"""
        self.window.update()