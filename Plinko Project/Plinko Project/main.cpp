//
//  main.cpp
//  Plinko Project
//
//  Created by Luke Raykovitz on 5/8/25.
//

#include <iostream>
#include <vector>
#include <unordered_map>
#include <cmath>
#include <cstdlib> // for system()


std::vector<int> aspect_ratio = {16,9};
int window_width = 1920;
int window_height = (window_width/aspect_ratio[0])*(aspect_ratio[1]);

float sim_width = 100;
float sim_height = (sim_width/aspect_ratio[0])*(aspect_ratio[1]);



// Declare Ball Parameters
struct ball_parameters {
    std::vector<float> pos; // Balls current x,y
    std::vector<float> velocity; // Balls current velocity vector x,y
    float bounce_damp; // Energy loss on bounce, 1 = no loss, 0 = total loss
    float rad;
};
// Set parameters for the ball and bind to "ball" name
ball_parameters ball = {{sim_width/2,sim_height},{0.05,0},.8,0.5};

std::unordered_map<int, ball_parameters> balls;
void initialize_balls() {
    balls[0] = {{0,0},{0,0},1,.5};
}

// Declare Globale parameters
struct global_parameters {
    float gravity; // Gravity Force, "-" = down
    float air_damping; // Energy loss every sample, 1 = no loss, 0 = total loss
    int substeps; // Unused
    int loop_thresh; // Max Amount of allowed samples
};
// Set Global parameters and bind to "global" name
global_parameters global = {-9.8,.99,4,100};



struct pin_parameters {
    std::vector<float> pos;
    float rad;
};



std::unordered_map<int, pin_parameters> pin;
void initialize_pins() {
    pin[0] = {{0,4},0.5};
    pin[1] = {{2,2},0.5};
    pin[2] = {{-2,2},0.5};
}



void pin_solver() {
    int i = 0;
    while (i < pin.size()) { // Loop Through Each Pin
        float d = sqrt((pow((ball.pos[0]-pin[i].pos[0]), 2)) + (pow((ball.pos[1] - pin[i].pos[1]), 2))); // Find Distance Between Pin i and the Ball
        
        if (d < pin[i].rad + ball.rad) { // Detect If Ball Collides With Pin i
            std::cout << "X"; // Visulize Collision Detection
            
            float x_direction = ball.pos[0] - pin[i].pos[0]; // Vector Pointing From the Pin to the Ball
            float y_direction = ball.pos[1] - pin[i].pos[1]; // Vector Pointing From the Pin to the Ball
            
            float normal_x = x_direction / d; // Normalize the Direction Vector
            float normal_y = y_direction / d; // Normalize the Direction Vector
                        
            float dot = ball.velocity[0]*(normal_x * -1) + ball.velocity[1]*(normal_y * -1); // Dot Product

            ball.velocity[0] = ball.velocity[0] - 2 * dot * normal_x; // Reflection Velocity
            ball.velocity[1] = ball.velocity[1] - 2 * dot * normal_y; // Reflection Velocity
            
            
            ball.pos[0] = pin[i].pos[0] + x_direction;
            ball.pos[1] = pin[i].pos[1] + y_direction;
            
            ball.velocity[0] *= ball.bounce_damp; // Dampening
            ball.velocity[1] *= ball.bounce_damp; // Dampening
        }
        
        i += 1;
    }
}



void floor_ceil_collision(int floor_height, int ceil_height) {
    // Detect Collision with floor
    if (ball.pos[1] < floor_height) {
        ball.velocity[1] *= -1; // Reflect Vertically
        ball.pos[1] = floor_height + .01;
        ball.velocity[0] *= ball.bounce_damp; // Dampening
        ball.velocity[1] *= ball.bounce_damp; // Dampening
    }
    
    
    else if (ball.pos[1] > ceil_height) {
        ball.velocity[1] *= -1; // Reflect Vertically
        ball.pos[1] = ceil_height + .01;
        ball.velocity[0] *= ball.bounce_damp; // Dampening
        ball.velocity[1] *= ball.bounce_damp; // Dampening
    }
}


// Wall Collisions
void wall_collision(int left, int right) {
    
    // Detect Collision with left wall
    if (ball.pos[0] < left) {
        ball.velocity[0] *= -1; // Reflect Horizontaly
        ball.velocity[0] *= ball.bounce_damp; // Dampening
        ball.velocity[1] *= ball.bounce_damp; // Dampening
    }
    
    // Detect Collision with right
    else if (ball.pos[0] > right){
        ball.velocity[0] *= -1; // Reflect Horizontaly
        ball.velocity[0] *= ball.bounce_damp; // Dampening
        ball.velocity[1] *= ball.bounce_damp; // Dampening
    }
}



std::vector<float> sim_operations() {
    ball.velocity[0] *= global.air_damping;
    ball.velocity[1] *= global.air_damping;

    
    ball.velocity[1] += global.gravity;
    ball.pos[0] += ball.velocity[0];
    ball.pos[1] += ball.velocity[1];
    
    
    
    floor_ceil_collision(0, sim_height);
    
    wall_collision(0, sim_width);
    
    pin_solver();
    std::vector<float> output = {((ball.pos[0]/sim_width)*window_width),((ball.pos[1]/sim_height)*window_height)};
    
    return output;
}



int main() {
    initialize_pins();
    
    int count = 0;
    while (count <= global.loop_thresh-1) {
        std::vector<float> screen_pos = sim_operations();
        std::cout << "\t | \t";
        std::cout << "Position: (" << screen_pos[0] << ", " << screen_pos[1] << ") "
                  << "Velocity: (" << ball.velocity[0] << ", " << ball.velocity[1] << ")" << std::endl;


        count += 1;
    }
        
    return 0;
}
