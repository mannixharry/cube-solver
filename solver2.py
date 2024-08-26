import pygame 
import sys 

class RubiksCube:
    def __init__(self):
        # Facelet string representation of the cube
        self.cube_string = list('TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTWOGRBYGBW')
                                          #OOOOOOOOOGGGGGGGGGRRRRRRRRRBBBBBBBBBYYYYYYYYY')

    def __repr__(self):
        cube_string = self.cube_string
        # Print the net representation
        return (f"   {cube_string[0:3]}\n"
                f"   {cube_string[3:6]}\n"
                f"   {cube_string[6:9]}\n"
                f"{cube_string[9:12]}{cube_string[18:21]}{cube_string[27:30]}{cube_string[36:39]}\n"
                f"{cube_string[12:15]}{cube_string[21:24]}{cube_string[30:33]}{cube_string[39:42]}\n"
                f"{cube_string[15:18]}{cube_string[24:27]}{cube_string[33:36]}{cube_string[42:45]}\n"
                f"   {cube_string[45:48]}\n"
                f"   {cube_string[48:51]}\n"
                f"   {cube_string[51:54]}\n")
    
    def display_2D_net(self):
        face_indices = ['U', 'L', 'F', 'R', 'B', 'D']
        pygame.init()

        # Define the dimensions
        block_size = 50  # Size of each square
        margin = 10  # Margin between squares

        # Define colors for faces
        color_map = {'W': (255, 255, 255),  # White
                     'Y': (255, 255, 0),    # Yellow
                     'G': (0, 255, 0),      # Green
                     'B': (0, 0, 255),      # Blue
                     'O': (255, 165, 0),    # Orange
                     'R': (255, 0, 0)}      # Red

        # Create the screen
        screen_width = 800
        screen_height = 800
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption('Rubik\'s Cube Net')

        # Get 2D net
        net_string = self.cube_string

        # Define positions based on net structure
        net_positions = {
            'U': (1, 0),  # Center top
            'L': (0, 1),  # Center left
            'F': (1, 1),  # Center middle
            'R': (2, 1),  # Center right
            'B': (3, 1),  # Center bottom
            'D': (1, 2)   # Bottom center
        }

        for face, (grid_x, grid_y) in net_positions.items():
            for i in range(3):
                for j in range(3):
                    color = color_map[net_string[face_indices.index(face) * 9 + i * 3 + j]]
                    pygame.draw.rect(screen, color, pygame.Rect(margin + (grid_x * 3 + j) * block_size,
                                                                margin + (grid_y * 3 + i) * block_size,
                                                                block_size, block_size))
        pygame.display.flip()

        # Run until the user asks to quit
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        pygame.quit()
        sys.exit()


class CubeRotations:

    def __init__(self):
        # Define the rotation tables for the edges around each face
        self.rotation_tables = {
            'U': [9, 10, 11, 27, 28, 29, 36, 37, 38, 18, 19, 20],  # Edges affected by rotating U face
            'D': [15, 16, 17, 24, 25, 26, 33, 34, 35, 42, 43, 44],  # Edges affected by rotating D face
            'F': [6, 7, 8, 18, 21, 24, 45, 46, 47, 44, 41, 38],    # Edges affected by rotating F face
            'B': [0, 1, 2, 36, 39, 42, 51, 52, 53, 26, 23, 20],    # Edges affected by rotating B face
            'L': [0, 3, 6, 9, 12, 15, 45, 48, 51, 35, 32, 29],     # Edges affected by rotating L face
            'R': [2, 5, 8, 38, 41, 44, 47, 50, 53, 27, 30, 33]     # Edges affected by rotating R face
        }

    def rotate_clockwise(self, cube, face):
        # Rotate the face itself
        self._rotate_face(cube, face, clockwise=True)
        # Rotate the edges around the face
        self._rotate_edges(cube, face, clockwise=True)

    def _rotate_face(self, cube, face, clockwise=True):
        face_start = 'ULFRBD'.index(face) * 9
        facelet_indices = [6, 3, 0, 7, 4, 1, 8, 5, 2]

        if clockwise:
            # Shift the facelet positions clockwise
            new_face = [cube.cube_string[face_start + facelet_indices[i]] for i in range(9)]
        else:
            # Shift the facelet positions anticlockwise
            new_face = [cube.cube_string[face_start + facelet_indices[i]] for i in range(9)]
            
        # Assign the new positions back to the face
        for i in range(9):
            cube.cube_string[face_start + i] = new_face[i]

    def _rotate_edges (self, cube, face, clockwise = True):
        return 
    





                
def main():
    # Example usage:
    cube = RubiksCube()
    # Instantiate the rotation logic
    rotator = CubeRotations()

    # Perform some rotations
    #rotator.rotate(cube, 'U')
    rotator.rotate_clockwise(cube, 'D')
    print(cube)
    
    engine.main(cube.cube_string)

import engine 

if __name__ == "__main__":
    main()
    
# take the colours on the face and rotate them clockwise
# cycle the edges in threes 