import turtle
import inspect

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
        sig = inspect.signature(command)
        params = sig.parameters
        original_x = kwargs.get('x', args[0] if len(args) > 0 else None)
        original_y = kwargs.get('y', args[1] if len(args) > 1 else None)
        new_args = (args, kwargs)
        self.objects.append((command, new_args, (original_x, original_y)))
        
    def draw(self, x, y):
        self.turtle.penup()
        self.turtle.clear()
        self.turtle.goto(-x, -y)
        for command, (args, kwargs), (original_x, original_y) in self.objects:
            new_args = list(args)
            new_kwargs = dict(kwargs)
            sig = inspect.signature(command)
            params = sig.parameters

            if 'x' in params and original_x is not None:
                if 'x' in new_kwargs:
                    new_kwargs['x'] = original_x - x
                else:
                    index = list(params.keys()).index('x')
                    if index < len(new_args):
                        new_args[index] = original_x - x

            if 'y' in params and original_y is not None:
                if 'y' in new_kwargs:
                    new_kwargs['y'] = original_y - y
                else:
                    index = list(params.keys()).index('y')
                    if index < len(new_args):
                        new_args[index] = original_y - y

            command(*new_args, **new_kwargs)

# Set up the screen
screen = turtle.Screen()
screen.title("Testing")
pen = turtle.Turtle()
pen.speed(0)

x = 0
y = 0

objects = []

c = Canvas(x, y, objects, pen)
c.add(pen.pendown)
c.add(pen.goto, 20, 20)
c.add(pen.goto, 0, 40)
c.add(pen.goto, -20, 20)
c.add(pen.goto, 0, 0)

c.draw(x, y)

# Define functions to move the canvas
def move_up():
    global y
    y -= 20
    c.draw(x, y)

def move_down():
    global y
    y += 20
    c.draw(x, y)

def move_left():
    global x
    x += 20
    c.draw(x, y)

def move_right():
    global x
    x -= 20
    c.draw(x, y)

# Bind the arrow keys to the movement functions
screen.onkey(move_up, "Up")
screen.onkey(move_down, "Down")
screen.onkey(move_left, "Left")
screen.onkey(move_right, "Right")
screen.listen()

# Keep the window open and responsive
screen.mainloop()