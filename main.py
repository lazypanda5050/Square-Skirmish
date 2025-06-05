import pygame
import sys
import random
from menu import Menu

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -12

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Set up the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Square Skirmish")
clock = pygame.time.Clock()

# Initialize menu
menu = Menu(WINDOW_WIDTH, WINDOW_HEIGHT)

def reset_game():
    global player_x, player_y, player_velocity_y, is_jumping
    player_x = WINDOW_WIDTH // 2 - player_size // 2
    player_y = WINDOW_HEIGHT // 2 - player_size // 2
    player_velocity_y = 0
    is_jumping = False

# Player properties
player_size = 50
player_x = WINDOW_WIDTH // 2 - player_size // 2
player_y = WINDOW_HEIGHT // 2 - player_size // 2
player_speed = 5
player_velocity_y = 0
is_jumping = False

# Platform class
class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self, surface):
        pygame.draw.rect(surface, GREEN, self.rect)

# Create some platforms
platforms = [
    Platform(100, 400, 200, 20),
    Platform(400, 300, 200, 20),
    Platform(200, 200, 200, 20),
    Platform(600, 500, 200, 20),
]

def check_collision(player_rect, platforms):
    for platform in platforms:
        if player_rect.colliderect(platform.rect):
            # Calculate overlap for each side
            overlap_left = player_rect.right - platform.rect.left
            overlap_right = platform.rect.right - player_rect.left
            overlap_top = player_rect.bottom - platform.rect.top
            overlap_bottom = platform.rect.bottom - player_rect.top
            
            # Find the smallest overlap
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
            
            # Handle collision based on the smallest overlap
            if min_overlap == overlap_top and player_velocity_y > 0:
                return "top", platform.rect.top - player_rect.height
            elif min_overlap == overlap_bottom and player_velocity_y < 0:
                return "bottom", platform.rect.bottom
            elif min_overlap == overlap_left:
                return "left", platform.rect.left - player_rect.width
            elif min_overlap == overlap_right:
                return "right", platform.rect.right
    return None, None

def main():
    global player_x, player_y, player_velocity_y, is_jumping
    
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle menu events
            menu_action = menu.handle_event(event)
            if menu_action == "quit":
                running = False
            elif menu_action == "start_game":
                reset_game()
            elif menu_action == "restart":
                reset_game()
            elif menu_action == "main_menu":
                menu.set_state("main")
        
        # Clear the screen
        screen.fill(BLACK)
        
        # Get current key bindings
        key_bindings = menu.get_key_bindings()
        
        # Game state handling
        if menu.state == "game":
            # Handle player movement
            keys = pygame.key.get_pressed()
            if keys[key_bindings["move_left"]]:
                player_x = max(0, player_x - player_speed)
            if keys[key_bindings["move_right"]]:
                player_x = min(WINDOW_WIDTH - player_size, player_x + player_speed)
            if keys[key_bindings["jump"]] and not is_jumping:
                player_velocity_y = JUMP_STRENGTH
                is_jumping = True
            
            # Apply gravity
            player_velocity_y += GRAVITY
            player_y += player_velocity_y
            
            # Create player rectangle for collision detection
            player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
            
            # Check for platform collisions
            collision_type, collision_pos = check_collision(player_rect, platforms)
            if collision_type == "top":
                player_y = collision_pos
                player_velocity_y = 0
                is_jumping = False
            elif collision_type == "bottom":
                player_y = collision_pos
                player_velocity_y = 0
            elif collision_type == "left":
                player_x = collision_pos
            elif collision_type == "right":
                player_x = collision_pos
            
            # Check for death (falling off screen)
            if player_y > WINDOW_HEIGHT:
                menu.set_state("death")
            
            # Draw platforms
            for platform in platforms:
                platform.draw(screen)
            
            # Draw the player
            pygame.draw.rect(screen, RED, (player_x, player_y, player_size, player_size))
        else:
            # Draw menu
            menu.draw(screen)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 