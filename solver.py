import cube
cube.import_tables()
from data import * 
from datetime import datetime
import json 

class PruningTables:
    '''Loads pruning tables from local files.

    Attributes:
        udslice_corner_table (dict): udslice position, corner orientation table. (g1 heuristic)
        udslice_edge_table (dict): udslice position, edge orientation  table. (g1 heurstic)
        corner_udslice_edge_table (dict): corner permutation, four edge permutation table. (g2 heuristic)
        mainedge_udslice_edge_table (dict): eight edge permutation, four edge permutation table. (g2 heuristic)
    '''   
    def __init__(self):

        with open('pruning_tables/udslice_corner_table.json', 'r') as file:
            self.udslice_corner_table = json.load(file)
        with open('pruning_tables/udslice_edge_table.json', 'r') as file:
            self.udslice_edge_table = json.load(file)
        with open('pruning_tables/corner_udslice_edge_table.json', 'r') as file:
            self.corner_udslice_edge_table = json.load(file)
        with open('pruning_tables/main_edge_udslice_edge_table.json', 'r') as file:
            self.mainedge_udslice_edge_table = json.load(file)

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

    class StageSolver:
        '''An 'abstract' parent class that g1 and g2 inherit from.
        Each child must implement its own _heuristic_function and _is_solved_function,
        but inherits search_for_solution.
        '''
        def __init__(self, max_depth, allowed_moves):
            
            self.max_depth = max_depth
            self.allowed_moves = allowed_moves
        
        def _heuristic_function(self, state): 
            '''Searches pruning tables for value of heuristic function, at a given state.

            Args:
                state (CoordCube): CoordCube for which the heuristic is being evaluated for.
            '''
            pass
        
        def _is_solved_function(self, state):
            '''Determines if the solver's conditions for a 'solved' cube are met. 

            Args:
                state (CoordCube): CoordCube for which the conditions are being checked. 
            '''
            pass
        
        def search_for_solution(self, cube_state, threshold=0): # IDA*
            '''IDA* algorithm.
            Stack implementation of DFS to avoid recursion depth limitations. 
            Performs pruning using the heuristic function.
            Recurisve calls increase depth threshold if solved conditions are not met. 

            Args:
                cube_state (CoordCube): CoordCube
                threshold (int, optional): Smallest pruned f-score from previous recursive call. Defaults to 0.

            Returns:
                List[Move]: solution path (this is the base case of recursion)
                (or result of recursive call).
            '''
            stack = [(cube_state, [])]
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
                        if move == Move.inverse_move(current_path[-1]):
                            continue
                    next_state = cube.CoordCube(current_state)
                    next_state.rotate_clockwise(move)

                    next_path = current_path + [move]

                    stack.append((next_state, next_path))

            return self.search_for_solution(cube_state, min_f)
   
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

            self.__udslice_corner_pruning_table = pruning_tables.udslice_corner_table
            self.__udslice_edge_pruning_table = pruning_tables.udslice_edge_table

        def _heuristic_function(self, state):
            '''g1 admissible heuristic function.
            Overrides StageSolver. 

            Args:
                state (CoordCube): CoordCube that the value of the heuristic is being calculated for. 

            Returns:
                int: heuristic
            '''

            search_coord1 = str((state.UD_slice_coordinate, state.corner_orientation_coordinate))
            d1 = self.__udslice_corner_pruning_table.get(search_coord1, self.max_depth)

            search_coord2 = str((state.UD_slice_coordinate, state.edge_orientation_coordinate))
            d2 = self.__udslice_edge_pruning_table.get(search_coord2, self.max_depth)

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

            self.__corner_udslice_edge_table = pruning_tables.corner_udslice_edge_table
            self.__main_edge_udslice_edge_pruning_table = pruning_tables.mainedge_udslice_edge_table

        def _heuristic_function(self, state):
            '''g2 admissible heuristic function.
            Overrides StageSolver. 

            Args:
                state (CoordCube): CoordCube that the value of the heuristic is being calculated for. 

            Returns:
                int: heuristic
            '''
            search_coord1 = str((state.corner_permutation_coordinate, state.four_edge_permutation_coordinate))
            d1 = self.__corner_udslice_edge_table.get(search_coord1, self.max_depth)

            search_coord2 = str((state.eight_edge_permutation_coordinate, state.four_edge_permutation_coordinate))
            d2 = self.__main_edge_udslice_edge_pruning_table.get(search_coord2, self.max_depth)

            return max(d1, d2)

        def _is_solved_function(self, state):
            return sum(state.g2_coordinates) == 0
        
    @staticmethod
    def __contract_solution(solution):
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

        if isinstance(cube_input, cube.CubieCube):
            cubie_input = cube_input
        elif isinstance(cube_input, str):
            cubie_input = cube.CubieCube(cube_input)
        elif isinstance(cube_input, cube.FaceletCube):
            cubie_input = cube_input.to_cubie_cube()
        else:
            raise ("Error: cube_input is not an expected type")
        
        initial_state = cube.CoordCube(cubie_input)

        # Solve G1
        g1_solution = self.__g1_solver.search_for_solution(initial_state)
        print("G1 Solution:", [Data.move_notation[i] for i in g1_solution])

        for move in g1_solution:
            cubie_input.move(move)
            initial_state.rotate_clockwise(move)

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
    