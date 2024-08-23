import pygame 
import sys 

class RubiksCube:
    def __init__(self):
        # Corner representation: permutation and orientation
        self.corners_permutation = [0, 1 , 2, 3, 4, 5, 6, 7]  # Starts in solved state
        self.corners_orientation = [0, 0, 0, 0, 0, 0, 0, 0]  # All corners correctly oriented

        # Edge representation: permutation and orientation
        self.edges_permutation = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # Starts in solved state
        self.edges_orientation = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # All edges correctly oriented
        
        # Define face colours
        self.face_colours = {
            'U': 'W',  # White
            'D': 'Y',  # Yellow
            'F': 'G',  # Green
            'B': 'B',  # Blue
            'L': 'O',  # Orange
            'R': 'R'   # Red
        }

        # Define the facelet positions for corners and edges
        self.corner_facelets = [
            ['U', 'F', 'L'], ['U', 'F', 'R'], ['U', 'B', 'L'], ['U', 'B', 'R'],
            ['D', 'F', 'L'], ['D', 'F', 'R'], ['D', 'B', 'L'], ['D', 'B', 'R']
        ]
        self.edge_facelets = [
            ['U', 'F'], ['U', 'R'], ['U', 'B'], ['U', 'L'],
            ['D', 'F'], ['D', 'R'], ['D', 'B'], ['D', 'L'],
            ['F', 'R'], ['R', 'B'], ['B', 'L'], ['L', 'F']
        ]

    def __repr__(self):
        
        cube_string = self.get_2D_net()
        
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

        # Define positions based on net structure
        net_positions = {
            'U': (3, 0),  # Center top
            'L': (0, 1),  # Center left
            'F': (1, 1),  # Center middle
            'R': (2, 1),  # Center right
            'B': (3, 1),  # Center bottom
            'D': (1, 2)   # Bottom center
        }

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
        net_string = self.get_2D_net()

        # Draw the net
        screen.fill((54, 69, 79))  # Fill background with black
        # Define positions based on net structure
        net_positions = {
            'U': (1, 0),  # White face moved 2 squares to the left (relative to 'F') and positioned above 'F'
            'L': (0, 1),  # Center left
            'F': (1, 1),  # Center middle (Green face)
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

        
    def get_2D_net(self):
        
        net = ['x'] * 54 
        
        face_indices = ['U', 'L', 'F', 'R', 'B', 'D']     
  
        net_insertion_table = {
            'U': [['B', 'L'], ['B'], ['B', 'R'], ['L'], 'x', ['R'], ['F', 'L'], ['F'], ['F', 'R']],
            'D': [['F', 'L'], ['F'], ['F', 'R'], ['L'], 'x', ['R'], ['B', 'L'], ['B'], ['B', 'R']],
            'F': [['U', 'L'], ['U'], ['U', 'R'], ['L'], 'x', ['R'], ['D', 'L'], ['D'], ['D', 'R']],
            'B': [['U', 'R'], ['U'], ['U', 'L'], ['R'], 'x', ['L'], ['D', 'R'], ['D'], ['D', 'L']],
            'L': [['U', 'B'], ['U'], ['U', 'F'], ['B'], 'x', ['F'], ['D', 'B'], ['D'], ['D', 'F']],
            'R': [['U', 'F'], ['U'], ['U', 'B'], ['F'], 'x', ['B'], ['D', 'F'], ['D'], ['D', 'B']]
        }
        
        for i, face in enumerate(face_indices):
            face_colour = self.face_colours[face]
            net[i*9 + 4] = face_colour

        for i, (permutation, orientation) in enumerate(zip(self.corners_permutation, self.corners_orientation)):
            corner_facelet = self.corner_facelets[i]
            colours = [self.face_colours[j] for j in self.corner_facelets[permutation]]
            match orientation:
                case 0:
                    oriented_piece = colours
                case 1:
                    oriented_piece = colours[2:] + colours[:2]
                case 2:
                    oriented_piece = colours[1:] + colours[:1]
            
            for i, face in enumerate(corner_facelet):
                index = face_indices.index(face) * 9 + net_insertion_table[face].index(corner_facelet[:i] + corner_facelet[i+1:])
                net[index] = oriented_piece[i]
        
        for i, (permutation, orientation) in enumerate(zip(self.edges_permutation, self.edges_orientation)):
            edge_facelet = self.edge_facelets[i]
            colours = [self.face_colours[j] for j in self.edge_facelets[permutation]]
            match orientation:
                case 0:
                    oriented_piece = colours
                case 1: 
                    oriented_piece = colours[:1] + colours [:0]
            
            for i, face in enumerate(edge_facelet):
                index = face_indices.index(face) * 9 + net_insertion_table[face].index(edge_facelet[:i] + edge_facelet[i+1:])
                net[index] = oriented_piece[i]

        character_representation = ''.join(net)
        return character_representation
    


class CubeRotations:
    def __init__(self):
        # Define the corner and edge rotation tables
        self.corner_rotations = {
            'U': [3, 0, 1, 2, 4, 5, 6, 7],
            'D': [0, 1, 2, 3, 7, 4, 5, 6],
            'F': [4, 0, 2, 6, 5, 1, 3, 7],
            'B': [0, 1, 5, 4, 2, 3, 7, 6],
            'L': [1, 5, 2, 0, 4, 6, 7, 3],
            'R': [0, 2, 6, 4, 1, 3, 7, 5],
        }

        self.edge_rotations = {
            'U': [3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11],
            'D': [0, 1, 2, 3, 8, 5, 6, 7, 11, 10, 9, 4],
            'F': [8, 0, 2, 10, 4, 1, 3, 11, 5, 9, 7, 6],
            'B': [0, 1, 9, 8, 2, 3, 11, 10, 4, 5, 7, 6],
            'L': [1, 8, 3, 9, 0, 4, 2, 10, 5, 6, 7, 11],
            'R': [0, 2, 10, 11, 1, 3, 9, 8, 4, 5, 6, 7],
        }

        # Inverse rotations are derived from the original rotation tables
        self.corner_inverse_rotations = {face: self.inverse_permutation(self.corner_rotations[face]) for face in self.corner_rotations}
        self.edge_inverse_rotations = {face: self.inverse_permutation(self.edge_rotations[face]) for face in self.edge_rotations}

        # Define the corner and edge orientation changes for each rotation
        self.corner_orientations = {
            'U': [0, 0, 0, 0, 0, 0, 0, 0],
            'D': [0, 0, 0, 0, 0, 0, 0, 0],
            'F': [2, 1, 0, 1, 0, 2, 2, 1],
            'B': [1, 2, 0, 2, 0, 1, 1, 2],
            'L': [1, 2, 0, 0, 2, 1, 1, 2],
            'R': [2, 1, 2, 1, 0, 1, 0, 1],
        }

        self.edge_orientations = {
            'U': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'D': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'F': [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0],
            'B': [1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1],
            'L': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            'R': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        }

        # Inverse orientations are the same for each move (reversed effect)
        self.corner_inverse_orientations = {face: self.inverse_orientations(self.corner_orientations[face]) for face in self.corner_orientations}
        self.edge_inverse_orientations = {face: self.inverse_orientations(self.edge_orientations[face]) for face in self.edge_orientations}

    def inverse_permutation(self, permutation):
        inverse = [0] * len(permutation)
        for i, p in enumerate(permutation):
            inverse[p] = i
        return inverse

    def inverse_orientations(self, orientations):
        return [(3 - ori) % 3 if ori != 0 else 0 for ori in orientations]

    def rotate_clockwise(self, cube, face):
        # Apply the rotation to the cube using the stored tables
        new_corners_perm = [0] * 8
        for i in range(8):
            new_corners_perm[i] = cube.corners_permutation[self.corner_rotations[face][i]]
        cube.corners_permutation = new_corners_perm

        for i in range(8):
            cube.corners_orientation[i] = (cube.corners_orientation[i] + self.corner_orientations[face][i]) % 3

        new_edges_perm = [0] * 12
        for i in range(12):
            new_edges_perm[i] = cube.edges_permutation[self.edge_rotations[face][i]]
        cube.edges_permutation = new_edges_perm

        for i in range(12):
            cube.edges_orientation[i] = (cube.edges_orientation[i] + self.edge_orientations[face][i]) % 2

    def rotate_anticlockwise(self, cube, face):
        # Apply the inverse rotation to the cube
        new_corners_perm = [0] * 8
        for i in range(8):
            new_corners_perm[i] = cube.corners_permutation[self.corner_inverse_rotations[face][i]]
        cube.corners_permutation = new_corners_perm

        for i in range(8):
            cube.corners_orientation[i] = (cube.corners_orientation[i] + self.corner_inverse_orientations[face][i]) % 3

        new_edges_perm = [0] * 12
        for i in range(12):
            new_edges_perm[i] = cube.edges_permutation[self.edge_inverse_rotations[face][i]]
        cube.edges_permutation = new_edges_perm

        for i in range(12):
            cube.edges_orientation[i] = (cube.edges_orientation[i] + self.edge_inverse_orientations[face][i]) % 2

    def rotate(self, cube, notation):
        face = notation[0]
        if len(notation) > 1 and notation[1] == '\'':
            self.rotate_anticlockwise(cube, face)
        else:
            self.rotate_clockwise(cube, face)
                

# Example usage:
cube = RubiksCube()
# Instantiate the rotation logic
rotator = CubeRotations()


print(cube)
print(cube.get_2D_net())
cube.display_2D_net()