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
std::unordered_map<int, ball_parameters> ball;
void initialize_balls() {
    ball[0] = {{0,0},{0,0},1,.5};
}


float gravity = -9.8; // Gravity Force, "-" = down
float air_damping = .99; // Energy loss every sample, 1 = no loss, 0 = total loss
int substeps = 100; // Unused
int loop_thresh = 100; // Max Amount of allowed samples



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


void pin_collisions() {
    int n = 0;
    while (n < ball.size()) {
        int i = 0;
        while (i < pin.size()) {
            float d = sqrt((pow((ball[n].pos[0] - pin[i].pos[0]), 2)) + (pow((ball[n].pos[1] - pin[i].pos[1]), 2)));
            
            if (d < pin[i].rad + ball[n].rad) { // Detect If Ball Collides With Pin i
                std::cout << "X"; // Visulize Collision Detection
                
                float x_direction = ball[n].pos[0] - pin[i].pos[0]; // Vector Pointing From the Pin to the Ball
                float y_direction = ball[n].pos[1] - pin[i].pos[1]; // Vector Pointing From the Pin to the Ball
                
                float normal_x = x_direction / d; // Normalize the Direction Vector
                float normal_y = y_direction / d; // Normalize the Direction Vector
                            
                float dot = ball[n].velocity[0]*(normal_x * -1) + ball[n].velocity[1]*(normal_y * -1); // Dot Product

                ball[n].velocity[0] = ball[n].velocity[0] - 2 * dot * normal_x; // Reflection Velocity
                ball[n].velocity[1] = ball[n].velocity[1] - 2 * dot * normal_y; // Reflection Velocity
                
                
                ball[n].pos[0] = pin[i].pos[0] + x_direction;
                ball[n].pos[1] = pin[i].pos[1] + y_direction;
                
                ball[n].velocity[0] *= ball[n].bounce_damp; // Dampening
                ball[n].velocity[1] *= ball[n].bounce_damp; // Dampening
            }
            
            i += 1;
        }
        
        n += 1;
    }
}



void floor_ceil_collision(int floor_height, int ceil_height) {
    int n = 0;
    while (n < ball.size()) {
        // Detect Collision with floor
        if (ball[n].pos[1] < floor_height) {
            ball[n].velocity[1] *= -1; // Reflect Vertically
            ball[n].pos[1] = floor_height + .01;
            ball[n].velocity[0] *= ball[n].bounce_damp; // Dampening
            ball[n].velocity[1] *= ball[n].bounce_damp; // Dampening
        }
        
        
        else if (ball[n].pos[1] > ceil_height) {
            ball[n].velocity[1] *= -1; // Reflect Vertically
            ball[n].pos[1] = ceil_height + .01;
            ball[n].velocity[0] *= ball[n].bounce_damp; // Dampening
            ball[n].velocity[1] *= ball[n].bounce_damp; // Dampening
        }
        
        n += 1;
    }
}


// Wall Collisions
void wall_collision(int left, int right) {
    int n = 0;
    while (n < ball.size()) {
        // Detect Collision with left wall
        if (ball[n].pos[0] < left) {
            ball[n].velocity[0] *= -1; // Reflect Horizontaly
            ball[n].velocity[0] *= ball[n].bounce_damp; // Dampening
            ball[n].velocity[1] *= ball[n].bounce_damp; // Dampening
        }
        
        // Detect Collision with right
        else if (ball[n].pos[0] > right){
            ball[n].velocity[0] *= -1; // Reflect Horizontaly
            ball[n].velocity[0] *= ball[n].bounce_damp; // Dampening
            ball[n].velocity[1] *= ball[n].bounce_damp; // Dampening
        }
        
        n += 1;
    }
}



std::vector<float> sim_operations() {
    std::vector<float> output; // Declare outside the loop
    
    int n = 0;
    while (n < ball.size()) {
        ball[n].velocity[0] *= air_damping;
        ball[n].velocity[1] *= air_damping;

        ball[n].velocity[1] += gravity;
        ball[n].pos[0] += ball[n].velocity[0];
        ball[n].pos[1] += ball[n].velocity[1];

        // Add each ball's transformed position to the output vector
        output.push_back((ball[n].pos[0] / sim_width) * window_width);
        output.push_back((ball[n].pos[1] / sim_height) * window_height);

        ++n;
    }

    floor_ceil_collision(0, sim_height);
    wall_collision(0, sim_width);
    pin_collisions();

    return output;
}




int main() {
    initialize_pins();
    
    int count = 0;
    while (count <= loop_thresh-1) {
        int n = 0;
        while (n < ball.size()) {
            std::vector<float> screen_pos = sim_operations();
            std::cout << "\t | \t";
            std::cout << "Position: (" << screen_pos[0] << ", " << screen_pos[1] << ") "
                      << "Velocity: (" << ball[n].velocity[0] << ", " << ball[n].velocity[1] << ")" << std::endl;

            n += 1;
        }
        count += 1;
    }
        
    return 0;
}
