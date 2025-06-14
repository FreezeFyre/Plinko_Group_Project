"""Plinko simulation built with pygame.

This module contains a very small physics sandbox that mimics a Plinko
board.  Balls fall through a grid of pins and land in goal slots at the
bottom of the screen.  The simulation runs on a background thread while a
display loop renders the state to a resizable window.
"""

import math
from dataclasses import dataclass
from typing import List, Self
import pygame

pygame.init()
import time
import threading

# Font used for the on-screen score display
score_font = pygame.font.SysFont("Arial", 30)

# -------------------------------------------------------------
# Window and simulation dimensions
# -------------------------------------------------------------
# Aspect ratio of the game window (width : height).  We use a tall 9:16
# ratio so the playing field is vertical.
aspect_ratio = [9, 16]

# Initial window dimensions.  The height is set to the full vertical
# resolution of the user's monitor (1050px) and the width is derived from
# the aspect ratio.
window_height = 1050
window_width = (window_height * aspect_ratio[0]) / aspect_ratio[1]

sim_width = 100  # Simulation width in meters
sim_height = (sim_width / aspect_ratio[0]) * aspect_ratio[1]

radius = 1.5

pin_radius = radius # Meters

max_velocity = 300.0

sample_rate = 128 # In Herz

timeout = sample_rate * 30 # in seconds

dt = 1/sample_rate
gravity = 25*  9.8 # In Meters
air_damping = .9999 ** dt

ball_radius = radius # In Meters
bounce_damping = .9 # Range 0 to 1

max_active_balls = 16

goal_count = 10

if goal_count % 2 == 0:
    goal_count += 1

goal_width = sim_width/goal_count
divider_color = (94, 94, 96)
divider_width = 4 # Pixel
goal_height = (sim_height/100) * 5 # Percent of Screen Height

# Shadow settings
shadow_offset = 4  # pixel offset for drop shadows
shadow_color = (0, 0, 0, 120)  # semi-transparent black

epsilon = 1 / 10**10

rows = 9
y_start = sim_height * 0.10

score = 0

min_score = 10  # Minimum score attainable from a goal
# Scale by 10 to the power of 1 + i/5 for scoring falloff

debug_mode = {"value": False}


# Helper to count currently active balls
def count_active_balls() -> int:
    """Return the number of balls currently in play."""
    return sum(1 for b in ball if b.active)



# Define Ball Parameters
@dataclass
class BallParameters:
    """Container for all mutable ball state used by the simulation."""

    pos: List[float]
    velocity: List[float]
    window_pos: List[float]
    active: bool  # Whether the ball is currently active
    time: int  # Number of simulation steps the ball has existed
ball: List[BallParameters] = []


# Define Pin Parameters
@dataclass
class PinParameters:
    """Simple container describing the location of a single pin."""

    pos: List[float]
    window_pos: List[float]
pin: List[PinParameters] = []


# Ball Creation Logic Goes In Here
def initialize_balls() -> None:
    """Create the initial inactive ball used as a template."""

    ball.append(BallParameters([0.0, 0.0], [0.0, 0.0], [0.0, 0.0], False, 0))



# Pin Creation Logic Goes Here
def initialize_pins() -> None:
    """Populate the board with a triangular grid of pins."""

    global pin

    # Safe spacing to force collisions
    S = 3 * ball_radius + 3 * pin_radius - epsilon
    V = S * math.sin(math.radians(60))  # vertical spacing

    # Top row: centered, odd number of pins
    max_pins = int(sim_width // S)
    if max_pins % 2 == 0:
        max_pins -= 1
    half = max_pins // 2

    for row in range(rows):
        y = y_start + row * V
        stagger = (row % 2 == 1)

        if stagger:
            # Add 1 extra pin on each side
            i_range = range(-half - 1, half + 2)
        else:
            i_range = range(-half, half + 1)

        for i in i_range:
            x = (sim_width / 2) + i * S
            if stagger:
                x += S / 2

            if 0 <= x <= sim_width:
                pin.append(PinParameters([x, y], [0.0, 0.0]))



def ball_timeout() -> None:
    """Deactivate balls that have existed longer than the timeout."""

    for n in range(len(ball)):
        if not ball[n].active:
            continue

        ball[n].time += 1

        if ball[n].time >= timeout:
            ball[n].active = False


# Convert simulation pos to window pos and add it to each pin
def pin_window_pos() -> None:
    """Update the cached screen positions for each pin."""

    for n in range(len(pin)):
        pin[n].window_pos[0] = (pin[n].pos[0] / sim_width) * window_width
        pin[n].window_pos[1] = window_height - ((pin[n].pos[1] / sim_height) * window_height)



# Detect and Calculate Balls Colliding with Pins
def pin_collisions() -> None:
    """Handle collisions between balls and pins."""
    for n in range(len(ball)):
        if not ball[n].active:
            continue
        for i in range(len(pin)):
            d = math.sqrt((ball[n].pos[0] - pin[i].pos[0])**2 + (ball[n].pos[1] - pin[i].pos[1])**2)

            if d < (pin_radius + ball_radius):
                x_direction = ball[n].pos[0] - pin[i].pos[0]
                y_direction = ball[n].pos[1] - pin[i].pos[1]

                normal_x = x_direction / d
                normal_y = y_direction / d
                dot = ball[n].velocity[0]*(normal_x) + ball[n].velocity[1]*(normal_y)

                ball[n].velocity[0] = ball[n].velocity[0] - 2 * dot * normal_x
                ball[n].velocity[1] = ball[n].velocity[1] - 2 * dot * normal_y

                ball[n].pos[0] = pin[i].pos[0] + normal_x * (pin_radius + ball_radius + epsilon)
                ball[n].pos[1] = pin[i].pos[1] + normal_y * (pin_radius + ball_radius + epsilon)

                ball[n].velocity[0] *= bounce_damping
                ball[n].velocity[1] *= bounce_damping



# Ball Collisions
def ball_collisions() -> None:
    """Handle collisions between balls themselves."""
    for n in range(len(ball)):
        if not ball[n].active:
            continue
        for i in range(len(ball)):
            if i == n:
                continue
            d = math.sqrt((ball[n].pos[0] - ball[i].pos[0])**2 + (ball[n].pos[1] - ball[i].pos[1])**2)
            if d == 0:
                continue

            if d < (ball_radius * 2):
                x_direction = ball[n].pos[0] - ball[i].pos[0]
                y_direction = ball[n].pos[1] - ball[i].pos[1]

                normal_x = x_direction / d
                normal_y = y_direction / d
                dot = ball[n].velocity[0]*(normal_x) + ball[n].velocity[1]*(normal_y)

                ball[n].velocity[0] = ball[n].velocity[0] - 2 * dot * normal_x
                ball[n].velocity[1] = ball[n].velocity[1] - 2 * dot * normal_y

                ball[n].pos[0] = ball[i].pos[0] + normal_x * ((ball_radius * 2) + epsilon)
                ball[n].pos[1] = ball[i].pos[1] + normal_y * ((ball_radius * 2) + epsilon)

                ball[n].velocity[0] *= bounce_damping
                ball[n].velocity[1] *= bounce_damping


# Detect and Calculate Balls Colliding with the Floor and Ceiling
def floor_ceil_collision(floor_height: float, ceil_height: float) -> None:
    """Handle collisions with the floor and ceiling and update score."""
    for n in range(len(ball)):
        if not ball[n].active:
            continue
        if ball[n].pos[1] < floor_height + ball_radius:
            ball[n].active = False

            # --- scoring logic ---
            global score

            goal_index = int(ball[n].pos[0] // goal_width)
            goal_index = max(0, min(goal_count - 1, goal_index))  # clamp

            center_index = goal_count // 2
            distance_from_center = abs(goal_index - center_index)

            points = round(1000 / (10 ** (distance_from_center / 5)))

            score += points

        elif (ball[n].pos[1] > ceil_height):
            ball[n].velocity[1] *= -1
            ball[n].pos[1] = ceil_height - ball_radius - 0.01
            ball[n].velocity[0] *= bounce_damping
            ball[n].velocity[1] *= bounce_damping



# Detect and Calculate Collisions with walls
def wall_collisions(left: float, right: float) -> None:
    """Handle collisions of balls with the side walls."""
    for n in range(len(ball)):
        if not ball[n].active:
            continue
        if (ball[n].pos[0] < left):
            ball[n].velocity[0] *= -1
            ball[n].pos[0] = left + ball_radius + 0.01
            ball[n].velocity[0] *= bounce_damping
            ball[n].velocity[1] *= bounce_damping

        elif (ball[n].pos[0] > right):
            ball[n].velocity[0] *= -1
            ball[n].pos[0] = right - ball_radius - 0.01
            ball[n].velocity[0] *= bounce_damping
            ball[n].velocity[1] *= bounce_damping



# Apply Global Simulation Calculations
def global_simulations() -> None:
    """Apply gravity, damping and integration for all active balls."""
    for n in range(len(ball)):
        if not ball[n].active:
            continue
        ball[n].velocity[0] *= air_damping
        ball[n].velocity[1] *= air_damping

        ball[n].velocity[1] -= gravity * dt

        speed = math.sqrt(ball[n].velocity[0]**2 + ball[n].velocity[1]**2)
        if speed > max_velocity:
            scale = max_velocity / speed
            ball[n].velocity[0] *= scale
            ball[n].velocity[1] *= scale

        ball[n].pos[0] += ball[n].velocity[0] * dt
        ball[n].pos[1] += ball[n].velocity[1] * dt




# Goal Collisions
def goal_side_collisions() -> None:
    """Handle collisions with goal dividers at the bottom of the board."""
    for n in range(len(ball)):
        if not ball[n].active:
            continue
        if ball[n].pos[1] > goal_height:
            continue  # Only check when inside the goal zone

        for i in range(1, goal_count):  # skip 0 to avoid left wall
            divider_x = i * goal_width
            dx = ball[n].pos[0] - divider_x
            if abs(dx) < ball_radius:
                # Collided with vertical divider
                if dx < 0:
                    ball[n].pos[0] = divider_x - ball_radius - 0.01
                else:
                    ball[n].pos[0] = divider_x + ball_radius + 0.01

                ball[n].velocity[0] *= -1
                ball[n].velocity[0] *= bounce_damping
                ball[n].velocity[1] *= bounce_damping





# Updates the Screen Pos of Each Ball
def sim_to_window() -> None:
    """Convert simulation coordinates to window coordinates."""

    for n in range(len(ball)):
        if not ball[n].active:
            continue
        ball[n].window_pos[0] = (ball[n].pos[0] / sim_width) * window_width
        ball[n].window_pos[1] = window_height - ((ball[n].pos[1] / sim_height) * window_height)



# Simulation Loop
def simulation_loop(running) -> None:
    """Background thread that updates physics state."""
    while running():
        start_time = time.time()

        sim_to_window()
        pin_window_pos()

        ball_timeout()
        global_simulations()
        pin_collisions()
        ball_collisions()
        floor_ceil_collision(0,sim_height)
        wall_collisions(0,sim_width)
        goal_side_collisions()

        elapsed = time.time() - start_time
        sleep_time = max(0, (1/sample_rate) - elapsed)
        time.sleep(sleep_time)



# Display Loop
def display_loop(running) -> None:
    """Main thread loop responsible for rendering and user input."""
    pygame.init()
    global window_width, window_height
    screen = pygame.display.set_mode(
        (int(window_width), int(window_height)), pygame.RESIZABLE
    )
    clock = pygame.time.Clock()

    while running():
        screen.fill((31, 31, 36))
        shadow_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_state["value"] = False
            elif event.type == pygame.VIDEORESIZE:
                # keep the aspect ratio based on the new height so the
                # window remains vertical
                window_height = event.h
                window_width = (window_height * aspect_ratio[0]) / aspect_ratio[1]
                screen = pygame.display.set_mode(
                    (int(window_width), int(window_height)), pygame.RESIZABLE
                )

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

				# Check if click is in top-right "Debug" button
                button_width = 60
                button_height = 25
                if (window_width - button_width - 10 <= mouse_x <= window_width - 10 and
				    10 <= mouse_y <= 10 + button_height):
                    debug_mode["value"] = not debug_mode["value"]

				# Spawn new ball if allowed
                elif count_active_balls() < max_active_balls:
                    sim_x = (mouse_x / window_width) * sim_width
                    sim_y = ((window_height - mouse_y) / window_height) * sim_height
                    for b in ball:
                        if not b.active:
                            b.pos = [sim_x, sim_height]
                            b.velocity = [0.0, 0.0]
                            b.window_pos = [0.0, 0.0]
                            b.active = True
                            b.time = 0
                            break
                    else:
                        if len(ball) < max_active_balls:
                            new_ball = BallParameters([sim_x, sim_height], [0.0, 0.0], [0.0, 0.0], True, 0)
                            ball.append(new_ball)



        # Draw shadows first
        for p in pin:
            pygame.draw.circle(
                shadow_surface,
                shadow_color,
                (
                    int(p.window_pos[0]),
                    int(p.window_pos[1]) + shadow_offset,
                ),
                int(pin_radius * window_width / sim_width),
            )
        for b in ball:
            if not b.active:
                continue
            pygame.draw.circle(
                shadow_surface,
                shadow_color,
                (
                    int(b.window_pos[0]),
                    int(b.window_pos[1]) + shadow_offset,
                ),
                int(ball_radius * window_width / sim_width),
            )

        screen.blit(shadow_surface, (0, 0))

        # Draw actual objects over shadows
        for p in pin:
            pygame.draw.circle(
                screen,
                (94, 94, 96),
                (int(p.window_pos[0]), int(p.window_pos[1])),
                int(pin_radius * window_width / sim_width),
            )
        for b in ball:
            if not b.active:
                continue
            pygame.draw.circle(
                screen,
                (196, 232, 232),
                (int(b.window_pos[0]), int(b.window_pos[1])),
                int(ball_radius * window_width / sim_width),
            )
        

        for i in range(1, goal_count):
            divider_x = (i * goal_width / sim_width) * window_width
            pygame.draw.line(screen, divider_color, (divider_x, window_height), (divider_x, window_height - (goal_height / sim_height) * window_height), divider_width)

        # --- score display ---
        # fancy lil shadow
        shadow = score_font.render(f"Score: {score}", True, (159, 159, 161))
        screen.blit(shadow, (12, 12))  

        score_text = score_font.render(f"Score: {score}", True, (152, 195, 245))  # text color, i cant find a good color so idk change it if u want
        screen.blit(score_text, (10, 10))  # position on screen

			# --- Draw Debug Toggle Button ---
        button_width = 60
        button_height = 25
        button_rect = pygame.Rect(window_width - button_width - 10, 10, button_width, button_height)
        pygame.draw.rect(screen, (50, 50, 50), button_rect)
        pygame.draw.rect(screen, (200, 200, 200), button_rect, 2)

        button_font = pygame.font.SysFont(None, 20)
        label = "Debug" if not debug_mode["value"] else "Hide"
        label_surface = button_font.render(label, True, (255, 255, 255))
        label_rect = label_surface.get_rect(center=button_rect.center)
        screen.blit(label_surface, label_rect)

			# --- Display debug info if enabled ---
        if debug_mode["value"]:
            font = pygame.font.SysFont(None, 18)
            margin = 10
            line_height = 18
            lines = []

            for i, b in enumerate(ball):
                if b.active:
                    pos_text = f"{i}: ({b.pos[0]:.5f}, {b.pos[1]:.5f})"
                    lines.append(pos_text)

                    velocity_scale = 0.1  # tuning value for how long lines appear
                    vx = b.velocity[0] * (window_width / sim_width) * velocity_scale
                    vy = -b.velocity[1] * (window_height / sim_height) * velocity_scale  # flip Y for screen space

                    start_pos = (int(b.window_pos[0]), int(b.window_pos[1]))
                    end_pos = (int(b.window_pos[0] + vx), int(b.window_pos[1] + vy))
                    pygame.draw.line(screen, (0, 255, 0), start_pos, end_pos, 2)

            for i, line in enumerate(lines):
                text_surface = font.render(line, True, (200, 200, 200))
                text_rect = text_surface.get_rect(topright=(window_width - margin, margin + (i + 3) * line_height))
                screen.blit(text_surface, text_rect)


        pygame.display.flip()
        clock.tick(60)


# ____ Main Processing ____ #
# Set up the simulation state and start the worker threads.

initialize_pins()
initialize_balls()
sim_to_window()
pin_window_pos()

running_state = {"value": True}

simulation_thread = threading.Thread(target=simulation_loop, args=(lambda: running_state["value"],))
simulation_thread.start()

display_loop(lambda: running_state["value"])
