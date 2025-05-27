import math
from dataclasses import dataclass
from typing import List
import pygame
import time


aspect_ratio = [16,9];
window_width = 1920;
window_height = (window_width/aspect_ratio[0])*(aspect_ratio[1]);

sim_width = 1000; ## In Meters
sim_height = (sim_width/aspect_ratio[0])*(aspect_ratio[1]);

pin_radius = .5; ## Meters

max_velocity = 300.0;

gravity = -9.8; ## In Meters
air_damping = .99;

ball_radius = .5; ## In Meters
bounce_damping = .85; # Range 0 to 1

sample_rate = 60; ## In Herz


# Define Ball Parameters
@dataclass
class BallParameters:
    pos: List[float]
    velocity: List[float]
    window_pos: List[int]
ball: List[BallParameters] = []


# Define Pin Parameters
@dataclass
class PinParameters:
    pos: List[float]
    window_pos: List[int]
pin: List[PinParameters] = []


# Ball Creation Logic Goes In Here
# Initialize Balls
def initialize_balls():
    ball.append(BallParameters([0.0 , 0.0],[0.0 , 0.0],[0,0]))


# Pin Creation Logic Goes Here
# Initialize Pins
def initialize_pins():
    pin.append(PinParameters([50 , 50],[0,0]))



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
        ball[n].window_pos[0] = (ball[n].pos[0] / sim_width) * window_width
        ball[n].window_pos[1] = window_height - ((ball[n].pos[1] / sim_height) * window_height)



# Simulation Loop
def simulation_loop(running): ## If the app is runnning updates every ball position and velocity every "sample_rate" of a second
    while running == True: ## Execute Every "sample_rate" of a second
        start_time = time.time()


        sim_to_window() ## Update the Screen Position Array For each pin and ball

        global_simulations() ## Apply Gravity and Air damping to every ball
        pin_collisions() ## Check if a ball collides with a pin if one does apply bouncing to it
        floor_ceil_collision(0,sim_height)
        wall_collisions(0,sim_width)


        # Sleep to maintain 60Hz
        elapsed = time.time() - start_time
        sleep_time = max(0, (1/sample_rate) - elapsed)
        time.sleep(sleep_time)



# Display Loop
def display_loop(running): ## Creates a window, updates every frame, every frame calls pin and ball positions from array

    while running == True:
        for n in range(len(pin)):
            print(pin[n].window_pos[0], pin[n].window_pos[1])
        for n in range(len(ball)):
            print(ball[n].window_pos[0], ball[n].window_pos[1])


## ____ Main Processing ____ ##

initialize_pins() ## Initialize the position of each pin
initialize_balls() ## Initialize the position of each Ball and its starting velocity
pin_window_pos()

running = True
simulation_loop(running)
display_loop(running)

