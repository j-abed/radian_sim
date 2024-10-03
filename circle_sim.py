import pygame
import math

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
BRIGHT_PERIMETER = (255, 255, 0)  # Bright yellow for the perimeter

# Circle parameters
circle_center = (screen_width // 2, screen_height // 2)
circle_radius = 200
rotation_angle = 0
opening_size = math.pi / 8  # 1/16th of the circumference

# Clock to control the frame rate
clock = pygame.time.Clock()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen (fill with black background)
    screen.fill(BLACK)

    # Calculate the angle of rotation
    rotation_angle += 0.02  # Adjust the speed of rotation if needed

    # Draw the perimeter of the circle, leaving a fixed opening
    for angle in range(0, 360):
        rad = math.radians(angle)
        if rad < rotation_angle or rad > rotation_angle + opening_size:
            x = circle_center[0] + circle_radius * math.cos(rad)
            y = circle_center[1] + circle_radius * math.sin(rad)
            pygame.draw.circle(screen, BRIGHT_PERIMETER, (int(x), int(y)), 2)

    # Update the display
    pygame.display.flip()

    # Limit the frame rate to 60 frames per second
    clock.tick(60)

# Quit Pygame
pygame.quit()
