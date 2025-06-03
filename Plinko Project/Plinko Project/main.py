import math
from dataclasses import dataclass
from typing import List
import pygame
import time
import threading


aspect_ratio = [16,9];
window_width = 1440;
window_height = (window_width/aspect_ratio[0])*(aspect_ratio[1]);

sim_width = 100; ## In Meters
sim_height = (sim_width/aspect_ratio[0])*(aspect_ratio[1]);

pin_radius = 1; ## Meters

max_velocity = 300.0;

sample_rate = 120; ## In Herz

dt = 1/sample_rate
gravity = 2 * dt; ## In Meters
air_damping = .999 ** dt;

ball_radius = 1; ## In Meters
bounce_damping = .9; # Range 0 to 1
ball_radius = .5;
ball_radius = .5; ## In Meters
bounce_damping = .85; # Range 0 to 1

max_active_balls = 128;

goal_count = 10
goal_width = sim_width/goal_count
divider_color = (255, 255, 255)
divider_width = 4 # Pixel
goal_height = (sim_height/100) * 5 # Percent of Screen Height


rows = 9
per_row = 16
width = sim_width
height = sim_height * 0.7
spacing = width / per_row
y_offset = sim_height * 0.2



# Helper to count currently active balls
def count_active_balls():
    return sum(1 for b in ball if b.active)



# Define Ball Parameters
@dataclass
class BallParameters:
    pos: List[float]
    velocity: List[float]
    window_pos: List[float]
    active: bool ## 0 is inactive 1 is active
ball: List[BallParameters] = []


# Define Pin Parameters
@dataclass
class PinParameters:
    pos: List[float]
    window_pos: List[float]
pin: List[PinParameters] = []



# Ball Creation Logic Goes In Here
# Initialize Balls
def initialize_balls():
    ball.append(BallParameters([0.0 , 0.0],[0.0 , 0.0],[0.0,0.0],False))



# Pin Creation Logic Goes Here
# Initialize Pins
def initialize_pins():
    for row in range(rows):
        if row % 2 == 0:
            for i in range(per_row + 1):
                x = spacing * i
                y = (height / rows) * row + y_offset
                pin.append(PinParameters([x , y],[0.0,0.0]));
        else:
            for i in range(per_row):
                x = spacing * (i + 1) - (spacing / 2)
                y = (height / rows) * row + y_offset
                pin.append(PinParameters([x , y],[0.0,0.0]));



# Convert simulation pos to window pos and add it to each pin
def pin_window_pos():
    for n in range(len(pin)):
        pin[n].window_pos[0] = (pin[n].pos[0] / sim_width) * window_width
        pin[n].window_pos[1] = window_height - ((pin[n].pos[1] / sim_height) * window_height)



# Detect and Calculate Balls Colliding with Pins
def pin_collisions():
    for n in range(len(ball)):
        for i in range(len(pin)):
            # Distance Between  Pin And Ball
            d = math.sqrt((ball[n].pos[0] - pin[i].pos[0])**2 + (ball[n].pos[1] - pin[i].pos[1])**2)

            if d < (pin_radius + ball_radius):

                # Find Vector Pointing From The Ball To The Pin
                x_direction = pin[i].pos[0] - ball[n].pos[0]
                y_direction = pin[i].pos[1] - ball[n].pos[1]

                # Normalize Direction Vector (Make Length = 1 but still pointing same direction)
                normal_x = x_direction / d
                normal_y = y_direction / d

                # Create Dot Product (Calculates How Aligned The Two Vectors Are(Tests For Perpindicular etc...))
                dot = ball[n].velocity[0]*(normal_x) + ball[n].velocity[1]*(normal_y);

                ball[n].velocity[0] = ball[n].velocity[0] - 2 * dot * normal_x;
                ball[n].velocity[1] = ball[n].velocity[1] - 2 * dot * normal_y;
                
                # Perfect Elastic Bounce
                ball[n].pos[0] = pin[i].pos[0] + normal_x * (pin_radius + ball_radius + 0.01);
                ball[n].pos[1] = pin[i].pos[1] + normal_y * (pin_radius + ball_radius + 0.01);
                
                
                ball[n].velocity[0] *= bounce_damping; # Apply Bounce Energy Absorption X
                ball[n].velocity[1] *= bounce_damping; # Apply Bounce Energy Absorption Y



# Detect and Calculate Balls Colliding with the Floor and Ceiling
def floor_ceil_collision(floor_height,ceil_height):
    for n in range(len(ball)):
        if (ball[n].pos[1] < floor_height):
            ball[n].velocity[1] *= -1;
            ball[n].pos[1] = floor_height +ball_radius + 0.01;
            ball[n].velocity[0] *= bounce_damping;
            ball[n].velocity[1] *= bounce_damping;

        elif (ball[n].pos[1] > ceil_height):
            ball[n].velocity[1] *= -1;
            ball[n].pos[1] = ceil_height - ball_radius + 0.01;
            ball[n].velocity[0] *= bounce_damping;
            ball[n].velocity[1] *= bounce_damping;



# Detect and Calculate Collisions with walls
def wall_collisions(left,right):
    for n in range(len(ball)):
        if (ball[n].pos[0] < left):
            ball[n].velocity[0] *= -1;
            ball[n].velocity[0] *= bounce_damping;
            ball[n].velocity[1] *= bounce_damping;

        elif (ball[n].pos[0] > right):
            ball[n].velocity[0] *= -1;
            ball[n].velocity[0] *= bounce_damping;
            ball[n].velocity[1] *= bounce_damping;



# Apply Global Simulation Calculations
def global_simulations():
    for n in range(len(ball)):
        ball[n].velocity[0] *= air_damping;
        ball[n].velocity[1] *= air_damping;

        ball[n].velocity[1] += gravity;

        # Insert Velocity Clamping Here 


        ball[n].pos[0] += ball[n].velocity[0];
        ball[n].pos[1] += ball[n].velocity[1];




# Updates the Screen Pos of Each Ball
def sim_to_window():
    for n in range(len(ball)):
        if not ball[n].active:
            continue
        ball[n].window_pos[0] = (ball[n].pos[0] / sim_width) * window_width
        ball[n].window_pos[1] = window_height - ((ball[n].pos[1] / sim_height) * window_height)



# Per-Ball Simulation Calculation
def sim_operations():
    initialize_pins()
    initialize_balls()
# Simulation Loop
def simulation_loop(running):
    while running():
        start_time = time.time()

        sim_to_window()
        pin_window_pos()

        global_simulations()
        pin_collisions()
        floor_ceil_collision(0,sim_height)
        wall_collisions(0,sim_width)
        goal_side_collisions()

        elapsed = time.time() - start_time
        sleep_time = max(0, (1/sample_rate) - elapsed)
        time.sleep(sleep_time)



# Display Loop
def display_loop(running):
    pygame.init()
    screen = pygame.display.set_mode((int(window_width), int(window_height)))
    clock = pygame.time.Clock()

    while running():
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_state["value"] = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Only spawn a new ball if we haven't reached the max active amount
                if count_active_balls() < max_active_balls:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    sim_x = (mouse_x / window_width) * sim_width
                    sim_y = ((window_height - mouse_y) / window_height) * sim_height
                    new_ball = BallParameters([sim_x, sim_height], [0.0, 0.0], [0.0, 0.0], True)
                    new_ball.window_pos[0] = (sim_x / sim_width) * window_width
                    new_ball.window_pos[1] = window_height - ((sim_y / sim_height) * window_height)
                    ball.append(new_ball)


        for p in pin:
            pygame.draw.circle(screen, (255, 255, 255), (int(p.window_pos[0]), int(p.window_pos[1])), int(pin_radius * window_width / sim_width))
        for b in ball:
            if not b.active:
                continue
            pygame.draw.circle(screen, (255, 0, 0), (int(b.window_pos[0]), int(b.window_pos[1])), int(ball_radius * window_width / sim_width))

        for i in range(1, goal_count):
            divider_x = (i * goal_width / sim_width) * window_width
            pygame.draw.line(screen, divider_color, (divider_x, window_height), (divider_x, window_height - (goal_height / sim_height) * window_height), divider_width)

        pygame.display.flip()
        clock.tick(60)


## ____ Main Processing ____ ##

initialize_pins()
initialize_balls()
sim_to_window()
pin_window_pos()

running_state = {"value": True}

simulation_thread = threading.Thread(target=simulation_loop, args=(lambda: running_state["value"],))
simulation_thread.start()

display_loop(lambda: running_state["value"])
