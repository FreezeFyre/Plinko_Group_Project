//
//  main.cpp
//  Plinko Project
//
//  Created by Luke Raykovitz on 5/8/25.
//

#include <iostream>
#include <vector>
#include <unordered_map>


struct ball_paramaters {
    int id;
    std::vector<float> pos;
    std::vector<float> velocity;
    int mass;
    float bounce_damp;
};

ball_paramaters ball = {0,{0,10},{1,0},0,0.8};

struct global_paramaters {
    float gravity;
    float air_damping;
    int substeps;
    int loop_thresh;
};

global_paramaters global = {-.098,.99,4,100};



void floor_collision(int floor_height) {
    if (ball.pos[1] < floor_height) {
        ball.pos[1] = floor_height;
        ball.velocity[1] *= -1;
        ball.velocity[0] *= ball.bounce_damp;
        ball.velocity[1] *= ball.bounce_damp;
    }
}



void wall_collision(int left, int right) {
    if (ball.pos[0] < left) {
        ball.velocity[0] *= -1;
        ball.velocity[0] *= ball.bounce_damp;
        ball.velocity[1] *= ball.bounce_damp;
    }
    
    else if (ball.pos[0] > right){
        ball.velocity[0] *= -1;
        ball.velocity[0] *= ball.bounce_damp;
        ball.velocity[1] *= ball.bounce_damp;
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
