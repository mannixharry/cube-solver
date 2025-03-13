import cube
from data import * 
from datetime import datetime
from pruning_table_generator import pruning_tables

class Solver:
    def __init__(self):
        self.g1_solver = self.g1Solver()
        self.g2_solver = self.g2Solver()

    class StageSolver:
        def __init__(self, max_depth, allowed_moves):

            self.max_depth = max_depth
            self.allowed_moves = allowed_moves
        
        def heuristic_function(self, state): 
            pass
        
        def is_solved_function(self, state):
            pass
        
        # must be overridden 

        def search_for_solution(self, cube_state, threshold=0): # IDA*
            
            stack = [(cube_state, [])]
            min_h = float('inf')
            while len(stack) > 0: 

                current_state, current_path = stack.pop()
                coord = cube.CoordCube(current_state)

                g_score = len(current_path) 
                h_score = self.heuristic_function(current_state)

                f_score = g_score + h_score

                if f_score > threshold or g_score > self.max_depth:
                    if f_score < min_h:
                        min_h = f_score
                    continue

                if self.is_solved_function(coord):
                    return current_path
                
                for move in self.allowed_moves:
                    if current_path:
                        if move == Move.inverse_move(current_path[-1]):
                            continue
                    next_state = cube.CoordCube(current_state)
                    next_state.rotate_clockwise(move)

                    next_path = current_path + [move]

                    stack.append((next_state, next_path))

            return self.search_for_solution(cube_state, min_h)
   
    class g1Solver(StageSolver):
        def __init__(self):

            max_depth = 12 
            allowed_moves = Data.g1_allowed_moves
            super().__init__(max_depth, allowed_moves)

            self.udslice_corner_pruning_table = pruning_tables.udslice_corner_table
            self.udslice_edge_pruning_table = pruning_tables.udslice_edge_table

        def heuristic_function(self, state):
            search_coord1 = str((state.UD_slice_coordinate, state.corner_orientation_coordinate))
            d1 = self.udslice_corner_pruning_table.get(search_coord1, self.max_depth)

            search_coord2 = str((state.UD_slice_coordinate, state.edge_orientation_coordinate))
            d2 = self.udslice_edge_pruning_table.get(search_coord2, self.max_depth)

            return max(d1, d2)

        def is_solved_function(self, state):
            return state.UD_slice_coordinate == state.corner_orientation_coordinate == state.edge_orientation_coordinate == 0 

    class g2Solver(StageSolver):
        def __init__(self):
            
            max_depth = 18
            allowed_moves = Data.g2_allowed_moves
            super().__init__(max_depth, allowed_moves)

            self.corner_udslice_edge_table = pruning_tables.corner_udslice_edge_table
            self.main_edge_udslice_edge_pruning_table = pruning_tables.mainedge_udslice_edge_table

        def heuristic_function(self, state):
            search_coord1 = str((state.corner_permutation_coordinate, state.four_edge_permutation_coordinate))
            d1 = self.corner_udslice_edge_table.get(search_coord1, self.max_depth)

            search_coord2 = str((state.eight_edge_permutation_coordinate, state.four_edge_permutation_coordinate))
            d2 = self.main_edge_udslice_edge_pruning_table.get(search_coord2, self.max_depth)

            return max(d1, d2)

        def is_solved_function(self, state):
            return state.corner_permutation_coordinate == state.four_edge_permutation_coordinate == state.eight_edge_permutation_coordinate == 0 
        
    @staticmethod
    def contract_solution(solution):

        contracted_solution = []
        current_face = None
        current_turn_count = 0

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
        g1_solution = self.g1_solver.search_for_solution(initial_state)
        print("G1 Solution:", [Data.move_notation[i] for i in g1_solution])

        for move in g1_solution:
            cubie_input.move(move)
            initial_state.rotate_clockwise(move)

        print(f"Time to G1: {datetime.now() - start_time}")

        # Solve G2
        initial_state_g2 = cube.CoordCube(cubie_input)
        g2_solution = self.g2_solver.search_for_solution(initial_state_g2)

        print("G2 Solution:", [Data.move_notation[i] for i in g2_solution])

        for move in g2_solution:
            cubie_input.move(move)

        print(f"Time to G2: {datetime.now() - start_time}")

        full_solution = g1_solution + g2_solution
        contracted_solution = self.contract_solution(full_solution)

        print(f"\nWhole Solution ({len(contracted_solution)} moves):", [Data.move_notation[i] for i in contracted_solution])
    
        return contracted_solution
    
if __name__ == "__main__":
    solver = Solver()

    test_cube = cube.CubieCube('YYYYWWYYYGGGGGGGGGRRRRORROROROORBOOOBBBOBBBWBWWWWYYWBW')
    contracted_solution = solver.solve_cube(test_cube)


