from data import *
import math 
import random 
import json 

class MoveTables():
    def __init__(self):
        with open('move_tables/corner_orientation_table.json', 'r') as file:
            self.corner_orientation_table = json.load(file)
        with open('move_tables/edge_orientation_table.json', 'r') as file:
            self.edge_orientation_table = json.load(file)
        with open('move_tables/UD_slice_permutation_table.json', 'r') as file:
            self.UD_slice_permutation_table = json.load(file)
        with open('move_tables/four_edge_permutation_table.json', 'r') as file:
            self.four_edge_permutation_table = json.load(file)
        with open('move_tables/eight_edge_permutation_table.json', 'r') as file:
            self.eight_edge_permutation_table = json.load(file)
        with open('move_tables/corner_permutation_table.json', 'r') as file:
            self.corner_permutation_table = json.load(file) 
            
def import_tables():
    global move_tables
    move_tables = MoveTables()
    
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
        self.__corner_permutation_dict, self.__corner_orientation_dict, self.__edge_permutation_dict, self.__edge_orientation_dict = Data.cubie_move_dicts
        
        self.__corner_colour_table, self.__edge_colour_table = Data.corner_colour_table, Data.edge_colour_table # These map colours to cubie pieces. 
        self.__corner_facelet_indices, self.__edge_facelet_indices = Data.corner_facelet_indices, Data.edge_facelet_indices # These map pieces to their facelets. ie: UFL to U6, L2, F0.
 
        def __load_configuration_from(cube_input): # Helper procedure to copy configuration from an input cubie_cube. (avoids repetition)
            self.corner_permutations = cube_input.corner_permutations
            self.corner_orientations = cube_input.corner_orientations
            self.edge_permutations = cube_input.edge_permutations 
            self.edge_orientations = cube_input.edge_orientations 

        # Handles the cube_input parameter 
        if cube_input is not None:
            if isinstance(cube_input, FaceletCube): # Checks to see if a Facelet-Cube is input.
                __load_configuration_from(self.__from_facelet_cube(cube_input))
            elif isinstance(cube_input, CubieCube): # Checks to see if a Cubie-Cube is input.
                __load_configuration_from(cube_input)
            elif isinstance(cube_input, str): # Checks to see if a string is input.
                __load_configuration_from(self.__from_facelet_cube(FaceletCube(cube_input)))
            else:
                raise TypeError('cube_input does not match an expected type')

    # Converts a facelet representation of a cube to a cubie representation. 
    def __from_facelet_cube(self, facelet_cube):

        # Initialize a new cubie_cube and temporary variables. 
        cubie_cube = CubieCube()

        # Initialize the configuration arrays for a solved cube (temporary). 
        new_corner_permutations = list(range(8))
        new_corner_orientations = [0] * 8
        new_edge_permutations = list(range(12))
        new_edge_orientations = [0] * 12

        for i, corner_index in enumerate(self.__corner_facelet_indices): 
            # Get the colours for the current corner's facelets
            colours = [facelet_cube.facelets[idx] for idx in corner_index]

            # Determine the orientation based on the index of 'W' or 'Y' in the colours array. 
            orientation = -(colours.index('W') if 'W' in colours else colours.index('Y')) % 3

            # Reverse the orientation of the colours (by cycling the array) so they can be used to find the piece.
            oriented_colours = [colours[(j - orientation) % 3] for j in range(3)]
            permutation = self.__corner_colour_table.index(oriented_colours)

            # Assign to the respective corner arrays
            new_corner_permutations[i] = permutation
            new_corner_orientations[i] = orientation
    
        for i, edge_index in enumerate(self.__edge_facelet_indices): 
            # Get the colors for the current edge's facelets
            colours = [facelet_cube.facelets[idx] for idx in edge_index]

            # Determine the orientation based on the index as before. 
            orientation_colors = ['W', 'Y', 'G', 'B']
            orientation = next(colours.index(color) for color in orientation_colors if color in colours)

            oriented_colours = [colours[(j - orientation) % 2] for j in range(2)]
            permutation = self.__edge_colour_table.index(oriented_colours)

            # Assign to the respective edge arrays
            new_edge_permutations[i] = permutation
            new_edge_orientations[i] = orientation
        
        # Update the new cubie-cube's configuration. 
        cubie_cube.corner_permutations = new_corner_permutations
        cubie_cube.corner_orientations = new_corner_orientations
        cubie_cube.edge_permutations = new_edge_permutations
        cubie_cube.edge_orientations = new_edge_orientations

        return cubie_cube
    
    # This procedure manages cubie-cube rotations.                
    def move(self, move):

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
            corner_permutation_map = self.__corner_permutation_dict[face]
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
            corner_orientation_map = self.__corner_orientation_dict[face]

            # Apply map.
            for i in range(8):
                new_corner_orientations[i] = (self.corner_orientations[i] + corner_orientation_map[i]) % 3 # Note the use of modular arithmetic. 

            # Update.
            self.corner_orientations = new_corner_orientations

            # Logic for the edges is largely the same as for the corners (above).
            edge_permutation_map = self.__edge_permutation_dict[face]
            new_edge_permutations = [0] * 12
            new_edge_orientations = [0] * 12

            for i in range(12):
                new_edge_permutations[i] = self.edge_permutations[edge_permutation_map[i]]
                new_edge_orientations[i] = self.edge_orientations[edge_permutation_map[i]]

            self.edge_permutations = new_edge_permutations
            self.edge_orientations = new_edge_orientations

            edge_orientation_map = self.__edge_orientation_dict[face]

            for i in range(12):
                new_edge_orientations[i] = (self.edge_orientations[i] + edge_orientation_map[i]) % 2 

            self.edge_orientations = new_edge_orientations

    # Procedure to display the configuration of the cube in the console. 
    def __repr__(self):
        return (f"Corner Permutations: {self.corner_permutations}\n"
                f"Corner Orientations: {self.corner_orientations}\n"
                f"Edge Permutations: {self.edge_permutations}\n"
                f"Edge Orientations: {self.edge_orientations}\n")
    
    def verify_solvability(self):

        corner_twist_valid = sum(self.corner_orientations) % 3 == 0 # Check corner orientation validity

        edge_flip_valid = sum(self.edge_orientations) % 2 == 0    # Check edge orientation validity

        corner_permutation_parity = sum(
            x > y for i, x in enumerate(self.corner_permutations) for y in self.corner_permutations[i + 1:]
        ) % 2 # Check corner permutation parity

        edge_permutation_parity = sum(
            a > b for i, a in enumerate(self.edge_permutations) for b in self.edge_permutations[i + 1:]
        ) % 2 # Check edge permutation parity 

        # Parity consistency check
        # (Corner parity and edge parity are always the same for a solvable cube) 
        parity_consistent = corner_permutation_parity == edge_permutation_parity

        if corner_twist_valid and edge_flip_valid and parity_consistent:
            return True
        else:
            print(f"Error: The input cube is unsolvable."
                f"\nCorner Twisted: {not corner_twist_valid}"
                f"\nEdge Flipped: {not edge_flip_valid}"
                f"\nCorner Parity Consistent: {not corner_permutation_parity}"
                f"\nEdge Parity Consistent: {not edge_permutation_parity}"
            )
            return False
        
    def scramble(self):
         
        corner_permutations = list(range(8))
        corner_orientations = [0] * 8
        edge_permutations = list(range(12))
        edge_orientations = [0] * 12

        random.shuffle(corner_permutations)
        random.shuffle(edge_permutations)

        # Check parity 
        corner_permutation_parity = sum(
            a > b for i, a in enumerate(corner_permutations) for b in corner_permutations[i + 1:]
        ) % 2
        edge_permutation_parity = sum(
            a > b for i, a in enumerate(edge_permutations) for b in edge_permutations[i + 1:]
        ) % 2

        # Parity consistency
        parity_consistent = corner_permutation_parity == edge_permutation_parity

        # If not solvable, swap a apir of adjacent edges to change edge parity.
        # It will now be the same as the corner parity.
        if not parity_consistent:
            edge_permutations[0], edge_permutations[1] = edge_permutations[1], edge_permutations[0]
        
        corner_orientations = [random.randint(0,2) for i in range(7)]
        corner_orientations.append(- sum(corner_orientations)%3) # force divisiblity by 3

        edge_orientations = [random.randint(0,1) for i in range(11)]
        edge_orientations.append(sum(edge_orientations)%2) # force divisibility by 2 
       
        self.corner_permutations = corner_permutations
        self.corner_orientations = corner_orientations
        self.edge_permutations = edge_permutations
        self.edge_orientations = edge_orientations

class FaceletCube:
    def __init__(self, cube_input=None):
        
        self.__corner_colour_table, self.__edge_colour_table = Data.corner_colour_table, Data.edge_colour_table # These map colours to cubie pieces. 
        self.__corner_facelet_indices, self.__edge_facelet_indices = Data.corner_facelet_indices, Data.edge_facelet_indices # These map pieces to their facelets. ie: UFL to U6, L2, F0.

        self.__colours_on_face_map = Data.colours_on_face_map # Used to cycle the colours on a face.

        # Initialize the facelet representation of a solved cube. 
        self.facelets = list('WWWWWWWWWGGGGGGGGGOOOOOOOOORRRRRRRRRBBBBBBBBBYYYYYYYYY')

        # Handles the cube_input parameter. 
        if cube_input is not None:
            if isinstance(cube_input, FaceletCube):
                self.facelets = cube_input.facelets
            elif isinstance(cube_input, str):
                self.facelets = list(cube_input)
            elif isinstance(cube_input, CubieCube):
                self.facelets = self.__from_cubie_cube(cube_input).facelets
            else:
                raise TypeError('cube_input does not match an expected type')
    
    # Converts a cubie representation to a facelet representation. 
    def __from_cubie_cube(self, cubie_cube):
        
        facelets = [''] * 54
       
        # Iteratively load the colour data for each corner into the facelet array.  
        for i in range(8):
            # Retrieve the piece code and orientation of the corner in position i. 
            permutation = cubie_cube.corner_permutations[i]
            orientation = cubie_cube.corner_orientations[i]
            for j in range(3):
                # Map the colours of the retrieved piece to the facelet indices of the position. 
                facelets[self.__corner_facelet_indices[i][j]] = (self.__corner_colour_table[permutation])[(j+orientation)%3]

        # Load the colour data for each edge into the facelet array. 
        for i in range(12):
            permutation = cubie_cube.edge_permutations[i]
            orientation = cubie_cube.edge_orientations[i]
            for j in range(2):
                facelets[self.__edge_facelet_indices[i][j]] = self.__edge_colour_table[permutation][(j + orientation) % 2]

        # Fill the centre pieces (these are fixed).
        centre_colours = ['W', 'G', 'O', 'R', 'B', 'Y']
        centre_indices = [Facelet.U4, Facelet.F4, Facelet.L4, Facelet.R4, Facelet.B4, Facelet.D4]
        for i in range(6):
            facelets[centre_indices[i]] = centre_colours[i]
        
        # Create a facelet_cube with the calculated facelets to return.
        facelet_string = str(''.join(facelets))
        facelet_cube = FaceletCube(facelet_string)
        return facelet_cube
    
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
                new_face_indices[j] = face_indices[self.__colours_on_face_map[j]] 
            face_indices = new_face_indices
        # Update the configuration.
        for i in range(9):
            self.facelets[i+start_pointer] = face_indices[i]

    def __repr__(self):
        return ''.join(self.facelets)
    
    def verify_string_validity(self):
        return all(self.facelets.count(colour) == 9 for colour in 'WGORBY')
    
    def verify_validity(self):
        self.is_valid = self.verify_string_validity()
        try:
            CubieCube(self)
        except:
            self.is_valid = False
        return self.is_valid
        
class CoordCube:
    def __init__(self, cube_input=None):
        # Initialize the CoordCube representation of a solved cube. 
        self.g1_coordinates = [0,0,0]
        self.g2_coordinates = [0,0,0]
        
        self.__cubie_cube = CubieCube()
        try:
            self.__g1_move_tables = [
                    move_tables.corner_orientation_table,
                    move_tables.edge_orientation_table,
                    move_tables.UD_slice_permutation_table
            ]
            self.__g2_move_tables = [
                move_tables.eight_edge_permutation_table,
                move_tables.four_edge_permutation_table,
                move_tables.corner_permutation_table
            ]
        except:
            pass
        
        def __load_configuration_from(cube_input):  # Helper procedure to copy configuration from an input CoordCube
            
            self.g1_coordinates = cube_input.g1_coordinates 
            self.g2_coordinates = cube_input.g2_coordinates 
   
        # Load cube configuration.
        if cube_input is not None:
            if isinstance(cube_input, CoordCube):
                self.__cubie_cube = None  # Unnecessary since calculate_..._coordinate will never be called.
                __load_configuration_from(cube_input)
            elif isinstance(cube_input, CubieCube):
                coord_cube = self.__from_cubie_cube(cube_input)
                __load_configuration_from(coord_cube)

    def __from_cubie_cube(self, cubie_cube):
        # Creates a new CoordCube from a CubieCube.
        coord_cube = CoordCube()
        coord_cube.__cubie_cube = cubie_cube

        # Calculate all coordinates
        corner_orientation_coordinate = coord_cube.__calculate_corner_orientation_coordinate()
        edge_orientation_coordinate = coord_cube.__calculate_edge_orientation_coordinate()
        UD_slice_coordinate = coord_cube.__calculate_UD_slice_coordinate()
        
        eight_edge_permutation_coordinate = coord_cube.__calculate_eight_edge_permutation_coordinate()
        four_edge_permutation_coordinate = coord_cube.__calculate_four_edge_permutation_coordinate()
        corner_permutation_coordinate = coord_cube.__calculate_corner_permutation_coordinate()

        coord_cube.g1_coordinates = [corner_orientation_coordinate, edge_orientation_coordinate, UD_slice_coordinate]
        coord_cube.g2_coordinates = [eight_edge_permutation_coordinate, four_edge_permutation_coordinate, corner_permutation_coordinate]
    
        return coord_cube

    @property
    def corner_orientation_coordinate(self):
        return self.g1_coordinates[0]
    @property 
    def edge_orientation_coordinate(self):
        return self.g1_coordinates[1]
    @property
    def UD_slice_coordinate(self):
        return self.g1_coordinates[2]
    @property   
    def eight_edge_permutation_coordinate(self):
        return self.g2_coordinates[0]
    @property 
    def four_edge_permutation_coordinate(self):
        return self.g2_coordinates[1]
    @property 
    def corner_permutation_coordinate(self):
        return self.g2_coordinates[2]
    
    def rotate_clockwise(self, move):
        # Update coordinates based on move
        self.g1_coordinates = [(self.__g1_move_tables[i])[str(self.g1_coordinates[i])][move] for i in range(3)]
        self.g2_coordinates = [(self.__g2_move_tables[i])[str(self.g2_coordinates[i])][move] for i in range(3)]
      
    def __repr__(self):
        return str((
            self.g1_coordinates,
            self.g2_coordinates
        ))
    
    '''
    Calculation methods for each coordinate.

    corner_orientation_coordinate : the orientation array is treated as a ternary number. This is converted to decimal to find the coordinate. 
    edge_orientation_coordinate : this is the same as for the corner orientation, only binary is used. 
    etc... 
    '''

    def __calculate_corner_orientation_coordinate(self):
        return sum(self.__cubie_cube.corner_orientations[i] * (3 ** i) for i in range(7))

    def __calculate_edge_orientation_coordinate(self):
        return sum(self.__cubie_cube.edge_orientations[i] * (2 ** i) for i in range(11))

    def __calculate_UD_slice_coordinate(self):
        slice_indices = [1 if i in [8, 9, 10, 11] else 0 for i in self.__cubie_cube.edge_permutations]
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

    def __calculate_corner_permutation_coordinate(self):
        corner_permutation_coordinate = 0
        for i in range(8):
            smaller_count = sum(1 for j in range(i) if self.__cubie_cube.corner_permutations[j] > self.__cubie_cube.corner_permutations[i])
            corner_permutation_coordinate += smaller_count * math.factorial(i)
        return corner_permutation_coordinate

    def __calculate_eight_edge_permutation_coordinate(self):
        eight_edge_permutation_coordinate = 0
        for i in range(8):
            smaller_count = sum(1 for j in range(i) if self.__cubie_cube.edge_permutations[j] > self.__cubie_cube.edge_permutations[i])
            eight_edge_permutation_coordinate += smaller_count * math.factorial(i)
        return eight_edge_permutation_coordinate

    def __calculate_four_edge_permutation_coordinate(self):
        four_edge_permutation_coordinate = 0
        for i in range(4):
            smaller_count = sum(1 for j in range(i) if self.__cubie_cube.edge_permutations[j + 8] > self.__cubie_cube.edge_permutations[i + 8])
            four_edge_permutation_coordinate += smaller_count * math.factorial(i)
        return four_edge_permutation_coordinate
