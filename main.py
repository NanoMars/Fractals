import math
import turtle
import inspect
from tkinter import *

class Camera:
    def __init__(self, x, y, objects, turtle, screen, scale=1):
        self.x = x
        self.y = y
        self.objects = objects
        self.turtle = turtle
        self.execution_ids = []
        self.current_id = 0
        self.scale = scale
        self.redraw = 0
        self.current_position = (0, 0)  # Track the turtle's current position
        self.screen = screen  # Store the screen reference for dynamic size checking
        self.screen_width = screen.window_width() // 2
        self.screen_height = screen.window_height() // 2

    def update_screen_size(self):
        """Update the screen dimensions."""
        self.screen_width = self.screen.window_width() // 2
        self.screen_height = self.screen.window_height() // 2

    def add(self, command, *args, **kwargs):
        sig = inspect.signature(command)
        params = sig.parameters
        original_x = kwargs.get('x', args[0] if len(args) > 0 else None)
        original_y = kwargs.get('y', args[1] if len(args) > 1 else None)
        new_args = (args, kwargs)
        self.objects.append((command, new_args, (original_x, original_y)))

    def update_position(self, command, *args, **kwargs):
        """Update the turtle's position based on the command."""
        if command.__name__ == 'goto':
            new_x = kwargs.get('x', args[0] if len(args) > 0 else None)
            new_y = kwargs.get('y', args[1] if len(args) > 1 else None)
            if new_x is not None and new_y is not None:
                # Adjust the position based on camera position and scale
                adjusted_x = (new_x - self.x) * self.scale
                adjusted_y = (new_y - self.y) * self.scale
                self.current_position = (adjusted_x, adjusted_y)
        elif command.__name__ in ['forward', 'fd']:
            distance = args[0] * self.scale if len(args) > 0 else kwargs.get('distance', 0) * self.scale
            angle = self.turtle.heading()
            dx, dy = calculate_components(angle, distance)
            self.current_position = (
                self.current_position[0] + dx,
                self.current_position[1] + dy
            )
        elif command.__name__ in ['back', 'backward', 'bk']:
            distance = args[0] * self.scale if len(args) > 0 else kwargs.get('distance', 0) * self.scale
            angle = self.turtle.heading()
            dx, dy = calculate_components(angle, -distance)
            self.current_position = (
                self.current_position[0] + dx,
                self.current_position[1] + dy
            )

    def draw(self):
        self.current_id += 1
        self.execution_ids.append(self.current_id)
        self.turtle.reset()
        self.turtle.hideturtle()
        self.turtle.clear()
        self.turtle.penup()
        self.turtle.goto((-self.x) * self.scale, (-self.y) * self.scale)
        self.turtle.showturtle()

        # Update the screen size before drawing, considering the scale
        self.update_screen_size()
        scaled_screen_width = self.screen_width / self.scale
        scaled_screen_height = self.screen_height / self.scale

        for command, (args, kwargs), (original_x, original_y) in self.objects:
            if self.execution_ids and self.execution_ids[-1] != self.current_id:
                continue

            # Calculate the adjusted start position
            start_pos = (
                (self.current_position[0] - self.x) * self.scale,
                (self.current_position[1] - self.y) * self.scale
            )

            # Update the turtle's position based on the command
            self.update_position(command, *args, **kwargs)

            # Calculate the adjusted end position
            end_pos = (
                (self.current_position[0] - self.x) * self.scale,
                (self.current_position[1] - self.y) * self.scale
            )

            # Check if either the start or end positions are outside the screen boundaries
            if (start_pos[0] < -scaled_screen_width or start_pos[0] > scaled_screen_width or
                start_pos[1] < -scaled_screen_height or start_pos[1] > scaled_screen_height or
                end_pos[0] < -scaled_screen_width or end_pos[0] > scaled_screen_width or
                end_pos[1] < -scaled_screen_height or end_pos[1] > scaled_screen_height):
                self.turtle.pencolor("red")
            else:
                self.turtle.pencolor("black")

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

def calculate_components(angle, distance):
    radians = math.radians(angle)
    dx = distance * math.cos(radians)
    dy = distance * math.sin(radians)
    return dx, dy

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
            
        

def calculate_components(angle, distance):
    radians = math.radians(angle)
    dx = distance * math.cos(radians)
    dy = distance * math.sin(radians)
    return dx, dy

def add_line(camera, x, y, angle, distance):
    dx, dy = calculate_components(angle, distance)
    
    # Move the turtle and draw the line
    camera.add(camera.turtle.pendown)
    camera.add(camera.turtle.goto, x + dx, y + dy)
    camera.add(camera.turtle.penup)
    
def draw_koch(camera, turtle, order, size, x=0, y=0, angle=0):
    if order == 0:
        add_line(camera, x, y, angle, size)
    else:
        for angle_change in [60, -120, 60, 0]:
            draw_koch(camera, turtle, order-1, size/3, x, y, angle)
            dx, dy = calculate_components(angle, size/3)
            x += dx
            y += dy
            angle += angle_change

def draw_sierpinski(camera, turtle, order, size, x=0, y=0, angle=0):
    if order == 0:
        for _ in range(3):
            add_line(camera, x, y, angle, size)
            dx, dy = calculate_components(angle, size)
            x += dx
            y += dy
            angle += 120
    else:
        for _ in range(3):
            draw_sierpinski(camera, turtle, order-1, size/2, x, y, angle)
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

def draw_fractal(fractal_function, *args):
    pen.reset()
    pen.penup()
    pen.goto(-200, 0)
    pen.pendown()
    fractal_function(c, pen, *args, x=-200, y=0, angle=0)
    c.draw()
    
def draw_border(camera):
    """Draw a border around the screen size."""
    camera.update_screen_size()
    left = -camera.screen_width
    right = camera.screen_width
    top = camera.screen_height
    bottom = -camera.screen_height

    # Draw the four sides of the border
    add_line(camera, left, top, 0, right - left)
    add_line(camera, right, top, -90, top - bottom)
    add_line(camera, right, bottom, 180, right - left)
    add_line(camera, left, bottom, 90, top - bottom)

    camera.draw()

# Set up the screen
screen = turtle.Screen()
screen.title("Fractal Drawer")
pen = turtle.Turtle()
pen.speed(0)
objects = []

# Create the Camera instance with the screen passed as an argument
c = Camera(0, 0, objects, pen, screen, scale=1)

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

# Set up the button to draw the border
button = Button(screen.getcanvas().master, text="Draw Border", command=lambda: draw_border(c))
button.pack()
screen.listen()



# Keep the window open and responsive
screen.mainloop()