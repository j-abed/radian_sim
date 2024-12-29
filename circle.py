import pygame
import math
import random
import psutil
import time
from collections import Counter
import timeit

# Initialize Pygame
pygame.init()

# Define the screen dimensions and create a window
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Set the title of the window
pygame.display.set_caption("Rotating Circle Simulation")

# Define colors
BLACK = (0, 0, 0)
BALL_COLORS = [
    (231, 76, 60), (46, 204, 113), (52, 152, 219), (241, 196, 15),
    (155, 89, 182), (230, 126, 34), (236, 240, 241), (149, 165, 166),
    (243, 156, 18), (44, 62, 80), (192, 57, 43), (39, 174, 96),
    (41, 128, 185), (142, 68, 173), (127, 140, 141), (22, 160, 133),
    (255, 195, 0), (255, 87, 51), (156, 39, 176), (3, 169, 244),
    (76, 175, 80), (96, 125, 139), (233, 30, 99), (103, 58, 183),
    (158, 158, 158), (255, 235, 59), (0, 150, 136), (121, 85, 72),
    (244, 67, 54), (255, 255, 255), (0, 188, 212), (76, 175, 80)
]

# Circle parameters
circle_center = (screen_width // 2, screen_height // 2)
circle_radius = 200
rotation_angle = 0
opening_size = math.pi / 8  # 1/16th of the circumference (fixed size for the opening)

# Ball parameters
ball_radius = 5
ball_speed = 10
balls = []  # List to store balls
escaped_balls = 0  # Track number of balls that have escaped
elastic_collisions = True  # Elastic collision toggle

# Clock to control the frame rate
clock = pygame.time.Clock()

# Start/stop toggle
is_running = True

# Set a timer to check CPU/memory every 1 second
last_monitor_time = time.time()
cpu_usage_list = []
cpu_usage_avg = 0
memory_usage = 0

# Improved ASCII skull for crash display
skull_ascii = """
       _____     
     .-\"     "-.  
    /           \\ 
   |    X   X    | 
   |     .-.     |  
   |    ( O )    | 
    \\  '-'-'   /   
     '-._____.-'
"""

# Initialize start time
start_time = time.time()

# Function to spawn a ball inside the circle
def spawn_ball():
    angle = random.uniform(0, 2 * math.pi)
    x = circle_center[0] + (circle_radius - ball_radius - 1) * math.cos(angle)
    y = circle_center[1] + (circle_radius - ball_radius - 1) * math.sin(angle)
    velocity = [random.choice([-1, 1]) * ball_speed, random.choice([-1, 1]) * ball_speed]
    color = random.choice(BALL_COLORS)
    return {"position": [x, y], "velocity": velocity, "color": color, "escaped": False}

# Start with one ball inside the circle
balls.append(spawn_ball())

# Function to reflect the ball off the perimeter
def reflect_ball(ball):
    angle_to_center = math.atan2(ball["position"][1] - circle_center[1], ball["position"][0] - circle_center[0])
    normal_x = math.cos(angle_to_center)
    normal_y = math.sin(angle_to_center)

    dot_product = ball["velocity"][0] * normal_x + ball["velocity"][1] * normal_y
    ball["velocity"][0] -= 2 * dot_product * normal_x
    ball["velocity"][1] -= 2 * dot_product * normal_y

    if not elastic_collisions:
        ball["velocity"][0] *= 0.9  # Lose 10% speed
        ball["velocity"][1] *= 0.9

# Function to check if an angle is within the range of the rotating opening
def is_angle_in_opening(ball_angle, opening_start_angle, opening_end_angle):
    if opening_start_angle < opening_end_angle:
        return opening_start_angle <= ball_angle <= opening_end_angle
    else:
        return ball_angle >= opening_start_angle or ball_angle <= opening_end_angle

# Function to remove balls when they leave the screen
def remove_balls_outside_screen():
    for ball in balls[:]:
        x, y = ball["position"]
        if x < 0 or x > screen_width or y < 0 or y > screen_height:
            balls.remove(ball)

# Function to measure frame rendering time
def measure_frame_time(func):
    start_time = timeit.default_timer()
    func()
    frame_time = timeit.default_timer() - start_time
    print(f"Frame render time: {frame_time:.4f} seconds")
    return frame_time

# Function to draw the toggle button
def draw_button():
    button_color = (0, 255, 0) if elastic_collisions else (255, 0, 0)
    pygame.draw.rect(screen, button_color, (10, 50, 150, 40))
    font = pygame.font.SysFont(None, 30)
    button_text = "Elastic: ON" if elastic_collisions else "Elastic: OFF"
    text_surf = font.render(button_text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=(10 + 150 // 2, 50 + 40 // 2))
    screen.blit(text_surf, text_rect)

# Function to display information on screen
def display_info(elapsed_time):
    font = pygame.font.SysFont(None, 24)

    # Display ball counts (change labels to Inside, Outside, Total)
    inside_count_text = font.render(f"Inside Count: {len(balls)}", True, (255, 255, 255))
    outside_count_text = font.render(f"Outside Count: {escaped_balls}", True, (255, 255, 255))
    total_count_text = font.render(f"Total Count: {len(balls) + escaped_balls}", True, (255, 255, 255))
    screen.blit(inside_count_text, (screen_width - 250, 10))
    screen.blit(outside_count_text, (screen_width - 250, 50))
    screen.blit(total_count_text, (screen_width - 250, 90))

    # Display CPU and memory usage
    cpu_text = font.render(f"CPU: {cpu_usage_avg:.1f}%", True, (255, 255, 255))  # Use the average CPU usage
    memory_text = font.render(f"Memory: {memory_usage}%", True, (255, 255, 255))
    screen.blit(cpu_text, (10, screen_height - 30))  # Moved to bottom
    screen.blit(memory_text, (150, screen_height - 30))  # Moved to bottom

    # Display FPS
    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
    screen.blit(fps_text, (300, screen_height - 30))  # Moved to bottom

    # Display elapsed time
    elapsed_time_text = font.render(f"Time: {int(elapsed_time)}s", True, (255, 255, 255))
    screen.blit(elapsed_time_text, (450, screen_height - 30))  # Adjust position as needed

    # Show the most common ball color inside the circle with count
    ball_colors_in_circle = [tuple(ball["color"]) for ball in balls if not ball["escaped"]]
    if ball_colors_in_circle:
        most_common_color, count = Counter(ball_colors_in_circle).most_common(1)[0]
        pygame.draw.circle(screen, most_common_color, (screen_width - 100, 500), 30)
        most_color_text = font.render(f"Count: {count}", True, (255, 255, 255))
        screen.blit(most_color_text, (screen_width - 190, 480))

# Function to display crash message when frame time exceeds 1.5 seconds
def display_crash_message():
    # Clear the screen first
    screen.fill(BLACK)
    
    # Display the crash message and center it on the screen
    font = pygame.font.SysFont(None, 36)
    crash_text = font.render("Simulation Crashed!", True, (255, 0, 0))
    crash_rect = crash_text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
    screen.blit(crash_text, crash_rect)

    # Display ASCII skull centered on the screen
    font = pygame.font.SysFont(None, 24)
    lines = skull_ascii.split("\n")
    for i, line in enumerate(lines):
        ascii_text = font.render(line, True, (255, 0, 0))
        ascii_rect = ascii_text.get_rect(center=(screen_width // 2, screen_height // 2 + i * 30))
        screen.blit(ascii_text, ascii_rect)

    # Display final ball counts after clearing the screen
    display_info()

    # Refresh the screen
    pygame.display.flip()

    # Clear the balls list
    balls.clear()

# Function to handle simulation updates
def update_simulation():
    global rotation_angle, escaped_balls, cpu_usage_avg, memory_usage, start_time
    rotation_angle += 0.02
    rotation_angle %= (2 * math.pi)

    opening_start_angle = rotation_angle
    opening_end_angle = (opening_start_angle + opening_size) % (2 * math.pi)

    for angle in range(0, 360):
        rad = math.radians(angle)
        if not is_angle_in_opening(rad, opening_start_angle, opening_end_angle):
            x = circle_center[0] + circle_radius * math.cos(rad)
            y = circle_center[1] + circle_radius * math.sin(rad)
            pygame.draw.circle(screen, (255, 255, 0), (int(x), int(y)), 2)

    for ball in balls[:]:
        ball["position"][0] += ball["velocity"][0]
        ball["position"][1] += ball["velocity"][1]

        if not ball["escaped"]:
            dist_from_center = math.sqrt(
                (ball["position"][0] - circle_center[0]) ** 2 +
                (ball["position"][1] - circle_center[1]) ** 2
            )
            if dist_from_center >= circle_radius - ball_radius:
                ball_angle = math.atan2(ball["position"][1] - circle_center[1], ball["position"][0] - circle_center[0])
                ball_angle %= (2 * math.pi)

                if is_angle_in_opening(ball_angle, opening_start_angle, opening_end_angle):
                    ball["escaped"] = True
                    escaped_balls += 1
                    balls.append(spawn_ball())
                    balls.append(spawn_ball())
                else:
                    reflect_ball(ball)

        pygame.draw.circle(screen, ball["color"], (int(ball["position"][0]), int(ball["position"][1])), ball_radius)

    remove_balls_outside_screen()

    # Periodically update CPU and memory usage
    current_time = time.time()
    if current_time - last_monitor_time >= 1:
        cpu_usage_list.append(psutil.cpu_percent())
        if len(cpu_usage_list) > 5:  # Keep track of the last 5 seconds
            cpu_usage_list.pop(0)
        cpu_usage_avg = sum(cpu_usage_list) / len(cpu_usage_list)
        memory_usage = psutil.virtual_memory().percent

    # Calculate elapsed time
    elapsed_time = time.time() - start_time

    return elapsed_time

# Main loop
running = True
crashed = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Toggle start/stop with spacebar
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            is_running = not is_running

        # Toggle elastic collisions with button click
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if 10 <= mouse_x <= 10 + 150 and 50 <= mouse_y <= 50 + 40:
                elastic_collisions = not elastic_collisions

    if crashed:
        # Keep displaying the crash message and stop further updates
        continue

    screen.fill(BLACK)

    if is_running:
        # Measure time per frame and trigger crash if frame time exceeds 1.5 seconds
        frame_time = measure_frame_time(lambda: update_simulation())
        if frame_time > 1.5:
            display_crash_message()
            pygame.display.flip()
            crashed = True  # Stop the simulation but don't exit the application
            continue

    # Draw the elastic collision toggle button
    draw_button()

    # Display information (ball counts, CPU, memory, FPS, and most common ball color)
    elapsed_time = update_simulation()
    display_info(elapsed_time)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
