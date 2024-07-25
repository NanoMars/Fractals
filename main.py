import turtle
import inspect
from tkinter import *

class Camera:
    def __init__(self, x, y, objects, turtle, scale=1):
        self.x = x
        self.y = y
        self.objects = objects
        self.turtle = turtle

    def add(self, command, *args, **kwargs):
        sig = inspect.signature(command)
        params = sig.parameters
        original_x = kwargs.get('x', args[0] if len(args) > 0 else None)
        original_y = kwargs.get('y', args[1] if len(args) > 1 else None)
        new_args = (args, kwargs)
        self.objects.append((command, new_args, (original_x, original_y)))

    def draw(self, x, y, scale=1):
        self.turtle.reset()
        self.turtle.hideturtle()
        self.turtle.clear()
        self.turtle.penup()
        self.turtle.goto((-x) * scale, (-y) * scale)
        self.turtle.showturtle()
        for command, (args, kwargs), (original_x, original_y) in self.objects:
            new_args = list(args)
            new_kwargs = dict(kwargs)
            sig = inspect.signature(command)
            params = sig.parameters

            if command.__name__ in ['forward', 'fd', 'back', 'backward', 'bk', 'circle']:
                if len(new_args) > 0:
                    new_args[0] *= scale
                if 'distance' in new_kwargs:
                    new_kwargs['distance'] *= scale
                if 'radius' in new_kwargs:
                    new_kwargs['radius'] *= scale

            if 'x' in params and original_x is not None:
                if 'x' in new_kwargs:
                    new_kwargs['x'] = (original_x - x) * scale
                else:
                    index = list(params.keys()).index('x')
                    if index < len(new_args):
                        new_args[index] = (original_x - x) * scale

            if 'y' in params and original_y is not None:
                if 'y' in new_kwargs:
                    new_kwargs['y'] = (original_y - y) * scale
                else:
                    index = list(params.keys()).index('y')
                    if index < len(new_args):
                        new_args[index] = (original_y - y) * scale

            command(*new_args, **new_kwargs)

# Set up the screen
screen = turtle.Screen()
screen.title("Testing")
pen = turtle.Turtle()
pen.speed(0)
x, y = 0, 0
scale = 3
objects = []
redraw = 0

class MouseEventHandler:
    def __init__(self, canvas, screen):
        self.canvas = canvas
        self.screen = screen
        self.mouse_down_pos = None

    def on_mouse_down(self, x, y):
        self.mouse_down_pos = (x, y)

    def on_mouse_up(self, event):
        global x, y
        mouse_up_pos = (event.x - self.screen.window_width() // 2, 
                        -(event.y - self.screen.window_height() // 2))
        if self.mouse_down_pos:
            x_diff = (mouse_up_pos[0] - self.mouse_down_pos[0]) / scale
            y_diff = (mouse_up_pos[1] - self.mouse_down_pos[1]) / scale
            x -= x_diff
            y -= y_diff
            self.canvas.draw(x, y, scale)

    def on_scroll(self, event):
        global scale, redraw
        
        self.min_redraw = 10
        redraw += abs(event.delta)
        scale -= (event.delta / 5)
        scale = max(0.1, scale)
        if self.min_redraw < redraw:
            redraw = 0
            c.draw(x, y, scale)

c = Camera(x, y, objects, pen)
c.add(pen.speed, 0)
c.add(pen.pendown)
c.add(pen.goto, 20, 20)
c.add(pen.goto, 0, 40)
c.add(pen.goto, -20, 20)
c.add(pen.goto, 0, 0)
c.add(pen.forward, 50)
c.add(pen.back,50)
c.add(pen.circle, 30)
c.draw(x, y, scale)



# Set up the mouse event handler
mouse_handler = MouseEventHandler(c, screen)
screen.onscreenclick(mouse_handler.on_mouse_down, 1)
canvas = screen.getcanvas()
canvas.bind("<ButtonRelease-1>", mouse_handler.on_mouse_up)
canvas.bind_all("<MouseWheel>", mouse_handler.on_scroll)

# Keep the window open and responsive
screen.mainloop()