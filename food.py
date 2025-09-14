import turtle
import random

class Food:
    def __init__(self):
        self.food = turtle.Turtle()
        self.food.shape("circle")
        self.food.color("red")
        self.food.penup()
        self.food.goto(100, 100)  # Start position

    def get_food(self):
        """Return the food turtle object"""
        return self.food
    
    def relocate(self, boundary):
        """Relocate food to a random position within the boundary"""
        x = random.randint(-boundary, boundary)
        y = random.randint(-boundary, boundary)
        self.food.goto(x, y)
    
    def get_position(self):
        """Get the current position of the food"""
        return self.food.xcor(), self.food.ycor()