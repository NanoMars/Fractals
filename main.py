import turtle

class Canvas:
    def __init__(self, x, y, objects, turtle):
        self.x = x
        self.y = y
        self.objects = objects
        self.turtle = turtle
    def move(self, x, y):
        self.x += x
        self.y += y
        
    def add(self, command, *args, **kwargs):
        
        self.original_x = kwargs.get('x', args[0] if len(args) > 0 else None)
        self.original_y = kwargs.get('y', args[1] if len(args) > 1 else None)
        
        self.new_args = (args, kwargs)
        self.objects.append((command, self.new_args, (self.original_x, self.original_y)))
        
    def draw(self, x, y):
        turtle.goto(-self.x,-self.y)
        for command, args, (original_x, original_y) in self.objects:
            new_x = original_x - self.x
            new_y = original_y - self.y
            args['x'] = new_x
            args['y'] = new_y
            command(*args)
        

# Set up the screen
screen = turtle.Screen()
screen.title("testing")
pen = turtle.Turtle()

x = 0
y = 0
objects = []

c = Canvas(x, y, objects, pen)

c.add(pen.goto, 20, 20)

c.draw(x, y)
# Keep the window open and responsive
screen.mainloop()