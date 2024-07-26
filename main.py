import turtle
import inspect
from tkinter import *

class Camera:
    def __init__(self, x, y, objects, turtle, scale=1):
        self.x = x
        self.y = y
        self.objects = objects
        self.turtle = turtle
        self.execution_ids = []
        self.current_id = 0
        self.scale = scale
        self.redraw = 0

    def add(self, command, *args, **kwargs):
        sig = inspect.signature(command)
        params = sig.parameters
        original_x = kwargs.get('x', args[0] if len(args) > 0 else None)
        original_y = kwargs.get('y', args[1] if len(args) > 1 else None)
        new_args = (args, kwargs)
        self.objects.append((command, new_args, (original_x, original_y)))

    def draw(self):
        self.current_id += 1
        self.execution_ids.append(self.current_id)
        self.turtle.reset()
        self.turtle.hideturtle()
        self.turtle.clear()
        self.turtle.penup()
        self.turtle.goto((-self.x) * self.scale, (-self.y) * self.scale)
        self.turtle.showturtle()
        self.turtle.pendown()

        for command, (args, kwargs), (original_x, original_y) in self.objects:
            if self.execution_ids and self.execution_ids[-1] != self.current_id:
                continue
            new_args = list(args)
            new_kwargs = dict(kwargs)
            sig = inspect.signature(command)
            params = sig.parameters

            if command.__name__ in ['forward', 'fd', 'back', 'backward', 'bk', 'circle']:
                if len(new_args) > 0:
                    new_args[0] *= self.scale
                if 'distance' in new_kwargs:
                    new_kwargs['distance'] *= self.scale
                if 'radius' in new_kwargs:
                    new_kwargs['radius'] *= self.scale

            if 'x' in params and original_x is not None:
                if 'x' in new_kwargs:
                    new_kwargs['x'] = (original_x - self.x) * self.scale
                else:
                    index = list(params.keys()).index('x')
                    if index < len(new_args):
                        new_args[index] = (original_x - self.x) * self.scale

            if 'y' in params and original_y is not None:
                if 'y' in new_kwargs:
                    new_kwargs['y'] = (original_y - self.y) * self.scale
                else:
                    index = list(params.keys()).index('y')
                    if index < len(new_args):
                        new_args[index] = (original_y - self.y) * self.scale

            command(*new_args, **new_kwargs)

        self.execution_ids.remove(self.current_id)

class MouseEventHandler:
    def __init__(self, camera, screen):
        self.camera = camera
        self.screen = screen
        self.mouse_down_pos = None

    def on_mouse_down(self, x, y):
        self.mouse_down_pos = (x, y)

    def on_mouse_up(self, event):
        mouse_up_pos = (event.x - self.screen.window_width() // 2, 
                        -(event.y - self.screen.window_height() // 2))
        if self.mouse_down_pos:
            x_diff = (mouse_up_pos[0] - self.mouse_down_pos[0]) / self.camera.scale
            y_diff = (mouse_up_pos[1] - self.mouse_down_pos[1]) / self.camera.scale
            self.camera.x -= x_diff
            self.camera.y -= y_diff
            self.camera.draw()

    def on_scroll(self, event):
        self.camera.redraw += abs(event.delta)
        self.camera.scale -= (event.delta / 5)
        self.camera.scale = max(0.1, self.camera.scale)
        if self.camera.redraw > 5:
            self.camera.redraw = 0
            self.camera.draw()

def draw_koch(camera, turtle, order, size):
    if order == 0:
        camera.add(turtle.forward, size)
    else:
        for angle in [60, -120, 60, 0]:
            draw_koch(camera, turtle, order-1, size/3)
            camera.add(turtle.left, angle)

def draw_sierpinski(camera, turtle, order, size):
    if order == 0:
        for _ in range(3):
            camera.add(turtle.forward, size)
            camera.add(turtle.left, 120)
    else:
        for _ in range(3):
            draw_sierpinski(camera, turtle, order-1, size/2)
            camera.add(turtle.forward, size)
            camera.add(turtle.left, 120)

def draw_tree(camera, turtle, branch_length, shorten_by, angle):
    if branch_length > 5:
        camera.add(turtle.forward, branch_length)
        camera.add(turtle.left, angle)
        draw_tree(camera, turtle, branch_length - shorten_by, shorten_by, angle)
        camera.add(turtle.right, angle * 2)
        draw_tree(camera, turtle, branch_length - shorten_by, shorten_by, angle)
        camera.add(turtle.left, angle)
        camera.add(turtle.backward, branch_length)

def draw_dragon(camera, turtle, order, size, sign=1):
    if order == 0:
        camera.add(turtle.forward, size)
    else:
        draw_dragon(camera, turtle, order - 1, size / 1.414, 1)
        camera.add(turtle.left, 45 * sign)
        draw_dragon(camera, turtle, order - 1, size / 1.414, -1)
        camera.add(turtle.right, 45 * sign)

def draw_fractal(fractal_function, *args):
    pen.reset()
    pen.penup()
    pen.goto(-200, 0)
    pen.pendown()
    fractal_function(c, pen, *args)
    c.draw()

# Set up the screen
screen = turtle.Screen()
screen.title("Fractal Drawer")
pen = turtle.Turtle()
pen.speed(0)
objects = []

c = Camera(0, 0, objects, pen, scale=3)

# Set up the mouse event handler
mouse_handler = MouseEventHandler(c, screen)
screen.onscreenclick(mouse_handler.on_mouse_down, 1)
canvas = screen.getcanvas()
canvas.bind("<ButtonRelease-1>", mouse_handler.on_mouse_up)
canvas.bind_all("<MouseWheel>", mouse_handler.on_scroll)

# Bind keys to draw different fractals
screen.onkey(lambda: draw_fractal(draw_koch, 4, 400), "1")
screen.onkey(lambda: draw_fractal(draw_sierpinski, 4, 400), "2")
screen.onkey(lambda: draw_fractal(draw_tree, 100, 15, 30), "3")
screen.onkey(lambda: draw_fractal(draw_dragon, 10, 200), "4")
screen.listen()

# Keep the window open and responsive
screen.mainloop()