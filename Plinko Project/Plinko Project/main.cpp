//
//  main.cpp
//  Plinko Project
//
//  Created by Luke Raykovitz on 5/8/25.
//

#include <iostream>
#include <vector>
#include <unordered_map>



// Declare Ball Parameters
struct ball_paramaters {
    int id; // Incase Multiple Balls
    std::vector<float> pos; // Balls current x,y
    std::vector<float> velocity; // Balls current velocity vector x,y
    float bounce_damp; // Energy loss onn bounce, 1 = no loss, 0 = total loss
};
// Set Paramaters for the ball and bind to "ball" name
ball_paramaters ball = {0,{0,10},{1,0},0.8};



// Declare Globale Paramaters
struct global_paramaters {
    float gravity; // Gravity Force, "-" = down
    float air_damping; // Energy loss every sample, 1 = no loss, 0 = total loss
    int substeps; // Unused
    int loop_thresh; // Max Amount of allowed samples
};
// Set Global Paramaters and bind to "global" name
global_paramaters global = {-.098,.99,4,100};



void floor_collision(int floor_height) {
    // Detect Collision with floor
    if (ball.pos[1] < floor_height) {
        ball.velocity[1] *= -1; // Reflect Vertically
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



void sim_operations() {
    ball.velocity[0] *= global.air_damping;
    ball.velocity[1] *= global.air_damping;

    
    ball.velocity[1] += global.gravity;
    ball.pos[0] += ball.velocity[0];
    ball.pos[1] += ball.velocity[1];
    
    
    
    floor_collision(0);
    
    wall_collision(-10, 10);
}



int main() {


    
    int count = 0;
    while (count <= global.loop_thresh-1) {
        std::cout << count << "\t | \t";
        std::cout << "Position: (" << ball.pos[0] << ", " << ball.pos[1] << ") " << "Velocity: (" << ball.velocity[0] << ", " << ball.velocity[1] << ")" << std::endl;

        sim_operations();

        count += 1;
    }
        
    return 0;
}
