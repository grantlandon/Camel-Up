import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants for the screen, track, and camel sizes
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
TRACK_Y_POSITION = SCREEN_HEIGHT - 100  # Position of the track near the bottom of the screen
CAMEL_WIDTH = 50
CAMEL_HEIGHT = 30

# Colors for camels, background, and track elements
BACKGROUND_COLOR = (255, 255, 255)  # White background
CAMEL_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 165, 0)]  # Red, Green, Blue, Yellow, Orange
TRACK_COLOR = (200, 200, 200)  # Light grey for the track
LINE_COLOR = (0, 0, 0)  # Black for lines and numbers
FINISH_LINE_COLOR = (255, 0, 0)  # Red for the finish line

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Camel Up Game")

# Track configuration
NUM_SPACES = 16
SPACE_WIDTH = SCREEN_WIDTH // NUM_SPACES
FINISH_LINE_POSITION = 15  # Between space 15 and 16

# Initial positions for camels (stacked vertically above the starting space)
camel_positions = {color: [SPACE_WIDTH // 2 - CAMEL_WIDTH // 2, TRACK_Y_POSITION - (i * (CAMEL_HEIGHT) + CAMEL_HEIGHT // 2)] for i, color in enumerate(CAMEL_COLORS)}

# Game loop (basic setup to quit with window close)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with the background color
    screen.fill(BACKGROUND_COLOR)

    # Draw the track spaces at the bottom of the screen
    for i in range(NUM_SPACES):
        x = i * SPACE_WIDTH
        # Draw each track space
        pygame.draw.rect(screen, TRACK_COLOR, (x, TRACK_Y_POSITION, SPACE_WIDTH, CAMEL_HEIGHT * 2))
        pygame.draw.line(screen, LINE_COLOR, (x, TRACK_Y_POSITION), (x, TRACK_Y_POSITION + CAMEL_HEIGHT * 2), 2)
        
        # Draw space number below the track
        font = pygame.font.Font(None, 24)
        number_text = font.render(str(i + 1), True, LINE_COLOR)
        screen.blit(number_text, (x + SPACE_WIDTH // 2 - number_text.get_width() // 2, TRACK_Y_POSITION + CAMEL_HEIGHT * 2 + 10))
    
    # Draw the finish line between the 15th and 16th spaces
    finish_x = FINISH_LINE_POSITION * SPACE_WIDTH
    pygame.draw.line(screen, FINISH_LINE_COLOR, (finish_x, TRACK_Y_POSITION), (finish_x, TRACK_Y_POSITION + CAMEL_HEIGHT * 2), 5)

    # Draw each camel at its current position, stacking them vertically above the spaces
    for index, (color, position) in enumerate(camel_positions.items()):
        # Calculate stacked y position for camels
        stacked_y_position = position[1] 
        pygame.draw.rect(screen, color, (position[0], stacked_y_position, CAMEL_WIDTH, CAMEL_HEIGHT))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
