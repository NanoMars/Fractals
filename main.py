import turtle

class Canvas:
    def __init__(self, x, y, objects, turtle):
        self.x = x
        self.y = y
        
    def move(self, x, y):
        self.x += x
        self.y += y
        
    def draw(self, command, args, x , y):
        #hi
        print("hi")
        
        
# Set up the screen
screen = turtle.Screen()
screen.title("testing")
pen = turtle.Turtle()

x = 0
y = 0


canvas = Canvas(0, 0, [], pen)

# Keep the window open and responsive
screen.mainloop()