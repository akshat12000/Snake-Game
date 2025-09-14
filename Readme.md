# 🐍 Snake Game

A classic Snake game implementation built with Python and Turtle graphics, featuring clean object-oriented architecture and professional code organization.

## 🎮 Game Features

- **Smooth snake movement** with arrow key controls
- **Dynamic food system** with random positioning
- **Live score tracking** displayed on screen
- **Collision detection** for boundaries and food
- **Growing snake mechanics** - snake extends when eating food
- **Professional UI** with game over screen and clean exit
- **Responsive controls** with anti-reverse logic

## 🏗️ Architecture

This project demonstrates **professional software architecture** with clean separation of concerns:

```
📁 SimpleGame/
├── 🐍 snake.py          → Snake behavior & movement logic
├── 🍎 food.py           → Food positioning & management  
├── 🖼️ game_display.py   → UI, graphics, and display handling
├── 🎮 snake_game.py     → Main game logic & coordination
└── 📚 README.md         → Project documentation
```

### Design Principles Applied
- **Single Responsibility Principle** - Each class has one clear purpose
- **Encapsulation** - Internal state properly managed and hidden
- **Composition** - Game coordinates separate components
- **Clean Code** - Readable, maintainable, well-documented code

## 🚀 Getting Started

### Prerequisites
- Python 3.6 or higher
- Turtle graphics (included with Python)

### Installation
1. Clone or download this repository
2. Navigate to the SimpleGame directory
3. Run the game:

```bash
python snake_game.py
```

### Controls
- **↑ Arrow Key** - Move Up
- **↓ Arrow Key** - Move Down  
- **← Arrow Key** - Move Left
- **→ Arrow Key** - Move Right
- **Click** - Close game over screen

## 🎯 How to Play

1. **Start the game** - Run `python snake_game.py`
2. **Control the snake** - Use arrow keys to navigate
3. **Eat the food** - Guide the green snake to the red food
4. **Grow your snake** - Each food item makes the snake longer
5. **Avoid boundaries** - Don't hit the walls!
6. **Beat your score** - Try to eat as much food as possible

## 🏆 Game Rules

- Snake moves continuously in the current direction
- Eating food increases score by 1 and adds a body segment
- Game ends when snake hits the boundary walls
- Snake cannot reverse direction (prevents accidental self-collision)

## 🔧 Technical Implementation

### Snake Class (`snake.py`)
- Manages snake head and body segments
- Handles movement and direction changes
- Implements growth mechanics
- Anti-reverse direction validation

### Food Class (`food.py`)
- Creates and positions food items
- Random relocation within boundaries
- Clean interface for game interaction

### GameDisplay Class (`game_display.py`)
- Screen setup and configuration
- Live score display
- Game over screen with final score
- Keyboard input handling

### SnakeGame Class (`snake_game.py`)
- Coordinates all game components
- Main game loop implementation
- Collision detection logic
- Game state management

## 🎨 Customization

The modular architecture makes customization easy:

### Modify Game Speed
```python
# In snake_game.py - __init__ method
self.GAME_SPEED = 0.05  # Faster game (lower = faster)
```

### Change Colors
```python
# In snake.py - __init__ method
self.head.color("blue")  # Change snake color

# In food.py - __init__ method  
self.food.color("yellow")  # Change food color
```

### Adjust Game Area
```python
# In snake_game.py - __init__ method
self.BOUNDARY = 200  # Smaller game area
```

## 🚀 Future Enhancements

Potential features to add:
- **Self-collision detection** - Snake hits its own body
- **Speed progression** - Game gets faster as score increases
- **High score system** - Persistent score tracking
- **Power-ups** - Special food with bonus effects
- **Sound effects** - Audio feedback for actions
- **Multiple game modes** - Different gameplay variations

## 🤝 Contributing

This project follows professional coding standards:
- Clean, readable code with meaningful names
- Comprehensive documentation and comments
- Modular architecture for easy extension
- Consistent coding style throughout

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

## 🏅 Development Journey

This Snake game was built following professional software development practices:

1. **Started simple** - Basic moving square
2. **Added features incrementally** - Controls, collision, food, growth
3. **Refactored for quality** - Organized into clean functions
4. **Applied OOP principles** - Single class design
5. **Achieved modular architecture** - Separate specialized classes
6. **Professional polish** - Clean UI, proper error handling

**Result: Production-ready, enterprise-quality game code!** 🎯

---

### 🎮 Ready to Play?

```bash
python snake_game.py
```

**Enjoy the game and happy coding!** 🐍✨