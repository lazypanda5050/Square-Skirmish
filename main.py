import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Set up the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Square Skirmish")
clock = pygame.time.Clock()

# Player properties
player_size = 50
player_x = WINDOW_WIDTH // 2 - player_size // 2
player_y = WINDOW_HEIGHT // 2 - player_size // 2
player_speed = 5

def main():
    global player_x, player_y
    
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Handle player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player_y = max(0, player_y - player_speed)
        if keys[pygame.K_s]:
            player_y = min(WINDOW_HEIGHT - player_size, player_y + player_speed)
        if keys[pygame.K_a]:
            player_x = max(0, player_x - player_speed)
        if keys[pygame.K_d]:
            player_x = min(WINDOW_WIDTH - player_size, player_x + player_speed)
        
        # Clear the screen
        screen.fill(BLACK)
        
        # Draw the player
        pygame.draw.rect(screen, RED, (player_x, player_y, player_size, player_size))
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 