import cube
cube.import_tables()
from data import *
from datetime import datetime
import json
from abc import ABC, abstractmethod

# Coordinate-space sizes, used to flatten (coordinate_1, coordinate_2) pairs into a single
# index into a dense pruning table array: index = coordinate_1 * dim2 + coordinate_2.
CORNER_ORIENTATION_SIZE = 3 ** 7   # 2187
EDGE_ORIENTATION_SIZE = 2 ** 11    # 2048
FOUR_EDGE_PERMUTATION_SIZE = 24

class PruningTables:
    '''Loads pruning tables from local files.

    Attributes:
        udslice_corner_table (dict): udslice position, corner orientation table. (g1 heuristic)
        udslice_edge_table (dict): udslice position, edge orientation  table. (g1 heurstic)
        corner_udslice_edge_table (dict): corner permutation, four edge permutation table. (g2 heuristic)
        mainedge_udslice_edge_table (dict): eight edge permutation, four edge permutation table. (g2 heuristic)
    '''   
    def __init__(self):

        with open('pruning_tables/UD_slice_corner_table.json', 'r') as file:
            self.UD_slice_corner_table = json.load(file)
        with open('pruning_tables/UD_slice_edge_table.json', 'r') as file:
            self.UD_slice_edge_table = json.load(file)
        with open('pruning_tables/corner_four_edge_table.json', 'r') as file:
            self.corner_four_edge_table = json.load(file)
        with open('pruning_tables/eight_edge_four_edge_table.json', 'r') as file:
            self.eight_edge_four_edge_table = json.load(file)

def import_tables():
    '''Imports tables to global variable pruuning_tables to avoid an import error.
    
    The import error is caused by:
        - Solver.py trying to import pruning tables before they exist. 

    Solution: import pruning tables into Solver after they have been generated. 
    '''    
    global pruning_tables
    pruning_tables = PruningTables()
    
class Solver:
    '''Solves the cube. 
    '''
    def __init__(self):
        '''Initialize both solver stages. 
        '''
        self.__g1_solver = self.g1Solver()
        self.__g2_solver = self.g2Solver()

    class StageSolver(ABC):
        '''An 'abstract' parent class that g1 and g2 inherit from.
        Each child must implement its own _heuristic_function and _is_solved_function,
        but inherits search_for_solution.
        '''
        def __init__(self, max_depth, allowed_moves):
            
            self.max_depth = max_depth
            self.allowed_moves = allowed_moves
        
        @abstractmethod
        def _heuristic_function(self, state): 
            '''Searches pruning tables for value of heuristic function, at a given state.

            Args:
                state (CoordCube): CoordCube for which the heuristic is being evaluated for.
            '''
            pass
        
        @abstractmethod
        def _is_solved_function(self, state):
            '''Determines if the solver's conditions for a 'solved' cube are met. 

            Args:
                state (CoordCube): CoordCube for which the conditions are being checked. 
            '''
            pass
        
        def search_for_solution(self, state, threshold=0): # IDA*
            '''IDA* algorithm.
            Stack implementation of DFS to avoid recursion depth limitations. 
            Performs pruning using the heuristic function.
            Recurisve calls increase depth threshold if solved conditions are not met. 

            Args:
                statet (CoordCube): CoordCube
                threshold (int, optional): Smallest pruned f-score from previous recursive call. Defaults to 0.

            Returns:
                List[Move]: solution path (this is the base case of recursion)
                (or result of recursive call).
            '''
            stack = [(state, [])]
            min_f = float('inf')
            while len(stack) > 0: 

                current_state, current_path = stack.pop()
                coord = cube.CoordCube(current_state)

                g_score = len(current_path) 
                h_score = self._heuristic_function(current_state)

                f_score = g_score + h_score

                if f_score > threshold or g_score > self.max_depth:
                    if f_score < min_f:
                        min_f = f_score
                    continue

                if self._is_solved_function(coord):
                    return current_path
                
                for move in self.allowed_moves:
                    if current_path:
                        last_face = current_path[-1] % 6
                        face = move % 6
                        if face == last_face: #Ignore same-face moves. 
                            continue
                        if face == Data.opposite_face[last_face] and face < last_face:
                            continue # Canonical ordering for opposite face moves (which commute)
                        
                        
                    next_state = cube.CoordCube(current_state)
                    next_state.move(move)

                    next_path = current_path + [move]

                    stack.append((next_state, next_path))

            return self.search_for_solution(state, min_f)
   
    class g1Solver(StageSolver):
        '''Solves the cube to the g1 subset. 
        Inherits from StateSolver. 
        '''
        def __init__(self):
            '''Load g1 pruning tables and constants. 
            '''
            max_depth = 12 
            allowed_moves = Data.g1_allowed_moves
            super().__init__(max_depth, allowed_moves)

            self.__UD_slice_corner_table = pruning_tables.UD_slice_corner_table
            self.__UD_slice_edge_table = pruning_tables.UD_slice_edge_table

        def _heuristic_function(self, state):
            '''g1 admissible heuristic function.
            Overrides StageSolver. 

            Args:
                state (CoordCube): CoordCube that the value of the heuristic is being calculated for. 

            Returns:
                int: heuristic
            '''

            d1 = self.__UD_slice_corner_table[state.UD_slice_coordinate * CORNER_ORIENTATION_SIZE + state.corner_orientation_coordinate]
            d2 = self.__UD_slice_edge_table[state.UD_slice_coordinate * EDGE_ORIENTATION_SIZE + state.edge_orientation_coordinate]

            return max(d1, d2)

        def _is_solved_function(self, state):
            return sum(state.g1_coordinates) == 0

    class g2Solver(StageSolver):
        '''Solves the cube to the g2 subset.
        Inherits form StageSolver.
        '''
        def __init__(self):
            '''Load g2 pruning tables and constants. 
            '''
            max_depth = 18
            allowed_moves = Data.g2_allowed_moves
            super().__init__(max_depth, allowed_moves)

            self.__corner_four_edge_table = pruning_tables.corner_four_edge_table
            self.__eight_edge_four_edge_table = pruning_tables.eight_edge_four_edge_table

        def _heuristic_function(self, state):
            '''g2 admissible heuristic function.
            Overrides StageSolver. 

            Args:
                state (CoordCube): CoordCube that the value of the heuristic is being calculated for. 

            Returns:
                int: heuristic
            '''
            d1 = self.__corner_four_edge_table[state.corner_permutation_coordinate * FOUR_EDGE_PERMUTATION_SIZE + state.four_edge_permutation_coordinate]
            d2 = self.__eight_edge_four_edge_table[state.eight_edge_permutation_coordinate * FOUR_EDGE_PERMUTATION_SIZE + state.four_edge_permutation_coordinate]

            return max(d1, d2)

        def _is_solved_function(self, state):
            return sum(state.g2_coordinates) == 0
        
    def __contract_solution(self, solution):
        '''Combines repeated moves in solution where possible. 

        Args:
            solution (List[Move]): output from g1 solver + output from g2 solver. 

        Returns:
            List[Move]: contracted solution
        '''

        contracted_solution = []
        current_face = None
        current_turn_count = 0
        if len(solution) == 0:
            return contracted_solution
        for solution_index in range(len(solution) + 1):

            if solution_index < len(solution):
                move = solution[solution_index]
                face = move % 6
            else: 
                face = None
            turn_count = 1 + (move // 6)

            if current_face == face:
                current_turn_count += turn_count
            else:
                if current_face is not None:
                    final_turn_count = current_turn_count % 4
                    if final_turn_count != 0:
                        contracted_move = current_face + 6 * (final_turn_count - 1)
                        contracted_solution.append(contracted_move)
                current_face = face
                current_turn_count = turn_count

        return contracted_solution

    def solve_cube(self, cube_input):
        '''Calls methods to solve the cube to g1, update the cube state and solve to g2. 
        Contracts solution (simplifies it).

        There is no requirement to manage unsolvable cubes, since the Capture engine rules these out. see --> capture.py
        
        Args:
            cube_input (CubieCube, FaceletCube, str): Input cube to be solved. 

        Returns:
            List[Move]: contracted solution
        '''
      
        start_time = datetime.now()

        cubie_input = cube.CubieCube(cube_input)
        initial_state = cube.CoordCube(cubie_input)

        # Solve G1
        g1_solution = self.__g1_solver.search_for_solution(initial_state)
        print("G1 Solution:", [Data.move_notation[i] for i in g1_solution])

        for move in g1_solution:
            cubie_input.move(move)
            initial_state.move(move)

        print(f"Time to G1: {datetime.now() - start_time}")

        # Solve G2
        initial_state_g2 = cube.CoordCube(cubie_input)
        g2_solution = self.__g2_solver.search_for_solution(initial_state_g2)

        print("G2 Solution:", [Data.move_notation[i] for i in g2_solution])

        for move in g2_solution:
            cubie_input.move(move)

        print(f"Time to G2: {datetime.now() - start_time}")

        full_solution = g1_solution + g2_solution
        contracted_solution = self.__contract_solution(full_solution)

        print(f"\nWhole Solution ({len(contracted_solution)} moves):", [Data.move_notation[i] for i in contracted_solution])
    
        return contracted_solution
    