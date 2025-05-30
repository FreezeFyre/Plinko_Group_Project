import math
from dataclasses import dataclass
from typing import List
import pygame
import time


aspect_ratio = [16,9];
window_width = 1920;
window_height = (window_width/aspect_ratio[0])*(aspect_ratio[1]);

sim_width = 100;
sim_width = 1000; ## In Meters
sim_height = (sim_width/aspect_ratio[0])*(aspect_ratio[1]);

pin_radius = .5;
pin_y_start = 40;
pin_increment = 5;
pin_x_count = 20;
pin_y_count = 15;
x_start = 5;
pin_radius = .5; ## Meters

max_velocity = 300.0;

gravity = -9.8;
gravity = -9.8; ## In Meters
air_damping = .99;
loop_thresh = 100;

ball_radius = .5;
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



@@ -39,19 +38,28 @@ ball: List[BallParameters] = []
@dataclass
class PinParameters:
    pos: List[float]
    window_pos: List[int]
pin: List[PinParameters] = []


# Ball Creation Logic Goes In Here
# Initialize Balls
def initialize_balls():
    ball.append(BallParameters([0.0 , 0.0],[0.0 , 0.0]))
    ball.append(BallParameters([0.0 , 0.0],[0.0 , 0.0],[0,0]))


# Pin Creation Logic Goes Here
# Initialize Pins
def initialize_pins():
    pin.append(PinParameters([0.0 , 0.0]))
    pin.append(PinParameters([50 , 50],[0,0]))



# Convert simulation pos to window pos and add it to each pin
def pin_window_pos():
        for n in range(len(pin)):
            pin[n].window_pos[0] = (pin[n].pos[0] / sim_width) * window_width
            pin[n].window_pos[1] = window_height - ((pin[n].pos[1] / sim_height) * window_height)





@@ -136,31 +144,53 @@ def global_simulations():



# Return the Screen x and y of Ball n
def ball_screen_pos(n):
    screen_pos = [0,0]
    screen_pos[0] = (ball[n].pos[0] / sim_width) * window_width
    screen_pos[1] = (ball[n].pos[1] / sim_height) * window_height

    return screen_pos
# Updates the Screen Pos of Each Ball
def sim_to_window():
    for n in range(len(ball)):
        ball[n].window_pos[0] = (ball[n].pos[0] / sim_width) * window_width
        ball[n].window_pos[1] = window_height - ((ball[n].pos[1] / sim_height) * window_height)



# Per-Ball Simulation Calculation
def sim_operations():
    initialize_pins()
    initialize_balls()
# Simulation Loop
def simulation_loop(running): ## If the app is runnning updates every ball position and velocity every "sample_rate" of a second
    while running == True: ## Execute Every "sample_rate" of a second
        start_time = time.time()

    for n in range(len(ball)):
        ball_screen_pos(n)

    global_simulations()
    pin_collisions()
    floor_ceil_collision(0,sim_height)
    wall_collisions(0,sim_width)
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

for n in range(loop_thresh):
    sim_operations()
initialize_pins() ## Initialize the position of each pin
initialize_balls() ## Initialize the position of each Ball and its starting velocity
pin_window_pos()

running = True
simulation_loop(running)
display_loop(running)
