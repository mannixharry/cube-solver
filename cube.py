from data import *
import math 

class CubieCube:
    def __init__(self, cube_input=None):
        
        '''
        The cubie-cube representation stores the configuration of a cube using a set of four arrays. 
        It is this form of the cube, which we apply the rotation logic to.
        '''

        # Initialize the configuration arrays for a solved cube. 
        self.corner_permutations = list(range(8))
        self.corner_orientations = [0] * 8
        self.edge_permutations = list(range(12))
        self.edge_orientations = [0] * 12
        
        # Load the dictionaries used for rotation from Data.
        self.corner_permutation_dict, self.corner_orientation_dict, self.edge_permutation_dict, self.edge_orientation_dict = Data.cubie_move_dicts
        
        def load_configuration_from(cube_input): # Helper procedure to copy configuration from an input cubie_cube. (avoids repetition)
            self.corner_permutations = cube_input.corner_permutations
            self.corner_orientations = cube_input.corner_orientations
            self.edge_permutations = cube_input.edge_permutations 
            self.edge_orientations = cube_input.edge_orientations 

        # Handles the cube_input parameter 
        if cube_input is not None:
            if isinstance(cube_input, FaceletCube): # Checks to see if a Facelet-Cube is input.
                load_configuration_from(cube_input.to_cubie_cube())
            elif isinstance(cube_input, CubieCube): # Checks to see if a Cubie-Cube is input.
                load_configuration_from(cube_input)
            elif isinstance(cube_input, str): # Checks to see if a string is input.
                load_configuration_from(FaceletCube(cube_input).to_cubie_cube())
            else:
                raise TypeError('cube_input does not match an expected type')

    # This procedure manages cubie-cube rotations.                
    def rotate_clockwise(self, move):

        '''
        Move is given as an integer between 0-17. Move modulo 6 gives the face being turned. Whilst (Move div 6) + 1 gives the number of times
        the face is turned. This is by convention. 

        The rotation is executed in four groups of three steps:
        For each aspect of the transformation - ie both permutations and orientations: 
            - Load the relevent map and initialize tempory arrays.
            - Use the map to apply the transformation and store in temporary arrays.
            - Update the cube configuration using the values in the arrays.

        For the orientations, modular arithmatic is used. The final orientation of a corner is calculated as the sum of the original orientation and the orientation change given by the map modulo 3. 
        The reason why this works can be easily verified. For example: a clockwise rotation on a clockwise twisted corner will give a final twist of (1 + 1) = 2 (mod 3). This is an anticlockwise twist.
        The same principle applies for clockwise twists, only modulo 2 is used intead to represent the flip of a piece. 

        (We define by convention the orientation of a corner as its twist and the orientation as an edge as its flip)
        '''
        
        turn_count = 1 + (move // 6) # The procedure rotates a face clockwise only. Double and anti-clockwise rotation are achieved through repetition.
        face = move % 6 

        for t in range(turn_count):

            # Loads the corner_permutation map for the face being turned and initializes temporary arrays.
            corner_permutation_map = self.corner_permutation_dict[face]
            new_corner_permutations = [0] * 8
            new_corner_orientations = [0] * 8

            # Applies the permutation map to both corner arrays, and populates the new arrays. 
            for i in range(8):
                new_corner_permutations[i] = self.corner_permutations[corner_permutation_map[i]]
                new_corner_orientations[i] = self.corner_orientations[corner_permutation_map[i]] # It is imperative to also permute the information regarding the orientation of the corners.
            
            # Update the configuration.
            self.corner_permutations = new_corner_permutations
            self.corner_orientations = new_corner_orientations

            # Load. 
            corner_orientation_map = self.corner_orientation_dict[face]

            # Apply map.
            for i in range(8):
                new_corner_orientations[i] = (self.corner_orientations[i] + corner_orientation_map[i]) % 3 # Note the use of modular arithmetic. 

            # Update.
            self.corner_orientations = new_corner_orientations


            # Logic for the edges is largely the same as for the corners (above).
            edge_permutation_map = self.edge_permutation_dict[face]
            new_edge_permutations = [0] * 12
            new_edge_orientations = [0] * 12

            for i in range(12):
                new_edge_permutations[i] = self.edge_permutations[edge_permutation_map[i]]
                new_edge_orientations[i] = self.edge_orientations[edge_permutation_map[i]]

            self.edge_permutations = new_edge_permutations
            self.edge_orientations = new_edge_orientations

            edge_orientation_table = self.edge_orientation_dict[face]

            for i in range(12):
                new_edge_orientations[i] = (self.edge_orientations[i] + edge_orientation_table[i]) % 2 

            self.edge_orientations = new_edge_orientations
            
        # Procedure to display the configuration of the cube in the console. 
        def __repr__(self):
            return (f"Corner Permutations: {self.corner_permutations}\n"
                    f"Corner Orientations: {self.corner_orientations}\n"
                    f"Edge Permutations: {self.edge_permutations}\n"
                    f"Edge Orientations: {self.edge_orientations}\n")
        
class FaceletCube:
    def __init__(self, cube_input=None):
        
        self.corner_colour_table, self.edge_colour_table = Data.corner_colour_table, Data.edge_colour_table # These map colours to cubie pieces. 
        self.corner_facelet_indices, self.edge_facelet_indices = Data.corner_facelet_indices, Data.edge_facelet_indices # These map pieces to their facelets. ie: UFL to U6, L2, F0.

        self.colours_on_face_map = Data.colours_on_face_map # Used to cycle the colours on a face.
        
        # Initialize the facelet representation of a solved cube. 
        self.facelets = list('WWWWWWWWWGGGGGGGGGOOOOOOOOORRRRRRRRRBBBBBBBBBYYYYYYYYY')

        # Handles the cube_input parameter. 
        if cube_input is not None:
            if isinstance(cube_input, FaceletCube):
                self.facelets = cube_input.facelets
            elif isinstance(cube_input, str):
                self.facelets = list(cube_input)
            elif isinstance(cube_input, CubieCube):
                self.facelets = self.from_cubie_cube(cube_input).facelets
            else:
                raise TypeError('cube_input does not match an expected type')
    
    # Converts a cubie representation to a facelet representation. 
    def from_cubie_cube(self, cubie_cube):
        
        facelets = [''] * 54
        
        # Iteratively load the colour data for each corner into the facelet array.  
        for i in range(8):
            # Retrieve the piece code and orientation of the corner in position i. 
            permutation = cubie_cube.corner_permutations[i]
            orientation = cubie_cube.corner_orientations[i]
            for j in range(3):
                # Map the colours of the retrieved piece to the facelet indices of the position. 
                facelets[self.corner_facelet_indices[i][j]] = (self.corner_colour_table[permutation])[(j+orientation)%3]

        # Load the colour data for each edge into the facelet array. 
        for i in range(12):
            permutation = cubie_cube.edge_permutations[i]
            orientation = cubie_cube.edge_orientations[i]
            for j in range(2):
                facelets[self.edge_facelet_indices[i][j]] = self.edge_colour_table[permutation][(j + orientation) % 2]

        # Fill the centre pieces (these are fixed).
        centre_colours = ['W', 'G', 'O', 'R', 'B', 'Y']
        centre_indices = [Facelet.U4, Facelet.F4, Facelet.L4, Facelet.R4, Facelet.B4, Facelet.D4]
        for i in range(6):
            facelets[centre_indices[i]] = centre_colours[i]
        
        # Create a facelet_cube with the calculated facelets to return.
        facelet_string = str(''.join(facelets))
        facelet_cube = FaceletCube(facelet_string)
        return facelet_cube
    
    # Converts a facelet representation of a cube to a cubie representation. 
    def to_cubie_cube(self):
        
        # Initialize a new cubie_cube and temporary variables. 
        cubie_cube = CubieCube()

        # Initialize the configuration arrays for a solved cube (temporary). 
        new_corner_permutations = list(range(8))
        new_corner_orientations = [0] * 8
        new_edge_permutations = list(range(12))
        new_edge_orientations = [0] * 12

        for i, corner_index in enumerate(self.corner_facelet_indices): 
            # Get the colours for the current corner's facelets
            colours = [self.facelets[idx] for idx in corner_index]

            # Determine the orientation based on the index of 'W' or 'Y' in the colours array. 
            orientation = (colours.index('W') if 'W' in colours else colours.index('Y'))

            # Reverse the orientation of the colours (by cycling the array) so they can be used to find the piece.
            oriented_colours = [colours[(j + orientation) % 3] for j in range(3)]
            permutation = self.corner_colour_table.index(oriented_colours)

            # Assign to the respective corner arrays
            new_corner_permutations[i] = permutation
            new_corner_orientations[i] = orientation
    
        for i, edge_index in enumerate(self.edge_facelet_indices): 
            # Get the colors for the current edge's facelets
            colours = [self.facelets[idx] for idx in edge_index]

            # Determine the orientation based on the index as before. 
            orientation_colors = ['W', 'Y', 'G', 'B']
            orientation = next(colours.index(color) for color in orientation_colors if color in colours)

            oriented_colours = [colours[(j - orientation) % 2] for j in range(2)]
            permutation = self.edge_colour_table.index(oriented_colours)

            # Assign to the respective edge arrays
            new_edge_permutations[i] = permutation
            new_edge_orientations[i] = orientation
        
        # Update the new cubie-cube's configuration. 
        cubie_cube.corner_permutations = new_corner_permutations
        cubie_cube.corner_orientations = new_corner_orientations
        cubie_cube.edge_permutations = new_edge_permutations
        cubie_cube.edge_orientations = new_edge_orientations
        
        return cubie_cube
    
    # This cycles the colours on a single face (applies a move but only the colours on a face).
    def rotate_colours_on_face(self, move):
        face = move % 6
        move_count = 1 + (move // 6)

        start_pointer = 9 * face # This is the index of the first facelet on the face. 

        face_indices = self.facelets[start_pointer : start_pointer + 9] # Isolate the face.
        for i in range(move_count):
            new_face_indices = [0] * 9
            # Cycle the colours using the colours_on_face_map.
            for j in range(9):
                new_face_indices[j] = face_indices[self.colours_on_face_map[j]] 
            face_indices = new_face_indices
        # Update the configuration.
        for i in range(9):
            self.facelets[i+start_pointer] = face_indices[i]
        
    def __repr__(self):
        return ''.join(self.facelets)

  
class CoordCube:
    
    def __init__(self, cube_input=None):

        # Import move tables for rotations and transitions
        try: 
            self.g1_move_tables = [Move_Tables.corner_orientation_table, Move_Tables.edge_orientation_table, Move_Tables.UD_slice_permutation_table]
            self.g2_move_tables = [Move_Tables.eight_edge_permutation_table, Move_Tables.four_edge_permutation_table, Move_Tables.corner_permutation_table]
        except:
            pass
            
        # Inialize the CoordCube representation of a solved cube. 
        self.corner_orientation_coordinate = self.edge_orientation_coordinate = self.UD_slice_coordinate = 0
        self.eight_edge_permutation_coordinate = self.four_edge_permutation_coordinate = self.corner_permutation_coordinate = 0

        self.cubie_cube = CubieCube()

        # Load cube configuration.
        if cube_input is not None:

            if isinstance(cube_input, CoordCube):

                self.corner_orientation_coordinate = cube_input.corner_orientation_coordinate
                self.edge_orientation_coordinate = cube_input.edge_orientation_coordinate
                self.UD_slice_coordinate = cube_input.UD_slice_coordinate
                self.eight_edge_permutation_coordinate = cube_input.eight_edge_permutation_coordinate
                self.four_edge_permutation_coordinate = cube_input.four_edge_permutation_coordinate
                self.corner_permutation_coordinate = cube_input.corner_permutation_coordinate

                self.cubie_cube = None # Unnecessary since calculate_..._coordinate will never be called (as coordinates already determined)
                
            if isinstance(cube_input, CubieCube):
        
                # Initialize coordinates from the corner and edge orientations
                print('worked')
                self.cubie_cube = cube_input

                self.corner_orientation_coordinate = self.calculate_corner_orientation_coordinate()
                self.edge_orientation_coordinate = self.calculate_edge_orientation_coordinate()
                self.UD_slice_coordinate = self.calculate_UD_slice_coordinate()
                self.eight_edge_permutation_coordinate = self.calculate_eight_edge_permutation_coordinate()
                self.four_edge_permutation_coordinate = self.calculate_four_edge_permutation_coordinate()
                self.corner_permutation_coordinate = self.calculate_corner_permutation_coordinate()


        
        self.g1_coordinates = [self.corner_orientation_coordinate, self.edge_orientation_coordinate, self.UD_slice_coordinate]
        self.g2_coordinates = [self.eight_edge_permutation_coordinate, self.four_edge_permutation_coordinate, self.corner_permutation_coordinate]

    def get_g1_coordinates(self):
        return self.g1_coordinates
    
    def get_g2_coordinates(self):
        return self.get_g2_coordinates
    
    def update_coordinates(self):
        self.corner_orientation_coordinate, self.edge_orientation_coordinate, self.UD_slice_coordinate = self.g1_coordinates
        self.eight_edge_permutation_coordinate, self.four_edge_permutation_coordinate, self.corner_permutation_coordinate = self.g2_coordinates
    
    def rotate_clockwise(self, move):

        # Update coordinates based on move
        self.g1_coordinates = [(self.g1_move_tables[i])[str(self.g1_coordinates[i])][move] for i in range(3)]
        self.g2_coordinates = [(self.g2_move_tables[i])[str(self.g2_coordinates[i])][move] for i in range(3)]

        self.update_coordinates()

    def __repr__(self):
        return str((self.corner_orientation_coordinate, self.edge_orientation_coordinate, self.UD_slice_coordinate, self.eight_edge_permutation_coordinate, self.UD_edge_permutation_coordinate, self.corner_permutation_coordinate))
    # Calculation methods for each coordinate

    def calculate_corner_orientation_coordinate(self):
        # Converts corner orientations to a unique integer (range 0 to 3^7-1)
        return sum(self.cubie_cube.corner_orientations[i] * (3 ** i) for i in range(7))

    def calculate_edge_orientation_coordinate(self):
        # Converts edge orientations to a unique integer (range 0 to 2^11-1)
        return sum(self.cubie_cube.edge_orientations[i] * (2 ** i) for i in range(11))
    
    def calculate_UD_slice_coordinate(self):
        # Converts UD slice positions to a unique integer
        slice_indices = [1 if i in [8, 9, 10, 11] else 0 for i in self.cubie_cube.edge_permutations]
        UD_slice_coordinate = 0
        occupied_count = 0
        start_counting = False  # Flag to start counting after the first '1'

        for i in range(12):
            if not start_counting:
                if slice_indices[i] == 1:
                    start_counting = True
            elif slice_indices[i] == 0:
                UD_slice_coordinate += math.comb(i, occupied_count) 
            else:
                occupied_count += 1 
             
        return UD_slice_coordinate
    
    def calculate_corner_permutation_coordinate(self):
        corner_permutation_coordinate = 0
        for i in range(8):
            # Count elements to the right of i that are smaller than element i
            smaller_count = sum(1 for j in range(i) if self.cubie_cube.corner_permutations[j] > self.cubie_cube.corner_permutations[i])
            corner_permutation_coordinate += smaller_count * math.factorial(i)
        return corner_permutation_coordinate

    def calculate_eight_edge_permutation_coordinate(self):
        eight_edge_permutation_coordinate = 0
        for i in range(8):
            # Count elements to the right of i that are smaller than element i
            smaller_count = sum(1 for j in range(i) if self.cubie_cube.edge_permutations[j] > self.cubie_cube.edge_permutations[i])
            eight_edge_permutation_coordinate += smaller_count * math.factorial(i)
        return eight_edge_permutation_coordinate

    def calculate_four_edge_permutation_coordinate(self):
        UD_edge_permutation_coordinate = 0
        for i in range(4):
            # Similar logic but for UD edges
            smaller_count = sum(1 for j in range(i) if self.cubie_cube.edge_permutations[j + 8] > self.cubie_cube.edge_permutations[i + 8])
            UD_edge_permutation_coordinate += smaller_count * math.factorial(i)
        return UD_edge_permutation_coordinate
    
def main():
    pass

if __name__ == '__main__':
    main()


