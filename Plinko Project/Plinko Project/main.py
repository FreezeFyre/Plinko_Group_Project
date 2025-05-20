import pygame
import math
import random

# Setup
ASPECT_RATIO = (16, 9)
WINDOW_WIDTH = 1920 / 2
WINDOW_HEIGHT = int(WINDOW_WIDTH / ASPECT_RATIO[0] * ASPECT_RATIO[1])

SIM_WIDTH = 100
SIM_HEIGHT = (SIM_WIDTH / ASPECT_RATIO[0]) * ASPECT_RATIO[1]

# Ball parameters
class Ball:
    def __init__(self):
        self.id = 0
        self.pos = [50.1, SIM_HEIGHT]
        self.velocity = [random.uniform(-0.01, 0.01), 0]  # randomized horizontal velocity
        self.bounce_damp = random.uniform(0.7, 0.95)      # randomized bounce damping
        self.rad = 0.5

# Global parameters
class GlobalParams:
    def __init__(self):
        self.gravity = -.98
        self.air_damping = 0.99
        self.substeps = 4
        self.loop_thresh = 1000

# Pin parameters
class Pin:
    def __init__(self, x, y, rad=0.5):
        self.pos = [x, y]
        self.rad = rad

# Coordinate conversion
def sim_to_screen(pos):
    x = int((pos[0] / SIM_WIDTH) * WINDOW_WIDTH)
    y = int((1 - (pos[1] / SIM_HEIGHT)) * WINDOW_HEIGHT)
    return (x, y)

# Initialize pins
def initialize_pins():
    return [
        Pin(50.0, 45.0),
        Pin(46.5, 41.5),
        Pin(53.5, 41.5),
        Pin(43.0, 38.0),
        Pin(50.0, 38.0),
        Pin(57.0, 38.0),
        Pin(39.5, 34.5),
        Pin(46.5, 34.5),
        Pin(53.5, 34.5),
        Pin(60.5, 34.5),
        Pin(36.0, 31.0),
        Pin(43.0, 31.0),
        Pin(50.0, 31.0),
        Pin(57.0, 31.0),
        Pin(64.0, 31.0),
        Pin(32.5, 27.5),
        Pin(39.5, 27.5),
        Pin(46.5, 27.5),
        Pin(53.5, 27.5),
        Pin(60.5, 27.5),
        Pin(67.5, 27.5),
        Pin(29.0, 24.0),
        Pin(36.0, 24.0),
        Pin(43.0, 24.0),
        Pin(50.0, 24.0),
        Pin(57.0, 24.0),
        Pin(64.0, 24.0),
        Pin(71.0, 24.0),
        Pin(25.5, 20.5),
        Pin(32.5, 20.5),
        Pin(39.5, 20.5),
        Pin(46.5, 20.5),
        Pin(53.5, 20.5),
        Pin(60.5, 20.5),
        Pin(67.5, 20.5),
        Pin(74.5, 20.5),
        Pin(22.0, 17.0),
        Pin(29.0, 17.0),
        Pin(36.0, 17.0),
        Pin(43.0, 17.0),
        Pin(50.0, 17.0),
        Pin(57.0, 17.0),
        Pin(64.0, 17.0),
        Pin(71.0, 17.0),
        Pin(78.0, 17.0)
    ]

# Physics
def pin_solver(ball, pins):
    for pin in pins:
        dx = ball.pos[0] - pin.pos[0]
        dy = ball.pos[1] - pin.pos[1]
        d = math.hypot(dx, dy)
        if d < pin.rad + ball.rad:
            if d == 0:
                nx, ny = 1.0, 0.0
            else:
                nx = dx / d
                ny = dy / d
            overlap = pin.rad + ball.rad - d
            ball.pos[0] += nx * overlap
            ball.pos[1] += ny * overlap
            dot = ball.velocity[0] * nx + ball.velocity[1] * ny
            ball.velocity[0] -= 2 * dot * nx
            ball.velocity[1] -= 2 * dot * ny
            ball.velocity[0] *= ball.bounce_damp
            ball.velocity[1] *= ball.bounce_damp

def floor_ceil_collision(ball):
    if ball.pos[1] < 0:
        ball.velocity[1] *= -1
        ball.pos[1] = 0.01
        ball.velocity[0] *= ball.bounce_damp
        ball.velocity[1] *= ball.bounce_damp
    elif ball.pos[1] > SIM_HEIGHT:
        ball.velocity[1] *= -1
        ball.pos[1] = SIM_HEIGHT - 0.01
        ball.velocity[0] *= ball.bounce_damp
        ball.velocity[1] *= ball.bounce_damp

def wall_collision(ball):
    if ball.pos[0] < 0:
        ball.velocity[0] *= -1
        ball.velocity[0] *= ball.bounce_damp
        ball.velocity[1] *= ball.bounce_damp
    elif ball.pos[0] > SIM_WIDTH:
        ball.velocity[0] *= -1
        ball.velocity[0] *= ball.bounce_damp
        ball.velocity[1] *= ball.bounce_damp

def sim_operations(ball, global_params, pins):
    ball.velocity[0] *= global_params.air_damping
    ball.velocity[1] *= global_params.air_damping
    ball.velocity[1] += global_params.gravity * 0.016  # ~60fps
    ball.pos[0] += ball.velocity[0]
    ball.pos[1] += ball.velocity[1]
    floor_ceil_collision(ball)
    wall_collision(ball)
    pin_solver(ball, pins)
    return sim_to_screen(ball.pos)

# Pygame loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    ball = Ball()
    global_params = GlobalParams()
    pins = initialize_pins()

    running = True
    count = 0
    while running and count < global_params.loop_thresh:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((30, 30, 30))
        screen_pos = sim_operations(ball, global_params, pins)

        # Draw ball
        pygame.draw.circle(screen, (255, 0, 0), screen_pos, int(ball.rad / SIM_WIDTH * WINDOW_WIDTH * 2))

        # Draw pins
        for pin in pins:
            pin_pos = sim_to_screen(pin.pos)
            pygame.draw.circle(screen, (200, 200, 200), pin_pos, int(pin.rad / SIM_WIDTH * WINDOW_WIDTH * 2))

        pygame.display.flip()
        clock.tick(60)
        count += 1

    pygame.quit()

main()
