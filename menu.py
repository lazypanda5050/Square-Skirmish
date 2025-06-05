import pygame
from network import NetworkManager

class Button:
    def __init__(self, x, y, width, height, text, font_size=36):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.is_hovered = False
        self.color = (100, 100, 100)
        self.hover_color = (150, 150, 150)
        self.text_color = (255, 255, 255)

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class KeyBindButton(Button):
    def __init__(self, x, y, width, height, text, key_name, current_key):
        super().__init__(x, y, width, height, f"{text}: {pygame.key.name(current_key)}")
        self.key_name = key_name
        self.current_key = current_key
        self.is_rebinding = False

    def draw(self, surface):
        if self.is_rebinding:
            self.text = f"{self.key_name}: Press any key..."
        else:
            self.text = f"{self.key_name}: {pygame.key.name(self.current_key)}"
        super().draw(surface)

    def handle_event(self, event):
        if self.is_rebinding and event.type == pygame.KEYDOWN:
            self.current_key = event.key
            self.is_rebinding = False
            return True
        elif event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.is_rebinding = True
        return False

class TextInput:
    def __init__(self, x, y, width, height, font_size=36):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.font = pygame.font.Font(None, font_size)
        self.active = False
        self.color = (100, 100, 100)
        self.active_color = (150, 150, 150)
        self.text_color = (255, 255, 255)

    def draw(self, surface):
        color = self.active_color if self.active else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                self.text += event.unicode
        return False

class Menu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = "main"  # main, settings, game, death, multiplayer, host, join
        
        # Initialize key bindings first
        self.key_bindings = {
            "move_left": pygame.K_a,
            "move_right": pygame.K_d,
            "jump": pygame.K_SPACE
        }
        
        # Initialize network manager
        self.network = NetworkManager()
        self.game_code = None
        
        # Then create buttons and text inputs that depend on key_bindings
        self.buttons = self.create_buttons()
        self.text_inputs = self.create_text_inputs()

    def create_buttons(self):
        button_width = 200
        button_height = 50
        spacing = 20
        start_y = self.screen_height // 2 - 100

        main_menu_buttons = {
            "play": Button(self.screen_width//2 - button_width//2, start_y, 
                         button_width, button_height, "Play"),
            "multiplayer": Button(self.screen_width//2 - button_width//2, start_y + button_height + spacing,
                               button_width, button_height, "Multiplayer"),
            "settings": Button(self.screen_width//2 - button_width//2, start_y + (button_height + spacing) * 2,
                            button_width, button_height, "Settings"),
            "quit": Button(self.screen_width//2 - button_width//2, start_y + (button_height + spacing) * 3,
                         button_width, button_height, "Quit")
        }

        multiplayer_buttons = {
            "host": Button(self.screen_width//2 - button_width//2, start_y,
                         button_width, button_height, "Host Game"),
            "join": Button(self.screen_width//2 - button_width//2, start_y + button_height + spacing,
                         button_width, button_height, "Join Game"),
            "back": Button(self.screen_width//2 - button_width//2, start_y + (button_height + spacing) * 2,
                         button_width, button_height, "Back")
        }

        host_buttons = {
            "start": Button(self.screen_width//2 - button_width//2, start_y + button_height + spacing * 2,
                          button_width, button_height, "Start Game"),
            "back": Button(self.screen_width//2 - button_width//2, start_y + (button_height + spacing) * 3,
                         button_width, button_height, "Back")
        }

        join_buttons = {
            "connect": Button(self.screen_width//2 - button_width//2, start_y + button_height + spacing * 2,
                            button_width, button_height, "Connect"),
            "back": Button(self.screen_width//2 - button_width//2, start_y + (button_height + spacing) * 3,
                         button_width, button_height, "Back")
        }

        settings_buttons = {
            "move_left": KeyBindButton(self.screen_width//2 - button_width//2, start_y,
                                     button_width, button_height, "Move Left", "Move Left", self.key_bindings["move_left"]),
            "move_right": KeyBindButton(self.screen_width//2 - button_width//2, start_y + button_height + spacing,
                                      button_width, button_height, "Move Right", "Move Right", self.key_bindings["move_right"]),
            "jump": KeyBindButton(self.screen_width//2 - button_width//2, start_y + (button_height + spacing) * 2,
                                button_width, button_height, "Jump", "Jump", self.key_bindings["jump"]),
            "back": Button(self.screen_width//2 - button_width//2, start_y + (button_height + spacing) * 3,
                         button_width, button_height, "Back")
        }

        death_screen_buttons = {
            "restart": Button(self.screen_width//2 - button_width//2, start_y,
                            button_width, button_height, "Restart"),
            "main_menu": Button(self.screen_width//2 - button_width//2, start_y + button_height + spacing,
                              button_width, button_height, "Main Menu")
        }

        return {
            "main": main_menu_buttons,
            "multiplayer": multiplayer_buttons,
            "host": host_buttons,
            "join": join_buttons,
            "settings": settings_buttons,
            "death": death_screen_buttons
        }

    def create_text_inputs(self):
        button_width = 200
        button_height = 50
        spacing = 20
        start_y = self.screen_height // 2 - 100

        return {
            "join": {
                "game_code": TextInput(self.screen_width//2 - button_width//2, start_y + button_height + spacing,
                                     button_width, button_height)
            }
        }

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.state in ["game", "settings", "multiplayer", "host", "join"]:
                self.state = "main"
            return None

        # Handle text inputs
        if self.state in self.text_inputs:
            for input_field in self.text_inputs[self.state].values():
                input_field.handle_event(event)

        if self.state in self.buttons:
            for button in self.buttons[self.state].values():
                if button.handle_event(event):
                    if isinstance(button, KeyBindButton):
                        self.key_bindings[button.key_name.lower().replace(" ", "_")] = button.current_key
                    elif button.text == "Play":
                        self.state = "game"
                        return "start_game"
                    elif button.text == "Multiplayer":
                        self.state = "multiplayer"
                    elif button.text == "Host Game":
                        self.state = "host"
                        self.game_code = self.network.start_server()
                    elif button.text == "Join Game":
                        self.state = "join"
                    elif button.text == "Start Game" and self.game_code:
                        self.state = "game"
                        return "start_multiplayer_host"
                    elif button.text == "Connect":
                        game_code = self.text_inputs["join"]["game_code"].text.upper()
                        if len(game_code) == 6 and self.network.join_game("localhost"):
                            self.state = "game"
                            return "start_multiplayer_join"
                    elif button.text == "Settings":
                        self.state = "settings"
                    elif button.text == "Quit":
                        return "quit"
                    elif button.text == "Back":
                        if self.state == "host":
                            self.network.disconnect()
                        self.state = "multiplayer"
                    elif button.text == "Restart":
                        self.state = "game"
                        return "restart"
                    elif button.text == "Main Menu":
                        self.state = "main"
                        return "main_menu"
        return None

    def draw(self, screen):
        """Draw the menu"""
        screen.fill((0, 0, 0))
        
        # Draw title
        title_font = pygame.font.SysFont(None, 64)
        title_text = title_font.render("Square Skirmish", True, (255, 255, 255))
        screen.blit(title_text, (self.screen_width//2 - title_text.get_width()//2, 50))

        # Draw menu items
        for i, item in enumerate(self.menu_items):
            color = (255, 255, 0) if i == self.selected_item else (255, 255, 255)
            text = self.font.render(item, True, color)
            screen.blit(text, (self.screen_width//2 - text.get_width()//2, 200 + i * 50))

        # Draw current key binding if in key binding mode
        if self.current_state == "key_binding":
            key_text = self.font.render(f"Press a key for {self.current_binding}", True, (255, 255, 255))
            screen.blit(key_text, (self.screen_width//2 - key_text.get_width()//2, 400))

        # Draw multiplayer menu
        if self.current_state == "multiplayer":
            mp_text = self.font.render("Multiplayer", True, (255, 255, 255))
            screen.blit(mp_text, (self.screen_width//2 - mp_text.get_width()//2, 200))
            
            for i, item in enumerate(self.multiplayer_items):
                color = (255, 255, 0) if i == self.selected_item else (255, 255, 255)
                text = self.font.render(item, True, color)
                screen.blit(text, (self.screen_width//2 - text.get_width()//2, 250 + i * 50))

        # Draw host game screen
        if self.current_state == "host_game":
            host_text = self.font.render("Host Game", True, (255, 255, 255))
            screen.blit(host_text, (self.screen_width//2 - host_text.get_width()//2, 200))
            
            if self.network.game_code:
                code_text = self.font.render(f"Game Code: {self.network.game_code}", True, (255, 255, 255))
                screen.blit(code_text, (self.screen_width//2 - code_text.get_width()//2, 250))
                
                conn_info = self.network.get_connection_info()
                if conn_info:
                    ip_text = self.font.render(f"IP Address: {conn_info['ip']}", True, (255, 255, 255))
                    screen.blit(ip_text, (self.screen_width//2 - ip_text.get_width()//2, 300))
                    
                    port_text = self.font.render(f"Port: {conn_info['port']}", True, (255, 255, 255))
                    screen.blit(port_text, (self.screen_width//2 - port_text.get_width()//2, 350))
                
                waiting_text = self.font.render("Waiting for player...", True, (255, 255, 255))
                screen.blit(waiting_text, (self.screen_width//2 - waiting_text.get_width()//2, 400))
                
                back_text = self.font.render("Press ESC to cancel", True, (255, 255, 255))
                screen.blit(back_text, (self.screen_width//2 - back_text.get_width()//2, 450))

        # Draw join game screen
        if self.current_state == "join_game":
            join_text = self.font.render("Join Game", True, (255, 255, 255))
            screen.blit(join_text, (self.screen_width//2 - join_text.get_width()//2, 200))
            
            # Draw text input field
            pygame.draw.rect(screen, (255, 255, 255), (self.screen_width//2 - 100, 250, 200, 40), 2)
            input_text = self.font.render(self.game_code_input, True, (255, 255, 255))
            screen.blit(input_text, (self.screen_width//2 - 90, 260))
            
            # Draw error message if any
            error = self.network.get_connection_error()
            if error:
                error_text = self.font.render(error, True, (255, 0, 0))
                screen.blit(error_text, (self.screen_width//2 - error_text.get_width()//2, 300))
            
            back_text = self.font.render("Press ESC to cancel", True, (255, 255, 255))
            screen.blit(back_text, (self.screen_width//2 - back_text.get_width()//2, 350))

        # Draw death screen
        if self.current_state == "death":
            death_text = self.font.render("Game Over!", True, (255, 0, 0))
            screen.blit(death_text, (self.screen_width//2 - death_text.get_width()//2, 200))
            
            score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            screen.blit(score_text, (self.screen_width//2 - score_text.get_width()//2, 250))
            
            restart_text = self.font.render("Press SPACE to restart", True, (255, 255, 255))
            screen.blit(restart_text, (self.screen_width//2 - restart_text.get_width()//2, 300))
            
            menu_text = self.font.render("Press ESC for menu", True, (255, 255, 255))
            screen.blit(menu_text, (self.screen_width//2 - menu_text.get_width()//2, 350))

    def get_key_bindings(self):
        return self.key_bindings

    def set_state(self, state):
        self.state = state

    def get_network(self):
        return self.network 