import math
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

    def is_within_screen(self, x, y):
        screen_width, screen_height = self.turtle.screen.window_width(), self.turtle.screen.window_height()
        half_width, half_height = screen_width // 2, screen_height // 2
        return (-half_width <= x <= half_width) and (-half_height <= y <= half_height)

    def draw(self):
        self.current_id += 1
        self.execution_ids.append(self.current_id)
        self.turtle.hideturtle()
        self.turtle.clear()
        self.turtle.penup()
        self.turtle.goto((-self.x) * self.scale, (-self.y) * self.scale)
        self.turtle.showturtle()

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

            x = new_kwargs.get('x', new_args[0] if len(new_args) > 0 else None)
            y = new_kwargs.get('y', new_args[1] if len(new_args) > 1 else None)

            if command.__name__ == 'penup':
                print(f"Executing penup")
                self.turtle.penup()
            elif command.__name__ == 'pendown':
                print(f"Executing pendown")
                self.turtle.pendown()
            else:
                if x is not None and y is not None and self.is_within_screen(x, y):
                    print(f"Executing {command.__name__} with args {new_args} and kwargs {new_kwargs}")
                    command(*new_args, **new_kwargs)

        self.execution_ids.remove(self.current_id)
    def get_fractal_order(self, base_order, min_order=0, max_order=10):
        # Adjust the range and factor to suit your needs
        scale_factor = 5
        adjusted_order = base_order + int(self.scale * scale_factor)
        return max(min_order, min(max_order, adjusted_order))

class MouseEventHandler:
    def __init__(self, camera, screen):
        self.camera = camera
        self.screen = screen
        self.mouse_down_pos = None

    def on_mouse_down(self, x, y):
        self.mouse_down_pos = (x, y)
        print(f"Mouse down at: {self.mouse_down_pos}")

    def on_mouse_up(self, event):
        mouse_up_pos = (event.x - self.screen.window_width() // 2, 
                        -(event.y - self.screen.window_height() // 2))
        print(f"Mouse up at: {mouse_up_pos}")
        if self.mouse_down_pos:
            x_diff = (mouse_up_pos[0] - self.mouse_down_pos[0]) / self.camera.scale
            y_diff = (mouse_up_pos[1] - self.mouse_down_pos[1]) / self.camera.scale
            print(f"Mouse diff: {x_diff}, {y_diff}")
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

def calculate_components(angle, distance):
    radians = math.radians(angle)
    dx = distance * math.cos(radians)
    dy = distance * math.sin(radians)
    return dx, dy

def add_line(camera, x, y, angle, distance):
    dx, dy = calculate_components(angle, distance)
    camera.add(camera.turtle.penup)
    print("Added penup")
    camera.add(camera.turtle.goto, x, y)
    print(f"Added goto ({x}, {y})")
    camera.add(camera.turtle.pendown)
    print("Added pendown")
    camera.add(camera.turtle.goto, x + dx, y + dy)
    print(f"Added goto ({x + dx}, {y + dy})")
    camera.add(camera.turtle.penup)
    print("Added penup")

def draw_koch(camera, turtle, base_order, size, x=0, y=0, angle=0):
    order = camera.get_fractal_order(base_order)
    if order == 0:
        add_line(camera, x, y, angle, size)
    else:
        for angle_change in [60, -120, 60, 0]:
            draw_koch(camera, turtle, order - 1, size / 3, x, y, angle)
            dx, dy = calculate_components(angle, size / 3)
            x += dx
            y += dy
            angle += angle_change

def draw_sierpinski(camera, turtle, base_order, size, x=0, y=0, angle=0):
    order = camera.get_fractal_order(base_order)
    if order == 0:
        for _ in range(3):
            add_line(camera, x, y, angle, size)
            dx, dy = calculate_components(angle, size)
            x += dx
            y += dy
            angle += 120
    else:
        for _ in range(3):
            draw_sierpinski(camera, turtle, order - 1, size / 2, x, y, angle)
            dx, dy = calculate_components(angle, size)
            x += dx
            y += dy
            angle += 120

def draw_tree(camera, turtle, branch_length, shorten_by, angle, x=0, y=0, current_angle=0):
    if branch_length > 5:
        add_line(camera, x, y, current_angle, branch_length)
        dx, dy = calculate_components(current_angle, branch_length)
        x += dx
        y += dy
        draw_tree(camera, turtle, branch_length - shorten_by, shorten_by, angle, x, y, current_angle + angle)
        draw_tree(camera, turtle, branch_length - shorten_by, shorten_by, angle, x, y, current_angle - angle)
        add_line(camera, x, y, current_angle + 180, branch_length)

def draw_dragon(camera, turtle, base_order, size, x=0, y=0, angle=0, sign=1):
    order = camera.get_fractal_order(base_order)
    if order == 0:
        add_line(camera, x, y, angle, size)
    else:
        draw_dragon(camera, turtle, order - 1, size / 1.414, x, y, angle, 1)
        dx, dy = calculate_components(angle, size / 1.414)
        x += dx
        y += dy
        draw_dragon(camera, turtle, order - 1, size / 1.414, x, y, angle + 45 * sign, -1)
        angle += -45 * sign

def draw_tree(camera, turtle, branch_length, shorten_by, angle, x=0, y=0, current_angle=0):
    if branch_length > 5:
        add_line(camera, x, y, current_angle, branch_length)
        dx, dy = calculate_components(current_angle, branch_length)
        x += dx
        y += dy
        draw_tree(camera, turtle, branch_length - shorten_by, shorten_by, angle, x, y, current_angle + angle)
        draw_tree(camera, turtle, branch_length - shorten_by, shorten_by, angle, x, y, current_angle - angle)
        add_line(camera, x, y, current_angle + 180, branch_length)

def draw_dragon(camera, turtle, order, size, x=0, y=0, angle=0, sign=1):
    if order == 0:
        add_line(camera, x, y, angle, size)
    else:
        draw_dragon(camera, turtle, order - 1, size / 1.414, x, y, angle, 1)
        dx, dy = calculate_components(angle, size / 1.414)
        x += dx
        y += dy
        draw_dragon(camera, turtle, order - 1, size / 1.414, x, y, angle + 45 * sign, -1)
        angle += -45 * sign

def draw_fractal(fractal_function, *args, **kwargs):
    pen.reset()
    pen.penup()
    pen.goto(-200, 0)
    pen.pendown()
    fractal_function(c, pen, *args, **kwargs)
    c.draw()
    pen.reset()
    pen.penup()
    pen.goto(-200, 0)
    pen.pendown()
    fractal_function(c, pen, *args, **kwargs)
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
screen.onkey(lambda: draw_fractal(draw_koch, 3, 400), "1")
screen.onkey(lambda: draw_fractal(draw_sierpinski, 3, 400), "2")
screen.onkey(lambda: draw_fractal(draw_tree, 100, 15, 30), "3")
screen.onkey(lambda: draw_fractal(draw_dragon, 3, 200), "4")
screen.listen()



# Keep the window open and responsive
screen.mainloop()