class RubiksCube:
    def __init__(self):
        # Corner representation: permutation and orientation
        self.corners_permutation = [0, 1, 2, 3, 4, 5, 6, 7]  # Starts in solved state
        self.corners_orientation = [0, 0, 0, 0, 0, 0, 0, 0]  # All corners correctly oriented

        # Edge representation: permutation and orientation
        self.edges_permutation = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]  # Starts in solved state
        self.edges_orientation = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # All edges correctly oriented


        # Define face colors
        self.face_colors = {
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
        return (f"Corners: {self.corners_permutation}, {self.corners_orientation}\n"
                f"Edges: {self.edges_permutation}, {self.edges_orientation}")
    
    def get_2D_net(self):

        for i, permutation in enumerate(self.corners_permutation):
            corner_facelet = self.corner_facelets[i]
            corner_facelet_colours = [self.face_colors[j] for j in self.corner_facelets[permutation]]

            print(corner_facelet, corner_facelet_colours)

        # for each corner:
        # get the corresponding corner_facelet. ie for the first corner, it will be ['U', 'F', 'L']
        # get the corresponding colours from this. ie: ['W','G','O']
        # cycle the colours based off the corner orientation 
        # insert the colours into the 54 character face representation. 
        # this insertion can be based off a table 

        # ['x'] * 54
        
        # for the 54 character representation: 
        # "WWWWWWWWW RRRRRRRRR GGGGGGGGG YYYYYYYYY OOOOOOOOO BBBBBBBBB"  represents a solved cube 
        # "UUUUUUUUU RRRRRRRRR FFFFFFFFF DDDDDDDDD LLLLLLLLL BBBBBBBBB" 
        # each corner has a corresponding face index : ie UFL gives 0*6 + 6 = 6 because it is the 6th cube on the u face 

# 
        



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

# Perform a clockwise U rotation
rotator.rotate(cube, 'U')
rotator.rotate(cube, 'U\'')
print(cube)
cube.display_2D_net()