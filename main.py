import pygame
import sys
from menu import Menu
from network import NetworkManager

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
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Create the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Square Skirmish")
clock = pygame.time.Clock()

# Initialize menu and network
menu = Menu(WINDOW_WIDTH, WINDOW_HEIGHT)
network = NetworkManager()

# Game state
game_state = "menu"  # menu, playing, death
player = None
platforms = []
score = 0

def reset_game():
    global player, platforms, score
    player = {
        "x": WINDOW_WIDTH // 2,
        "y": WINDOW_HEIGHT // 2,
        "width": 30,
        "height": 30,
        "vel_y": 0,
        "jumping": False
    }
    platforms = [
        {"x": 0, "y": WINDOW_HEIGHT - 40, "width": WINDOW_WIDTH, "height": 40},
        {"x": 300, "y": 400, "width": 200, "height": 20},
        {"x": 100, "y": 300, "width": 200, "height": 20},
        {"x": 500, "y": 200, "width": 200, "height": 20}
    ]
    score = 0

def handle_movement(keys, key_bindings):
    # Handle player movement
    if keys[key_bindings["left"]]:
        player["x"] -= 5
    if keys[key_bindings["right"]]:
        player["x"] += 5
    if keys[key_bindings["jump"]] and not player["jumping"]:
        player["vel_y"] = -15
        player["jumping"] = True

def apply_physics():
    # Apply gravity
    player["vel_y"] += 0.8
    player["y"] += player["vel_y"]

    # Check platform collisions
    player["jumping"] = True
    for platform in platforms:
        if (player["x"] < platform["x"] + platform["width"] and
            player["x"] + player["width"] > platform["x"] and
            player["y"] + player["height"] > platform["y"] and
            player["y"] + player["height"] < platform["y"] + platform["height"] + player["vel_y"]):
            player["jumping"] = False
            player["vel_y"] = 0
            player["y"] = platform["y"] - player["height"]

    # Check screen boundaries
    if player["x"] < 0:
        player["x"] = 0
    if player["x"] > WINDOW_WIDTH - player["width"]:
        player["x"] = WINDOW_WIDTH - player["width"]
    if player["y"] > WINDOW_HEIGHT:
        game_state = "death"
        menu.set_death_screen(score)

def draw_game():
    screen.fill(BLACK)
    
    # Draw platforms
    for platform in platforms:
        pygame.draw.rect(screen, GREEN, (platform["x"], platform["y"], platform["width"], platform["height"]))
    
    # Draw player
    pygame.draw.rect(screen, RED, (player["x"], player["y"], player["width"], player["height"]))
    
    # Draw score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # Draw other player if in multiplayer
    if network.connected:
        other_player = network.get_other_player()
        if other_player:
            pygame.draw.rect(screen, BLUE, (other_player["x"], other_player["y"], 
                                          other_player["width"], other_player["height"]))

def handle_multiplayer():
    if network.connected:
        # Send player position to other player
        network.send_data({
            "x": player["x"],
            "y": player["y"],
            "width": player["width"],
            "height": player["height"]
        })

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Handle menu events
        if game_state == "menu":
            menu.handle_event(event)
            if menu.get_state() == "playing":
                game_state = "playing"
                reset_game()
            elif menu.get_state() == "host_game":
                game_code = network.start_server()
                if game_code:
                    menu.set_game_code(game_code)
            elif menu.get_state() == "join_game":
                if len(menu.game_code_input) == 6:
                    if network.join_game("localhost"):  # For local network testing
                        menu.set_connected(True)
                        game_state = "playing"
                        reset_game()
            elif menu.get_state() == "death":
                game_state = "death"
        
        # Handle game events
        elif game_state == "playing":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = "menu"
                    menu.set_state("main")
                    network.disconnect()
    
    # Update game state
    if game_state == "menu":
        menu.update()
        menu.draw(screen)
    elif game_state == "playing":
        keys = pygame.key.get_pressed()
        handle_movement(keys, menu.get_key_bindings())
        apply_physics()
        handle_multiplayer()
        draw_game()
    elif game_state == "death":
        menu.draw(screen)
    
    pygame.display.flip()
    clock.tick(FPS) 