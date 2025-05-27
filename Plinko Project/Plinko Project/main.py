import math
from dataclasses import dataclass
from typing import List


aspect_ratio = [16,9];
window_width = 1920;
window_height = (window_width/aspect_ratio[0])*(aspect_ratio[1]);

sim_width = 100;
sim_height = (sim_width/aspect_ratio[0])*(aspect_ratio[1]);

pin_radius = .5;
pin_y_start = 40;
pin_increment = 5;
pin_x_count = 20;
pin_y_count = 15;
x_start = 5;

max_velocity = 300.0;

gravity = -9.8;
air_damping = .99;
loop_thresh = 100;

ball_radius = .5;
bounce_damping = .85; # Range 0 to 1


# Define Ball Parameters
@dataclass
class BallParameters:
    pos: List[float]
    velocity: List[float]
ball: List[BallParameters] = []


# Define Pin Parameters
@dataclass
class PinParameters:
    pos: List[float]
pin: List[PinParameters] = []


# Ball Creation Logic Goes In Here
# Initialize Balls
def initialize_balls():
    ball.append(BallParameters([0.0 , 0.0],[0.0 , 0.0]))


# Pin Creation Logic Goes Here
# Initialize Pins
def initialize_pins():
    pin.append(PinParameters([0.0 , 0.0]))



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



# Return the Screen x and y of Ball n
def ball_screen_pos(n):
    screen_pos = [0,0]
    screen_pos[0] = (ball[n].pos[0] / sim_width) * window_width
    screen_pos[1] = (ball[n].pos[1] / sim_height) * window_height

    return screen_pos



# Per-Ball Simulation Calculation
def sim_operations():
    initialize_pins()
    initialize_balls()

    for n in range(len(ball)):
        ball_screen_pos(n)

    global_simulations()
    pin_collisions()
    floor_ceil_collision(0,sim_height)
    wall_collisions(0,sim_width)


## ____ Main Processing ____ ##

for n in range(loop_thresh):
    sim_operations()