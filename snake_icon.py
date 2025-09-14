# create_icon.py
from PIL import Image, ImageDraw

# Create a simple snake icon
size = 64
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw snake head (green circle)
draw.ellipse([10, 10, 54, 54], fill='green', outline='darkgreen', width=2)

# Draw eyes
draw.ellipse([20, 20, 25, 25], fill='white')
draw.ellipse([39, 20, 44, 25], fill='white')
draw.ellipse([21, 21, 24, 24], fill='black')
draw.ellipse([40, 21, 43, 24], fill='black')

# Save as ICO
img.save('snake_icon.ico', format='ICO')
print("Icon created: snake_icon.ico")