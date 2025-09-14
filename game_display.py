import turtle

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
    
    def show_game_over(self, final_score):
        """Display game over message on the game screen"""
        # Game over title
        game_over_display = turtle.Turtle()
        game_over_display.hideturtle()
        game_over_display.penup()
        game_over_display.color("red")
        game_over_display.goto(0, 50)
        game_over_display.write("GAME OVER!", align="center", font=("Arial", 24, "bold"))
        
        # Final score
        score_display = turtle.Turtle()
        score_display.hideturtle()
        score_display.penup()
        score_display.color("black")
        score_display.goto(0, 0)
        score_display.write(f"Final Score: {final_score}", align="center", font=("Arial", 16, "normal"))
        
        # Instructions
        instruction_display = turtle.Turtle()
        instruction_display.hideturtle()
        instruction_display.penup()
        instruction_display.color("gray")
        instruction_display.goto(0, -50)
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