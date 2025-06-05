import pygame

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

class Menu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = "main"  # main, settings, game, death
        
        # Initialize key bindings first
        self.key_bindings = {
            "move_left": pygame.K_a,
            "move_right": pygame.K_d,
            "jump": pygame.K_SPACE
        }
        
        # Then create buttons that depend on key_bindings
        self.buttons = self.create_buttons()

    def create_buttons(self):
        button_width = 200
        button_height = 50
        spacing = 20
        start_y = self.screen_height // 2 - 100

        main_menu_buttons = {
            "play": Button(self.screen_width//2 - button_width//2, start_y, 
                         button_width, button_height, "Play"),
            "settings": Button(self.screen_width//2 - button_width//2, start_y + button_height + spacing,
                            button_width, button_height, "Settings"),
            "quit": Button(self.screen_width//2 - button_width//2, start_y + (button_height + spacing) * 2,
                         button_width, button_height, "Quit")
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
            "settings": settings_buttons,
            "death": death_screen_buttons
        }

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.state == "game":
                self.state = "main"
            elif self.state == "settings":
                self.state = "main"
            return None

        if self.state in self.buttons:
            for button in self.buttons[self.state].values():
                if button.handle_event(event):
                    if isinstance(button, KeyBindButton):
                        self.key_bindings[button.key_name.lower().replace(" ", "_")] = button.current_key
                    elif button.text == "Play":
                        self.state = "game"
                        return "start_game"
                    elif button.text == "Settings":
                        self.state = "settings"
                    elif button.text == "Quit":
                        return "quit"
                    elif button.text == "Back":
                        self.state = "main"
                    elif button.text == "Restart":
                        self.state = "game"
                        return "restart"
                    elif button.text == "Main Menu":
                        self.state = "main"
                        return "main_menu"
        return None

    def draw(self, surface):
        surface.fill((0, 0, 0))
        
        if self.state == "main":
            title = pygame.font.Font(None, 74).render("Square Skirmish", True, (255, 255, 255))
            surface.blit(title, (self.screen_width//2 - title.get_width()//2, 100))
        elif self.state == "settings":
            title = pygame.font.Font(None, 74).render("Settings", True, (255, 255, 255))
            surface.blit(title, (self.screen_width//2 - title.get_width()//2, 100))
        elif self.state == "death":
            title = pygame.font.Font(None, 74).render("Game Over!", True, (255, 0, 0))
            surface.blit(title, (self.screen_width//2 - title.get_width()//2, 100))

        if self.state in self.buttons:
            for button in self.buttons[self.state].values():
                button.draw(surface)

    def get_key_bindings(self):
        return self.key_bindings

    def set_state(self, state):
        self.state = state 