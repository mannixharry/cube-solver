import pygame 
import sys 

class RubiksCube:
    def __init__(self):
        # Facelet string representation of the cube
        self.cube_string = list('WWWWWWWWWOOOOOOOOOGGGGGGGGGRRRRRRRRRBBBBBBBBBYYYYYYYYY')
                                    
    def __repr__(self):
        cube_string = self.cube_string
        # Print the net representation
        return (f"               {cube_string[0:3]}\n"
                f"               {cube_string[3:6]}\n"
                f"               {cube_string[6:9]}\n"
                f"{cube_string[9:12]}{cube_string[18:21]}{cube_string[27:30]}{cube_string[36:39]}\n"
                f"{cube_string[12:15]}{cube_string[21:24]}{cube_string[30:33]}{cube_string[39:42]}\n"
                f"{cube_string[15:18]}{cube_string[24:27]}{cube_string[33:36]}{cube_string[42:45]}\n"
                f"               {cube_string[48:51]}\n"
                f"               {cube_string[45:48]}\n"
                f"               {cube_string[51:54]}\n")
    
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
        self.encoded_rotation_tables = {
            'F' : ['U6', 'U7', 'U8', 'R0', 'R3', 'R6', 'D2', 'D1', 'D0', 'L8', 'L5', 'L2']
        }
        
        self.rotation_tables = {key: ['ULFRBD'.index(i[0])*9 + int(i[1]) for i in value] for (key, value) in self.encoded_rotation_tables.items()}
        
        print(self.encoded_rotation_tables)
        print(self.rotation_tables)
        
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
        rotation_table = self.rotation_tables[face]
        new_cube = cube.cube_string[:] #creates a new list rather than creating a reference
        for i, index in enumerate(rotation_table):
            new_cube[rotation_table[(i+3)%12]] = cube.cube_string[index]
            print(f"{index} ==> {rotation_table[(i+3)%12]}")
            
        for i in range(54):
            
            cube.cube_string[i] = new_cube[i]
        
                
def main():
    # Example usage:
    cube = RubiksCube()
    # Instantiate the rotation logic
    rotator = CubeRotations()

    # Perform some rotations
    rotator.rotate_clockwise(cube, 'F')
    rotator.rotate_clockwise(cube, 'F')
    
   
    #rotator.rotate_clockwise(cube, 'D')
    print(cube)
    print(cube.cube_string)
    engine.main(cube.cube_string)


import engine 

if __name__ == "__main__":
    main()
    
# take the colours on the face and rotate them clockwise
# cycle the edges in threes 