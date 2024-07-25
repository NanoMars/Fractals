import turtle
import inspect
from tkinter import *

# Declare global variables
global_x, global_y = 0, 0

class Camera:
    def __init__(self, x, y, objects, turtle):
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

    def draw(self, x, y):
        self.turtle.reset()
        self.turtle.hideturtle()
        self.turtle.clear()
        self.turtle.penup()
        self.turtle.teleport(-x,-y)
        self.turtle.showturtle()
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


class MouseEventHandler:
    def __init__(self, canvas, screen):
        self.canvas = canvas
        self.screen = screen
        self.mouse_down_pos = None

    def on_mouse_down(self, x, y):
        self.mouse_down_pos = (x, y)

    def on_mouse_up(self, event):
        global global_x, global_y
        mouse_up_pos = (event.x - self.screen.window_width() // 2, 
                        -(event.y - self.screen.window_height() // 2))
        if self.mouse_down_pos:
            x_diff = mouse_up_pos[0] - self.mouse_down_pos[0]
            y_diff = mouse_up_pos[1] - self.mouse_down_pos[1]
            global_x -= x_diff
            global_y -= y_diff
            self.canvas.draw(global_x, global_y)


# Set up the screen
screen = turtle.Screen()
screen.title("Testing")
pen = turtle.Turtle()
pen.speed(0)
x, y = 0, 0
objects = []

c = Camera(x, y, objects, pen)
c.add(pen.speed, 0)
c.add(pen.pendown)
c.add(pen.goto, 20, 20)
c.add(pen.goto, 0, 40)
c.add(pen.goto, -20, 20)
c.add(pen.goto, 0, 0)
c.draw(x, y)

# Set up the mouse event handler
mouse_handler = MouseEventHandler(c, screen)
screen.onscreenclick(mouse_handler.on_mouse_down, 1)
canvas = screen.getcanvas()
canvas.bind("<ButtonRelease-1>", mouse_handler.on_mouse_up)
#canvas.bind_all("<MouseWheel>", on_scroll)


# Keep the window open and responsive
screen.mainloop()