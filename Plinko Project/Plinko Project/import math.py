import math
import time
import pygame
from dataclasses import dataclass
from typing import List

# ----- Setup -----
aspect_ratio = [16, 9]
window_width = 1280
window_height = int((window_width / aspect_ratio[0]) * aspect_ratio[1])
sim_width = 100
sim_height = (sim_width / aspect_ratio[0]) * aspect_ratio[1]


# Constants
gravity = -9.8
air_damping = 0.99
ball_radius = 1
pin_radius = 1
sample_rate = 60

# Goal Divider Settings
num_slots = 10
divider_color = (255, 255, 255)
divider_width = 2
divider_height = 100  

# ----- Pygame Init -----
pygame.init()
screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
pygame.display.set_caption("Plinko Display Test")
clock = pygame.time.Clock()

# ----- Data Classes -----
@dataclass
class BallParameters:
    pos: List[float]
    velocity: List[float]
    window_pos: List[int]

@dataclass
class PinParameters:
    pos: List[float]
    window_pos: List[int]

# ----- Ball & Pin Lists -----
ball: List[BallParameters] = []
pin: List[PinParameters] = []

# ----- Init Functions -----
def initialize_balls():
    ball.clear()
    ball.append(BallParameters([50, 80], [0.0, 0.0], [0, 0]))

def initialize_pins():
    pin.clear()
    for i in range(10):
        for j in range(5):
            x = 10 + i * 8
            y = 20 + j * 8
            pin.append(PinParameters([x, y], [0, 0]))

# ----- Conversion -----
def sim_to_window():
    global window_width, window_height
    window_width, window_height = pygame.display.get_surface().get_size()
    for b in ball:
        b.window_pos[0] = int((b.pos[0] / sim_width) * window_width)
        b.window_pos[1] = int(window_height - ((b.pos[1] / sim_height) * window_height))

    for p in pin:
        p.window_pos[0] = int((p.pos[0] / sim_width) * window_width)
        p.window_pos[1] = int(window_height - ((p.pos[1] / sim_height) * window_height))

# goal dividers
def draw_goal_dividers():
    slot_width = window_width // num_slots
    for i in range(1, num_slots):
        x = i * slot_width
        pygame.draw.line(screen, divider_color, (x, window_height), (x, window_height - divider_height), divider_width)

# draws everything
def draw(score):
    screen.fill((0, 0, 0))  

    for p in pin:
        pygame.draw.circle(screen, (255, 255, 255), p.window_pos, 5)

    # draws the ball
    for b in ball:
        pygame.draw.circle(screen, (255, 0, 0), b.window_pos, 8)

    draw_goal_dividers()

    # draws the score
    font = pygame.font.SysFont(None, 36) # font and size feel free to change it to whatever
    score_surface = font.render(f"Score: {score}", True, (255, 255, 0))  # text color
    screen.blit(score_surface, (10, 10))  

    pygame.display.flip()

# ----- Main Loop -----
pygame.init()
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Plinko Display Test")
clock = pygame.time.Clock()

def main_loop():
    initialize_pins()
    initialize_balls()
    score = 0 

    running = True
    while running:
        balls_to_remove = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for b in ball:
            b.velocity[1] += gravity / sample_rate
            b.velocity[1] *= air_damping
            b.pos[1] += b.velocity[1] / sample_rate

            if b.pos[1] <= sim_height * 0.1:
                balls_to_remove.append(b)
                score += 1

        for b in balls_to_remove:
            ball.remove(b)

        sim_to_window()
        draw(score)
        clock.tick(sample_rate)

    pygame.quit()

# ---- Run the game ----
main_loop()