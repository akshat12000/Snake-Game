import turtle

class Snake:
    def __init__(self, x=0, y=0):
        self.MOVE_DISTANCE = 20
        self.direction = "east"
        self.body = []
        
        # Create snake head
        self.head = turtle.Turtle()
        self.head.shape("square")
        self.head.color("green")
        self.head.penup()
        self.head.goto(x, y)
    
    def move(self):
        """Move the snake in the current direction"""
        if self.direction == "east":
            x = self.head.xcor()
            self.head.setx(x + self.MOVE_DISTANCE)
        elif self.direction == "west":
            x = self.head.xcor()
            self.head.setx(x - self.MOVE_DISTANCE)
        elif self.direction == "north":
            y = self.head.ycor()
            self.head.sety(y + self.MOVE_DISTANCE)
        elif self.direction == "south":
            y = self.head.ycor()
            self.head.sety(y - self.MOVE_DISTANCE)

    def get_position(self):
        """Get the current position of the snake's head"""
        return self.head.xcor(), self.head.ycor()

    def change_direction(self, new_direction):
        """Change the snake's direction if not reversing"""
        opposite_directions = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east"
        }
        if new_direction != opposite_directions.get(self.direction):
            self.direction = new_direction

    def add_segment(self):
        """Add a new segment to the snake's body"""
        new_segment = turtle.Turtle()
        new_segment.shape("square")
        new_segment.color("lightgreen")
        new_segment.penup()
        if self.body:
            last_segment = self.body[-1]
            new_segment.goto(last_segment.xcor(), last_segment.ycor())
        else:
            new_segment.goto(self.head.xcor(), self.head.ycor())
        self.body.append(new_segment)
    
    def move_body(self, head_x, head_y):
        """Move the body segments to follow the head"""
        for index in range(len(self.body)-1, 0, -1):
            x = self.body[index-1].xcor()
            y = self.body[index-1].ycor()
            self.body[index].goto(x, y)

        if len(self.body) > 0:
            self.body[0].goto(head_x, head_y)