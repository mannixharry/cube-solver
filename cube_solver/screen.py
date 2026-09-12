import numpy as np
import pygame

from .data import *
from .paths import RESOURCES_DIR

class Renderer:
    '''Owns the pygame window: displaying the cube/UI and detecting clicks on facelets and buttons.'''

    def __init__(self, width=800, height=800):
        pygame.init()
        self.width = width
        self.height = height

        self.screen = self.__create_window()
        self.buttons = []

        self.__clicked_facelet = None
        self.__clicked_button = None
        self.__mouse_pressed = False

        self.__displayed_quadrilaterals = []

    def detect_facelet_click(self, mouse_pos):
        '''Sets __clicked_facelet to the index of the facelet under mouse_pos, if any.'''

        def __is_point_inside_quadrilateral(quad, point):
            '''Checks whether point lies within convex quadrilateral quad, by comparing its area
            to the sum of the areas of the four triangles point forms with each of its edges -
            these only match if point is inside.
            '''
            A, B, C, D = (np.array(corner) for corner in quad)
            P = np.array(point)
            ab, ac, ad = B - A, C - A, D - A
            pa, pb, pc, pd = A - P, B - P, C - P, D - P
            area = lambda x, y: abs(x[0] * y[1] - x[1] * y[0])
            quad_area = area(ab, ac) + area(ac, ad)  # Actually 2x the area, but irrelevant for a ratio.
            total_area = area(pa, pb) + area(pb, pc) + area(pc, pd) + area(pd, pa)
            relative_error = abs((total_area - quad_area) / quad_area)
            return relative_error < 0.001

        for quad, index in self.__displayed_quadrilaterals:
            if __is_point_inside_quadrilateral(quad, mouse_pos):
                self.__clicked_facelet = index

    def get_clicked_facelet(self):
        '''Returns and clears the most recently clicked facelet's index.'''
        clicked_facelet = self.__clicked_facelet
        self.__clicked_facelet = None
        return clicked_facelet

    def __create_window(self):
        '''Creates and returns the pygame window.'''
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Cube Solver')
        icon = pygame.image.load(RESOURCES_DIR / 'rubick.png')
        pygame.display.set_icon(icon)
        return screen

    def display_move_text(self, move_count, move):
        '''Displays the notation of the move being demonstrated, and the moves remaining.'''
        font = pygame.font.Font(RESOURCES_DIR / 'pixel_font.ttf', 80)

        move_text = font.render(f"{Data.move_notation_for_display[move]}", True, (0, 0, 51))
        move_count_text = font.render(f"{move_count}", True, (0, 0, 51))

        move_text_rect = move_text.get_rect(center=(0.5 * self.width, 0.75 * self.height))
        move_count_text_rect = move_count_text.get_rect(center=(0.85 * self.width, 0.15 * self.height))

        self.screen.blit(move_text, move_text_rect)
        self.screen.blit(move_count_text, move_count_text_rect)

    def display_text(self, text, size=80):
        '''Displays text centred near the top of the screen.'''
        font = pygame.font.Font(RESOURCES_DIR / 'pixel_font.ttf', size)
        text_surface = font.render(text, True, (0, 0, 51))
        text_rect = text_surface.get_rect(center=(0.5 * self.width, 0.2 * self.height))
        self.screen.blit(text_surface, text_rect)

    def display_info(self, instructions):
        '''Clears the screen and displays each line of instructions, vertically centred.'''
        self.screen.fill((255, 255, 255))
        font = pygame.font.Font(RESOURCES_DIR / 'pixel_font.ttf', 18)

        total_text_height = len(instructions) * 30
        y_offset = (self.height - total_text_height) // 2

        for line in instructions:
            text_surface = font.render(line, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(text_surface, text_rect)
            y_offset += 30

    def update_mouse(self, mouse_pressed, mouse_pos, keys_pressed):
        '''Detects a facelet click on mouse release, and forwards state to check for button clicks.'''
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        if any(mouse_pressed):
            self.__mouse_pressed = True
        elif self.__mouse_pressed:
            self.__mouse_pressed = False  # Mouse released (falling edge).
            self.detect_facelet_click(mouse_pos)

        self.detect_button_click(mouse_pressed, mouse_pos, keys_pressed)

    def clear_screen(self):
        '''Clears the screen and any tracked displayed quadrilaterals.'''
        self.screen.fill((255, 255, 255))
        self.__displayed_quadrilaterals = []

    def draw_line(self, a, b, colour):
        '''Draws a line from a to b in colour.'''
        pygame.draw.line(self.screen, colour, a, b, 6)

    def draw_quadrilateral(self, corners, colour):
        '''Draws a filled quadrilateral with a black outline.'''
        pygame.draw.polygon(self.screen, colour or 'black', corners)
        pygame.draw.polygon(self.screen, 'black', corners, 4)

    def add_displayed_quadrilateral(self, quadrilateral, index):
        '''Registers a drawn quadrilateral so it can be hit-tested for facelet clicks.

        Args:
            quadrilateral (np.array[Tuple[int, int]]): the quadrilateral's screen coordinates.
            index (int): the Facelet index it represents.
        '''
        self.__displayed_quadrilaterals.append((quadrilateral, index))

    def display_fps(self, fps):
        '''Displays an FPS counter in the top-left corner.'''
        font = pygame.font.SysFont('Arial', 20)
        fps_text = font.render(f'FPS: {int(fps)}', True, (0, 0, 0))
        self.screen.blit(fps_text, (10, 10))

    def detect_button_click(self, mouse_pressed, mouse_pos, keys_pressed):
        '''Sets __clicked_button to the most recently clicked button, if any.'''
        for button in self.buttons:
            if button.detect_click(mouse_pressed, mouse_pos, keys_pressed):
                self.__clicked_button = button

    def get_clicked_button(self):
        '''Returns and clears the most recently clicked button.'''
        clicked_button = self.__clicked_button
        self.__clicked_button = None
        return clicked_button

    def add_button(self, button):
        '''Adds a button to be displayed and checked for clicks.'''
        self.buttons.append(button)

    def display_buttons(self):
        '''Displays every registered button.'''
        for button in self.buttons:
            button.display(self.screen)

class Button:
    '''A clickable, optionally key-bound button with click debouncing.

    Attributes:
        name (str): unique button identifier.
    '''
    def __init__(self, name, image, top_left, size, key=None):
        '''
        Args:
            name (str): unique identifier for the button.
            image (pygame.Surface): the button's display image.
            top_left (Tuple[int, int]): position of the button's top-left corner.
            size (Tuple[int, int]): button dimensions.
            key (int, optional): keyboard key that also triggers the button. Defaults to None.
        '''
        self.__key = key
        self.__image = pygame.transform.scale(image, size)
        self.__rect = self.__image.get_rect()
        self.__rect.topleft = top_left

        self.name = name

        self.__last_click_time = pygame.time.get_ticks()
        self.__debounce = 100  # ms
        self.__latch = False

    def display(self, screen):
        '''Draws the button onto screen.'''
        screen.blit(self.__image, (self.__rect.x, self.__rect.y))

    def detect_click(self, mouse_pressed, mouse_pos, keys_pressed):
        '''Checks whether the button was just clicked (or its key just pressed), latching so a
        held click or key only registers once, and debouncing rapid re-clicks.

        Returns:
            bool: True if a click was detected.
        '''
        mouse_clicked = self.__rect.collidepoint(mouse_pos)
        key_pressed = self.__key is not None and keys_pressed[self.__key]

        if any(mouse_pressed) and mouse_clicked or key_pressed:
            if not self.__latch:
                current_time = pygame.time.get_ticks()
                self.__latch = True
                if current_time - self.__last_click_time > self.__debounce:
                    self.__last_click_time = current_time
                    return True
        else:
            self.__latch = False  # Require a release before the next click can register.

        return False
