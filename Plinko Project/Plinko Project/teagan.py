import pygame
from pygame.math import Vector2

# Setup
aspect_ratio = [16, 9]
scr_width = 1000
scr_height = int((scr_width / aspect_ratio[0]) * aspect_ratio[1])

sim_width = 100
sim_height = int((sim_width / aspect_ratio[0]) * aspect_ratio[1])

gravity = 9.8 / 60
air_damping = 0.99
bounce_damping = 0.9

loop_thresh = 100
max_velocity = 300
max_fps = 60
max_balls = 50

screen_color = 'Black'
wall_color = 'White'
wall_thickness = 5

pygame.init()
screen = pygame.display.set_mode((scr_width, scr_height), pygame.SCALED)
pygame.display.set_caption('Plinko!')
clock = pygame.time.Clock()

def draw_walls():
    pygame.draw.rect(screen, wall_color, (0, 0, scr_width, scr_height), wall_thickness)

class Pin:
    radius = 10
    color = 'White'
    all_pins = []
    rows = 9
    per_row = 14

    def __init__(self, x, y):
        self.pos = Vector2(x, y)

    def generate():
        width = (scr_width - (2 * wall_thickness))
        height = (scr_height - (2 * wall_thickness)) * 0.7
        spacing = (width / Pin.per_row)
        for row in range(Pin.rows):
            if row % 2 == 0:  # Offset every other row
                for pin in range(Pin.per_row + 1):
                    x = (spacing * pin) + wall_thickness
                    y = ((height / Pin.rows) * row) + (scr_height * 0.2)
                    Pin.all_pins.append(Pin(x, y))
            else:
                for pin in range(Pin.per_row):
                    x = (spacing * (pin + 1)) - (spacing / 2) + wall_thickness
                    y = ((height/ Pin.rows) * row) + (scr_height * 0.2)
                    Pin.all_pins.append(Pin(x, y))
        print(f"Generated {Pin.rows} rows of pins, alternating {Pin.per_row} and {Pin.per_row + 1} per row. Total pins: {len(Pin.all_pins)}")

    def draw(self):
        pygame.draw.circle(screen, Pin.color, (int(self.pos.x), int(self.pos.y)), Pin.radius)

class Ball:

    radius = 10         # Ball radius
    color = 'Red'       # Ball color
    indicator_color = 'Dark red'  # Color of the indicator ball
    ball_id = 0         # Ball ID manager
    total = []      # Dictionary to hold all balls
    spawn_height = (scr_height * 0.05)   # Height that balls spawn at

    def __init__(self, x):
        self.pos = Vector2(x, Ball.spawn_height)    # Position vector
        self.velocity = Vector2(0, 0)               # Velocity vector
        Ball.total.append(self)                     # Store ball in list

    def wall_collision(self):
        if self.pos.y > scr_height - self.radius - wall_thickness:  # If ball hits floor
            self.pos.y = scr_height - self.radius - wall_thickness  # Put ball within bounds
            self.velocity.y *= -bounce_damping                # Apply bounce damping on y axis
        elif self.pos.y < self.radius + wall_thickness:         # Or if ball hits ceiling ^
            self.pos.y = self.radius + wall_thickness
            self.velocity.y *= -bounce_damping
            print("Ball collided with ceiling")

        if self.pos.x < self.radius + wall_thickness:           # If ball hits left wall
            self.pos.x = self.radius + wall_thickness           # Put ball within bounds
            self.velocity.x *= -bounce_damping                   # Apply bounce damping on x axis
            print("Ball collided with left wall")
        elif self.pos.x > scr_width - self.radius - wall_thickness: # Or if ball hits right wall ^
            self.pos.x = scr_width - self.radius - wall_thickness
            self.velocity.x *= -bounce_damping
            print("Ball collided with right wall")

    def pin_collision(self):
        for pin in Pin.all_pins:
            dist = ((self.pos.x - pin.pos.x) ** 2 + (self.pos.y - pin.pos.y) ** 2) ** 0.5
            if dist < self.radius + Pin.radius:
                delta = self.pos - pin.pos
                normal = delta.normalize() if delta.length() > 0 else Vector2(0,0)
                overlap = self.radius + Pin.radius + 0.01
                dot = self.velocity.dot(normal)
                self.pos += normal * (overlap - dist)
                self.velocity -= normal * dot * 2 * bounce_damping # Reflect velocity

    def ball_collision(self, other_ball):
        for ball in Ball.total:
            if ball is not self:  # Avoid self-collision
                dist = ((self.pos.x - ball.pos.x) ** 2 + (self.pos.y - ball.pos.y) ** 2) ** 0.5
                if dist < ball.radius * 2:  # If balls are colliding
                    delta = self.pos - ball.pos
                    normal = delta.normalize() if delta.length() > 0 else Vector2(0,0)
                    overlap = self.radius + Pin.radius + 0.01
                    dot = self.velocity.dot(normal)
                    self.pos += normal * (overlap - dist)
                    self.velocity -= normal * dot * 2 * bounce_damping # Reflect velocity
                    if self.velocity.x > 0.5 and self.velocity.y > 0.5:  # Prevent very small velocities
                        print("Ball collided with ball")

            



    def update_pos(self):               # Function to check collisions and update position
        self.velocity.y += gravity      # Apply gravity on y axis
        self.velocity *= air_damping    # Apply air damping
        self.pos += self.velocity       # Move ball by velocity
        Ball.wall_collision(self)       # Check for wall collisions
        
    def draw(self): # Function for drawing ball each frame
        pygame.draw.circle(screen, Ball.color, (int(self.pos.x), int(self.pos.y)), Ball.radius)

    def draw_indicator():
        mouse_x, _ = pygame.mouse.get_pos()

        if mouse_x < Ball.radius + wall_thickness:
            mouse_x = Ball.radius + wall_thickness
        elif mouse_x > scr_width - Ball.radius - wall_thickness:
            mouse_x = scr_width - Ball.radius - wall_thickness

        pygame.draw.circle(screen, Ball.indicator_color, (mouse_x, Ball.spawn_height), Ball.radius)

def clear_all():
    Ball.total.clear()  # Clear all balls

running = True

Pin.generate()  # Generate pins 

while running:          # Main game loop, runs each frame
    clock.tick(max_fps) # Limit frame rate to max_fps

    screen.fill(screen_color)
    Ball.draw_indicator()
    
    for event in pygame.event.get():    # Detect user inputs
        if event.type == pygame.QUIT:               # If user tries to close the window
            running = False                         # Stop game loop
            print("Game closed by user")
        if event.type == pygame.MOUSEBUTTONDOWN:  # On mouse click
            if len(Ball.total) >= max_balls:
                print(f"Maximum number of balls reached ({max_balls})")
            else:
                mouse_x, _ = pygame.mouse.get_pos()     # Get mouse x pos
                Ball(mouse_x)
                print("Ball spawned at x =", mouse_x)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            clear_all()
            print("All balls cleared")

    for ball in Ball.total:      # For each ball in the dictionary
        ball.update_pos()                           # Update ball position
        ball.pin_collision()                        # Check for pin collisions
        ball.draw()                                 # Draw ball in new position
        ball.ball_collision(ball)                  # Check for ball collisions

    for pin in Pin.all_pins:
        pin.draw()

    draw_walls()
   
    pygame.display.flip()   # Update display

pygame.quit()   # End the program
