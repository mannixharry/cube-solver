from data import * 
import numpy as np
import pygame
from pygame.locals import K_ESCAPE

class Renderer:

    def __init__(self, width=800, height=800):
        pygame.init()
        self.width = width
        self.height = height
        self.thickness = 2
        self.screen = self.create_window()
        self.font = pygame.font.SysFont('Arial', 20)
        self.colour = (0, 0, 0)

        self.buttons = []

        self.clicked_facelet = None
        self.clicked_button = None
        self.mouse_pressed = False

        self.displayed_quadrilaterals = []
        self.displayed_quadrilaterals_indices = []
        
    def detect_facelet_click(self, mouse_pos):

        # !!!
        def is_point_inside_triangle(A, B, C, P):
            v0, v1, v2 = C - A, B - A, P - A
            dot00, dot01, dot02, dot11, dot12 = np.dot(v0, v0), np.dot(v0, v1), np.dot(v0, v2), np.dot(v1, v1), np.dot(v1, v2)
            invDenom = 1 / (dot00 * dot11 - dot01 * dot01)
            u, v = (dot11 * dot02 - dot01 * dot12) * invDenom, (dot00 * dot12 - dot01 * dot02) * invDenom
            return u >= 0 and v >= 0 and u + v <= 1

        def is_point_inside_quadrilateral(corners, P):
            A, B, C, D, = [np.array(i) for i in corners]
            P = np.array(P)
            return is_point_inside_triangle(A, B, C, P) or is_point_inside_triangle(A, C, D, P)

        for i, quad in enumerate(self.displayed_quadrilaterals):
            if is_point_inside_quadrilateral(quad, mouse_pos):
                
                self.clicked_facelet = self.displayed_quadrilaterals_indices[i]

    def get_clicked_facelet(self):
        return_facelet = self.clicked_facelet
        self.clicked_facelet = None
        return return_facelet

    def create_window(self):
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Cube Solver')
        icon = pygame.image.load('resources/rubick.png')
        pygame.display.set_icon(icon)
        return screen

    def display_move_text(self, move_count, move):
        font = pygame.font.Font('resources/pixel_font.ttf', 80)

        move_text = font.render(f"{Data.move_notation_for_display[move]}", True, (0, 0, 51))
        move_count_text = font.render(f"{move_count}", True, (0, 0, 51))

        move_text_rect = move_text.get_rect(center=(0.5 * self.width, 0.75 * self.height))
        move_count_text_rect = move_count_text.get_rect(center=(0.85 * self.width, 0.15 * self.height))

        # Blit the text at the calculated positions
        self.screen.blit(move_text, move_text_rect)
        self.screen.blit(move_count_text, move_count_text_rect)

    def display_text(self, text, size = 80):

        font = pygame.font.Font('resources/pixel_font.ttf', size)
        text = font.render(text, True, (0, 0, 51))
        text_rect = text.get_rect(center=(0.5 * self.width, 0.2 * self.height))
        # Blit the text at the calculated positions
        self.screen.blit(text, text_rect)


    def display_info(self,instructions):

        # Clear the screen
        self.screen.fill((255, 255, 255))  # Fill screen with white

        # Load the font for instructions
        font = pygame.font.Font('resources/pixel_font.ttf', 18)

        total_text_height = len(instructions) * 30  # 30px per line

        # Calculate the starting y_offset to center the text vertically
        y_offset = (self.height - total_text_height) // 2

        for line in instructions:
            text_surface = font.render(line, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(text_surface, text_rect)
            y_offset += 30  # Space between lines

    def update_mouse(self, mouse_pressed, mouse_pos, keys):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        if any(mouse_pressed): 
            self.mouse_pressed = True
        elif self.mouse_pressed == True:
            self.mouse_pressed = False # mouse released (falling edge)
            self.detect_facelet_click(mouse_pos)

        self.detect_button_click(mouse_pressed, mouse_pos, keys)
    def clear_screen(self):
        self.screen.fill((255, 255, 255))
        self.displayed_quadrilaterals, self.displayed_quadrilaterals_indices = [], []
    

    def clear_display_data(self):
        self.displayed_quadrilaterals, self.displayed_quadrilaterals_indices = [], []


    def draw_line(self, a, b, colour):
        pygame.draw.line(self.screen, colour, a, b, self.thickness*3)

    def draw_rectangle(self, corners, colour):
        if colour:
            pygame.draw.polygon(self.screen, colour, corners)
        else:
            pygame.draw.polygon(self.screen, 'black', corners)
        pygame.draw.polygon(self.screen, 'black', corners, self.thickness*2)

    def add_displayed_quadrilateral(self, rectangle, index):

        self.displayed_quadrilaterals.append(rectangle)
        self.displayed_quadrilaterals_indices.append(index)

    def display_fps(self, fps):
        fps_text = self.font.render(f'FPS: {int(fps)}', True, self.colour)
        self.screen.blit(fps_text, (10, 10))

    def detect_button_click(self, mouse_pressed, mouse_pos, keys_pressed):
   
        for button in self.buttons:
            if button.detect_click(mouse_pressed, mouse_pos, keys_pressed):
                self.clicked_button = button
                
    def get_clicked_button(self):
        return_button = self.clicked_button
        self.clicked_button = None 
        return return_button
    
    def add_button(self, button):
        self.buttons.append(button)
    
class Button:
    def __init__(self, name, image, x, y, size, key=None):
        self.key = key 
        

        self.image = pygame.transform.scale(image, size)  # Resize the image to 100x100
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)
        self.name = name 
        self.last_click_time = pygame.time.get_ticks()

        self.debounce = 100 # 100 ms button debounce 

        self.latch = False 
        
    def display(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        
    def detect_click(self, mouse_pressed, mouse_pos, keys_pressed):
         
        mouse_clicked = self.rect.collidepoint(mouse_pos)
        key_pressed = self.key is not None and keys_pressed[self.key]

        if any(mouse_pressed) and mouse_clicked or key_pressed:
            if not self.latch: 
                current_time = pygame.time.get_ticks()
                self.latch = True 
                if current_time - self.last_click_time > self.debounce:
                    self.last_click_time = current_time
                    return True 
        else: 
            self.latch = False # force a period of no input before the next click. 

        return False 

            