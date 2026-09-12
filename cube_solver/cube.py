import json
import math
import random

from .data import *
from .paths import MOVE_TABLES_DIR

class MoveTables:
    '''Loads move tables from local files.

    Attributes:
        corner_orientation_table, edge_orientation_table, UD_slice_permutation_table,
        four_edge_permutation_table, eight_edge_permutation_table, corner_permutation_table (dict):
            each maps a coordinate to its resulting coordinate after each of the 18 moves.
    '''

    def __init__(self):
        with open(MOVE_TABLES_DIR / 'corner_orientation_table.json', 'r') as file:
            self.corner_orientation_table = json.load(file)
        with open(MOVE_TABLES_DIR / 'edge_orientation_table.json', 'r') as file:
            self.edge_orientation_table = json.load(file)
        with open(MOVE_TABLES_DIR / 'UD_slice_permutation_table.json', 'r') as file:
            self.UD_slice_permutation_table = json.load(file)
        with open(MOVE_TABLES_DIR / 'four_edge_permutation_table.json', 'r') as file:
            self.four_edge_permutation_table = json.load(file)
        with open(MOVE_TABLES_DIR / 'eight_edge_permutation_table.json', 'r') as file:
            self.eight_edge_permutation_table = json.load(file)
        with open(MOVE_TABLES_DIR / 'corner_permutation_table.json', 'r') as file:
            self.corner_permutation_table = json.load(file)

def import_tables():
    '''Loads move tables into the global move_tables.

    Deferred to a function (rather than a module-level import) because move_table_generator.py
    imports this module to generate the tables in the first place - they may not exist on disk yet
    when cube.py itself is imported.
    '''
    global move_tables
    move_tables = MoveTables()

class CubieCube:
    '''A cube represented as four arrays: corner/edge permutations and orientations.

    Attributes:
        corner_permutations (List[int]): code of the Corner (see data.py) occupying each position.
        corner_orientations (List[int]): twist of each corner (0 = correct, 1 = clockwise, 2 = anti-clockwise).
        edge_permutations (List[int]): code of the Edge occupying each position.
        edge_orientations (List[int]): flip of each edge (0 = correct, 1 = flipped).

    All orientations are relative to a fixed reference orientation.
    '''

    def __init__(self, cube_input=None):
        '''Loads state from cube_input: a CubieCube, FaceletCube, cube string, or None for a solved cube.

        Raises:
            TypeError: cube_input does not match an expected type.
        '''
        self.corner_permutations = list(range(8))
        self.corner_orientations = [0] * 8
        self.edge_permutations = list(range(12))
        self.edge_orientations = [0] * 12

        self.__corner_permutation_dict, self.__corner_orientation_dict, self.__edge_permutation_dict, self.__edge_orientation_dict = Data.cubie_move_dicts

        self.__corner_colour_table, self.__edge_colour_table = Data.corner_colour_table, Data.edge_colour_table
        self.__corner_facelet_indices, self.__edge_facelet_indices = Data.corner_facelet_indices, Data.edge_facelet_indices

        def __load_configuration_from(cube_input):
            self.corner_permutations = cube_input.corner_permutations
            self.corner_orientations = cube_input.corner_orientations
            self.edge_permutations = cube_input.edge_permutations
            self.edge_orientations = cube_input.edge_orientations

        if cube_input is not None:
            if isinstance(cube_input, FaceletCube):
                __load_configuration_from(self.__from_facelet_cube(cube_input))
            elif isinstance(cube_input, CubieCube):
                __load_configuration_from(cube_input)
            elif isinstance(cube_input, str):
                __load_configuration_from(self.__from_facelet_cube(FaceletCube(cube_input)))
            else:
                raise TypeError('cube_input does not match an expected type')

    def __from_facelet_cube(self, facelet_cube):
        '''Converts a FaceletCube to a CubieCube.'''
        cubie_cube = CubieCube()

        new_corner_permutations = list(range(8))
        new_corner_orientations = [0] * 8
        new_edge_permutations = list(range(12))
        new_edge_orientations = [0] * 12

        for i, corner_index in enumerate(self.__corner_facelet_indices):
            colours = [facelet_cube.facelets[idx] for idx in corner_index]

            # Orientation = how far 'W'/'Y' has rotated away from its reference position.
            orientation = -(colours.index('W') if 'W' in colours else colours.index('Y')) % 3

            # Un-rotate the colours so they match a corner_colour_table entry, to find the piece.
            oriented_colours = [colours[(j - orientation) % 3] for j in range(3)]
            permutation = self.__corner_colour_table.index(oriented_colours)

            new_corner_permutations[i] = permutation
            new_corner_orientations[i] = orientation

        for i, edge_index in enumerate(self.__edge_facelet_indices):
            colours = [facelet_cube.facelets[idx] for idx in edge_index]

            orientation_colors = ['W', 'Y', 'G', 'B']
            orientation = next(colours.index(color) for color in orientation_colors if color in colours)

            oriented_colours = [colours[(j - orientation) % 2] for j in range(2)]
            permutation = self.__edge_colour_table.index(oriented_colours)

            new_edge_permutations[i] = permutation
            new_edge_orientations[i] = orientation

        cubie_cube.corner_permutations = new_corner_permutations
        cubie_cube.corner_orientations = new_corner_orientations
        cubie_cube.edge_permutations = new_edge_permutations
        cubie_cube.edge_orientations = new_edge_orientations

        return cubie_cube

    def move(self, move):
        '''Performs a cube turn.

        Args:
            move (Move): integer 0-17 (see data.py). move % 6 gives the face; move // 6 + 1 gives the
                number of clockwise quarter-turns (so double and anti-clockwise turns are just repetition).

        For orientations, the new value is (old value + move's orientation delta) mod 3 for corners,
        mod 2 for edges - e.g. a clockwise turn applied to an already clockwise-twisted corner gives
        (1 + 1) mod 3 = 2, i.e. an anti-clockwise twist.
        '''
        turn_count = 1 + (move // 6)
        face = move % 6

        for _ in range(turn_count):
            # Permute corners, carrying their orientation data along with them.
            corner_permutation_map = self.__corner_permutation_dict[face]
            new_corner_permutations = [0] * 8
            new_corner_orientations = [0] * 8
            for i in range(8):
                new_corner_permutations[i] = self.corner_permutations[corner_permutation_map[i]]
                new_corner_orientations[i] = self.corner_orientations[corner_permutation_map[i]]
            self.corner_permutations = new_corner_permutations
            self.corner_orientations = new_corner_orientations

            # Apply the twist delta for this move.
            corner_orientation_map = self.__corner_orientation_dict[face]
            for i in range(8):
                new_corner_orientations[i] = (self.corner_orientations[i] + corner_orientation_map[i]) % 3
            self.corner_orientations = new_corner_orientations

            # Edges follow the same two-step pattern as corners above.
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

    def __repr__(self):
        return (f"Corner Permutations: {self.corner_permutations}\n"
                f"Corner Orientations: {self.corner_orientations}\n"
                f"Edge Permutations: {self.edge_permutations}\n"
                f"Edge Orientations: {self.edge_orientations}\n")

    def verify_solvability(self):
        '''Checks that a sequence of turns solving the cube exists: valid corner/edge orientation
        totals, and matching corner/edge permutation parity.

        Returns:
            bool: True if solvable.
        '''
        corner_twist_valid = sum(self.corner_orientations) % 3 == 0
        edge_flip_valid = sum(self.edge_orientations) % 2 == 0

        corner_permutation_parity = sum(
            x > y for i, x in enumerate(self.corner_permutations) for y in self.corner_permutations[i + 1:]
        ) % 2
        edge_permutation_parity = sum(
            a > b for i, a in enumerate(self.edge_permutations) for b in self.edge_permutations[i + 1:]
        ) % 2
        parity_consistent = corner_permutation_parity == edge_permutation_parity

        if corner_twist_valid and edge_flip_valid and parity_consistent:
            return True
        else:
            print(f"Error: The input cube is not solvable."
                f"\nCorner Twisted: {not corner_twist_valid}"
                f"\nEdge Flipped: {not edge_flip_valid}"
                f"\nCorner Parity Consistent: {not corner_permutation_parity}"
                f"\nEdge Parity Consistent: {not edge_permutation_parity}"
            )
            return False

    def scramble(self):
        '''Randomizes the cube into a solvable state.'''
        corner_permutations = list(range(8))
        edge_permutations = list(range(12))

        random.shuffle(corner_permutations)
        random.shuffle(edge_permutations)

        corner_permutation_parity = sum(
            a > b for i, a in enumerate(corner_permutations) for b in corner_permutations[i + 1:]
        ) % 2
        edge_permutation_parity = sum(
            a > b for i, a in enumerate(edge_permutations) for b in edge_permutations[i + 1:]
        ) % 2

        # Corner and edge permutation parity must match for a solvable cube - if not, swap a pair of
        # edges to flip the edge parity.
        if corner_permutation_parity != edge_permutation_parity:
            edge_permutations[0], edge_permutations[1] = edge_permutations[1], edge_permutations[0]

        corner_orientations = [random.randint(0, 2) for i in range(7)]
        corner_orientations.append(-sum(corner_orientations) % 3)  # force total divisible by 3

        edge_orientations = [random.randint(0, 1) for i in range(11)]
        edge_orientations.append(sum(edge_orientations) % 2)  # force total even

        self.corner_permutations = corner_permutations
        self.corner_orientations = corner_orientations
        self.edge_permutations = edge_permutations
        self.edge_orientations = edge_orientations

class FaceletCube:
    '''A cube represented as a single array of 54 facelet colours.

    Attributes:
        facelets (List[str]): colour of each of the 54 facelets.
    '''

    def __init__(self, cube_input=None):
        '''Loads state from cube_input: a FaceletCube, cube string, CubieCube, or None for a solved cube.

        Raises:
            TypeError: cube_input does not match an expected type.
        '''
        self.__corner_colour_table, self.__edge_colour_table = Data.corner_colour_table, Data.edge_colour_table
        self.__corner_facelet_indices, self.__edge_facelet_indices = Data.corner_facelet_indices, Data.edge_facelet_indices
        self.__colours_on_face_map = Data.colours_on_face_map

        self.facelets = list('WWWWWWWWWGGGGGGGGGOOOOOOOOORRRRRRRRRBBBBBBBBBYYYYYYYYY')

        if cube_input is not None:
            if isinstance(cube_input, FaceletCube):
                self.facelets = cube_input.facelets
            elif isinstance(cube_input, str):
                self.facelets = list(cube_input)
            elif isinstance(cube_input, CubieCube):
                self.facelets = self.__from_cubie_cube(cube_input).facelets
            else:
                raise TypeError('cube_input does not match an expected type')

    def move(self, move):
        '''Performs a cube turn.

        Args:
            move (Move): integer 0-17 (see data.py).
        '''
        cubie_cube = CubieCube(self)
        cubie_cube.move(move)
        self.facelets = self.__from_cubie_cube(cubie_cube).facelets

    def __from_cubie_cube(self, cubie_cube):
        '''Converts a CubieCube to a FaceletCube.'''
        facelets = [''] * 54

        for i in range(8):
            permutation = cubie_cube.corner_permutations[i]
            orientation = cubie_cube.corner_orientations[i]
            for j in range(3):
                facelets[self.__corner_facelet_indices[i][j]] = (self.__corner_colour_table[permutation])[(j + orientation) % 3]

        for i in range(12):
            permutation = cubie_cube.edge_permutations[i]
            orientation = cubie_cube.edge_orientations[i]
            for j in range(2):
                facelets[self.__edge_facelet_indices[i][j]] = self.__edge_colour_table[permutation][(j + orientation) % 2]

        # Centre pieces are fixed and don't come from a cubie.
        centre_colours = ['W', 'G', 'O', 'R', 'B', 'Y']
        centre_indices = [Facelet.U4, Facelet.F4, Facelet.L4, Facelet.R4, Facelet.B4, Facelet.D4]
        for i in range(6):
            facelets[centre_indices[i]] = centre_colours[i]

        return FaceletCube(''.join(facelets))

    def rotate_colours_on_face(self, move):
        '''Cycles the colours on a single face without turning the bordering facelets.
        Used by capture.py to re-orient captured faces relative to each other.

        Args:
            move (Move): identifies the face and direction to cycle.
        '''
        face = move % 6
        move_count = 1 + (move // 6)

        start_pointer = 9 * face
        face_indices = self.facelets[start_pointer: start_pointer + 9]
        for i in range(move_count):
            new_face_indices = [0] * 9
            for j in range(9):
                new_face_indices[j] = face_indices[self.__colours_on_face_map[j]]
            face_indices = new_face_indices

        for i in range(9):
            self.facelets[i + start_pointer] = face_indices[i]

    def __repr__(self):
        return ''.join(self.facelets)

    def verify_string_validity(self):
        '''Checks that facelets contains exactly 9 of each of the 6 colours.'''
        return all(self.facelets.count(colour) == 9 for colour in 'WGORBY')

    def verify_validity(self):
        '''Checks that facelets can be converted to a valid CubieCube - i.e. every group of
        connected facelets matches a real piece's colours, and each piece is used exactly once.
        '''
        is_valid = self.verify_string_validity()
        try:
            CubieCube(self)
        except Exception:
            is_valid = False
        return is_valid

class CoordCube:
    '''A cube represented as six coordinates, used to index move and pruning tables directly
    instead of simulating turns on a CubieCube.

    Attributes:
        g1_coordinates (Tuple[int, int, int]): corner orientation, edge orientation, UD slice permutation.
        g2_coordinates (Tuple[int, int, int]): eight-edge permutation, four-edge permutation, corner permutation.
    '''

    def __init__(self, cube_input=None):
        '''Loads coordinates from cube_input: a CoordCube, CubieCube, or None for a solved cube.'''
        self.g1_coordinates = (0, 0, 0)
        self.g2_coordinates = (0, 0, 0)

        try:
            self.__g1_move_tables = (
                move_tables.corner_orientation_table,
                move_tables.edge_orientation_table,
                move_tables.UD_slice_permutation_table,
            )
            self.__g2_move_tables = (
                move_tables.eight_edge_permutation_table,
                move_tables.four_edge_permutation_table,
                move_tables.corner_permutation_table,
            )
        except NameError:
            pass  # Move tables not loaded yet - only a problem if move() is later called.

        def __load_configuration_from(cube_input):
            self.g1_coordinates = cube_input.g1_coordinates
            self.g2_coordinates = cube_input.g2_coordinates

        if cube_input is not None:
            if isinstance(cube_input, CoordCube):
                self.__cubie_cube = None  # Unused: calculate_..._coordinate is never called on this path.
                __load_configuration_from(cube_input)
            elif isinstance(cube_input, CubieCube):
                coord_cube = self.__from_cubie_cube(cube_input)
                __load_configuration_from(coord_cube)

    def __from_cubie_cube(self, cubie_cube):
        '''Converts a CubieCube to a CoordCube by computing all six coordinates.'''
        coord_cube = CoordCube()
        coord_cube.__cubie_cube = cubie_cube

        corner_orientation_coordinate = coord_cube.__calculate_corner_orientation_coordinate()
        edge_orientation_coordinate = coord_cube.__calculate_edge_orientation_coordinate()
        UD_slice_coordinate = coord_cube.__calculate_UD_slice_coordinate()

        eight_edge_permutation_coordinate = coord_cube.__calculate_eight_edge_permutation_coordinate()
        four_edge_permutation_coordinate = coord_cube.__calculate_four_edge_permutation_coordinate()
        corner_permutation_coordinate = coord_cube.__calculate_corner_permutation_coordinate()

        coord_cube.g1_coordinates = (corner_orientation_coordinate, edge_orientation_coordinate, UD_slice_coordinate)
        coord_cube.g2_coordinates = (eight_edge_permutation_coordinate, four_edge_permutation_coordinate, corner_permutation_coordinate)

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

    def move(self, move):
        '''Performs a cube turn by looking up each coordinate's resulting value in the move tables.

        Args:
            move (Move): move to perform.
        '''
        self.g1_coordinates = [self.__g1_move_tables[i][self.g1_coordinates[i]][move] for i in range(3)]
        self.g2_coordinates = [self.__g2_move_tables[i][self.g2_coordinates[i]][move] for i in range(3)]

    def __repr__(self):
        return str((self.g1_coordinates, self.g2_coordinates))

    def __calculate_corner_orientation_coordinate(self):
        '''Treats the 8 corner orientations as a ternary number. Range: [0, 2186].'''
        return sum(self.__cubie_cube.corner_orientations[i] * (3 ** i) for i in range(7))

    def __calculate_edge_orientation_coordinate(self):
        '''Treats the 12 edge orientations as a binary number. Range: [0, 2047].'''
        return sum(self.__cubie_cube.edge_orientations[i] * (2 ** i) for i in range(11))

    def __calculate_UD_slice_coordinate(self):
        '''Encodes which 4 of the 12 edge slots hold UD-slice edges as a combinatorial (binomial) index.
        Range: [0, 494].
        '''
        slice_indices = [1 if i in [8, 9, 10, 11] else 0 for i in self.__cubie_cube.edge_permutations]
        UD_slice_coordinate = 0
        occupied_count = 0
        start_counting = False  # Only start counting once the first UD-slice edge has been seen.

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
        '''Lehmer code of the corner permutation, converted to decimal. Range: [0, 40319].'''
        corner_permutation_coordinate = 0
        for i in range(8):
            smaller_count = sum(1 for j in range(i) if self.__cubie_cube.corner_permutations[j] > self.__cubie_cube.corner_permutations[i])
            corner_permutation_coordinate += smaller_count * math.factorial(i)
        return corner_permutation_coordinate

    def __calculate_eight_edge_permutation_coordinate(self):
        '''Lehmer code of the 8 non-UD-slice edges' permutation. Range: [0, 40319].'''
        eight_edge_permutation_coordinate = 0
        for i in range(8):
            smaller_count = sum(1 for j in range(i) if self.__cubie_cube.edge_permutations[j] > self.__cubie_cube.edge_permutations[i])
            eight_edge_permutation_coordinate += smaller_count * math.factorial(i)
        return eight_edge_permutation_coordinate

    def __calculate_four_edge_permutation_coordinate(self):
        '''Lehmer code of the 4 UD-slice edges' permutation. Range: [0, 23].'''
        four_edge_permutation_coordinate = 0
        for i in range(4):
            smaller_count = sum(1 for j in range(i) if self.__cubie_cube.edge_permutations[j + 8] > self.__cubie_cube.edge_permutations[i + 8])
            four_edge_permutation_coordinate += smaller_count * math.factorial(i)
        return four_edge_permutation_coordinate
