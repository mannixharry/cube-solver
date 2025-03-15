from data import * 
import numpy as np
import pygame

class Renderer:
    '''Repsonsible for displaying GUI and detecting user interactions. 
    GUI is a pygame window. 
    '''
    def __init__(self, width=800, height=800):
        '''Initializes a window with given dimensions.

        Args:
            width (int, optional): Screen width. Defaults to 800.
            height (int, optional): Screen height. Defaults to 800.
        '''

        pygame.init()
        self.width = width
        self.height = height
        
        self.screen = self.__create_window()
        
        self.buttons = []

        self.__clicked_facelet = None
        self.__clicked_button = None
        self.__mouse_pressed = False

        self.__displayed_quadrilaterals = []
        self.__displayed_quadrilaterals_indices = []
        
    def detect_facelet_click(self, mouse_pos):
        '''Updates __clicked_facelet to the index of the clicked facelet if a click is detected.

        Args:
            mouse_pos (tuple[int, int]): The position of the mouse on the screen.
        '''

        def __is_point_inside_quadrilateral(quad, P):
            '''Algorithm to determine if a coordinate P lies within the bounds of a (convex) quadrilateral. 

            Args:
                quad (List[np.array]): list of (2D) coordinates of the corners of the quadrilateral. 
                P (np.array): 2D coordinate.

            Returns:
                boolean: True if P inside quad; False otherwise.
            '''

            A, B, C, D = np.array(quad[0]), np.array(quad[1]), np.array(quad[2]), np.array(quad[3])
            P = np.array(P)
            ab, ac, ad = B-A, C-A, D-A
            pa, pb, pc, pd = A-P, B-P, C-P, D-P
            area = lambda x, y : np.linalg.norm(np.cross(x,y)) 
            quad_area = area(ab, ac) + area(ac,ad) # This is actually 2x but irrelevent
            total_area = area(pa, pb) + area(pb,pc) + area(pc, pd) + area(pd, pa)
            relative_error = abs((total_area-quad_area) / quad_area)          
            return relative_error < 0.001 # an arbitrary (small) value 

        for i, quad in enumerate(self.__displayed_quadrilaterals):
            if __is_point_inside_quadrilateral(quad, mouse_pos):

                self.__clicked_facelet = self.__displayed_quadrilaterals_indices[i]

    def get_clicked_facelet(self):
        '''Retrieves most recently clicked facelet.

        Returns:
            int: Index of clicked facelet.
        '''
        return_facelet = self.__clicked_facelet
        self.__clicked_facelet = None
        return return_facelet

    def __create_window(self):
        '''Creates a pygame window. 

        Returns:
            pygame.Surface: screen
        '''
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Cube Solver')
        icon = pygame.image.load('resources/rubick.png')
        pygame.display.set_icon(icon)
        return screen

    def display_move_text(self, move_count, move):
        '''Displays the notation of the move being made by the solver, and the number of moves remaining.

        Args:
            move_count (int): Number of moves left until cube is solved.
            move (Move): Move to display.
        '''

        font = pygame.font.Font('resources/pixel_font.ttf', 80)

        move_text = font.render(f"{Data.move_notation_for_display[move]}", True, (0, 0, 51))
        move_count_text = font.render(f"{move_count}", True, (0, 0, 51))

        move_text_rect = move_text.get_rect(center=(0.5 * self.width, 0.75 * self.height))
        move_count_text_rect = move_count_text.get_rect(center=(0.85 * self.width, 0.15 * self.height))

        self.screen.blit(move_text, move_text_rect)
        self.screen.blit(move_count_text, move_count_text_rect)

    def display_text(self, text, size = 80):
        '''Displays given text at the top region of the screen. 

        Args:
            text (str): Text to display on screen. 
            size (int, optional): Size of the text to display. Defaults to 80.
        '''

        font = pygame.font.Font('resources/pixel_font.ttf', size)
        text = font.render(text, True, (0, 0, 51))
        text_rect = text.get_rect(center=(0.5 * self.width, 0.2 * self.height))
       
        self.screen.blit(text, text_rect)

    def display_info(self,instructions):
        '''Displays instructions on how to use different parts of the program.

        Args:
            instructions (str): Instructions.
        '''

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
            y_offset += 30

    def update_mouse(self, mouse_pressed, mouse_pos, keys):
        '''Checks if the mouse has been clicked, and by extension, a facelet. 
        Also calls methods to check if a GUI button has been clicked or its keyboard button pressed.

        Args:
            mouse_pressed (Tuple[int]): Pressed mouse buttons. 
            mouse_pos (Tuple[int, int]): Mouse position on screen.
            keys (Tuple[int]): Pressed keyboard buttons. 
        '''

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        if any(mouse_pressed): 
            self.__mouse_pressed = True
        elif self.__mouse_pressed == True:
            self.__mouse_pressed = False # mouse released (falling edge)
            self.detect_facelet_click(mouse_pos)

        self.detect_button_click(mouse_pressed, mouse_pos, keys)

    def clear_screen(self):
        '''Clears the screen and displayed quadrilateral data. 
        '''
        self.screen.fill((255, 255, 255))
        self.__displayed_quadrilaterals, self.__displayed_quadrilaterals_indices = [], []
    
    def draw_line(self, a, b, colour):
        '''Draws a line between two points in a given colour.

        Args:
            a (Tuple[int, int]): Start point of line
            b (Tuple[int, int]): End point of line
            colour (Tuple[int, int, int]): Colour to draw line with. 
        '''
        pygame.draw.line(self.screen, colour, a, b, 6)

    def draw_quadrilateral(self, corners, colour):
        '''Draws a filled quadrilateral with given corners, and colour.

        Args:
            corners (np.array[Tuple[int,int]]): Screen coordinates of corners of quadrilaterals to draw. 
            colour (Tuple[int, int, int]): Colour to draw line with.
        '''
        if colour:
            pygame.draw.polygon(self.screen, colour, corners)
        else:
            pygame.draw.polygon(self.screen, 'black', corners)
        pygame.draw.polygon(self.screen, 'black', corners, 4)

    def add_displayed_quadrilateral(self, quadrilateral, index):
        '''Register a displayed quadrilateral (so that it can be included in checks for facelet clicks)

        Args:
            quadrilateral (np.array[Tuple[int,int]]): The quadrilateral to be added.
            index (int): The index of the quadrilateral (ie what Facelet it represents)
        '''

        self.__displayed_quadrilaterals.append(quadrilateral)
        self.__displayed_quadrilaterals_indices.append(index)

    def display_fps(self, fps):
        '''Displays an FPS counter
        Args:
            fps (int): FPS
        '''
        font = pygame.font.SysFont('Arial', 20)
        fps_text = font.render(f'FPS: {int(fps)}', True, (0,0,0))
        self.screen.blit(fps_text, (10, 10))

    def detect_button_click(self, mouse_pressed, mouse_pos, keys_pressed):
        '''
        Updates __clicked_button to the most recently clicked button.
        '''
        for button in self.buttons:
            if button.detect_click(mouse_pressed, mouse_pos, keys_pressed):
                self.__clicked_button = button
                
    def get_clicked_button(self):
        '''Retrives the most recently clicked button.

        Returns:
            Button: Clicked button.
        '''
        return_button = self.__clicked_button
        self.__clicked_button = None 
        return return_button
    
    def add_button(self, button):
        '''Adds a button to the button array.
        Args:
            button (Button): Button to add.
        '''
        self.buttons.append(button)
        
    def display_buttons(self):
        '''Calls methods to display each button in self.buttons.
        '''
        for button in self.buttons:
            button.display(self.screen)
    
class Button:
    '''A button.
    Includes debounce cooldown logic. 
    '''
    def __init__(self, name, image, x, y, size, key=None):
        '''Initialize key attributes

        Args:
            name (str): The 'name' of the button. Used to uniquely identify it.
            image (pygame.Surface): display image of the button. 
            x (int): top_left x coordinate.
            y (int): top_left y coordinate.
            size (Tuple[int, int]): Button dimensions.
            key (int, optional): Keyboard key to trigger button. Defaults to None.
        '''
        self.__key = key 
        self.__image = pygame.transform.scale(image, size)  # Resize the image to 100x100
        self.__rect = self.__image.get_rect()
        self.__rect.topleft = (x,y)
        
        self.name = name 
        
        self.__last_click_time = pygame.time.get_ticks()
        self.__debounce = 100 # 100 ms button debounce 
        self.__latch = False 
        
    def display(self, screen):
        '''Display the button the screen.

        Args:
            screen (pygame.Surface): screen object to display button on.
        '''
        screen.blit(self.__image, (self.__rect.x, self.__rect.y))
        
    def detect_click(self, mouse_pressed, mouse_pos, keys_pressed):
        '''Detect if the button has been clicked. 
        Include debounce-delay, and latching. 

        Args:
            mouse_pressed (Tuple[int]): Pressed mouse buttons. 
            mouse_pos (Tuple[int, int]): Mouse position on screen.
            keys (Tuple[int]): Pressed keyboard buttons. 
        Returns:
            boolean: True if click detected; False otherwise.
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
            self.__latch = False # force a period of no input before the next click. 

        return False 

            