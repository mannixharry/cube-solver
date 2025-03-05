import cube
import json
from data import * 
from datetime import datetime

class Solver:
    def __init__(self):
        """
        Initialize the solver with built-in G1 and G2 solvers.
        """
        self.g1_solver = self.StageSolver(
            pruning_data=[
                ('pruning_tables/udslice_corner_table.json', ['UD_slice_coordinate', 'corner_orientation_coordinate']),
                ('pruning_tables/udslice_edge_table.json', ['UD_slice_coordinate', 'edge_orientation_coordinate']),
            ],
            goal_state={
                'corner_orientation_coordinate': 0,
                'edge_orientation_coordinate': 0,
                'UD_slice_coordinate': 0,
            },
            max_depth=12,
            allowed_moves=list(range(18))  # All moves allowed for G1
        )

        self.g2_solver = self.StageSolver(
            pruning_data=[
                ('pruning_tables/main_edge_udslice_edge_table.json', ['eight_edge_permutation_coordinate', 'four_edge_permutation_coordinate']),
                ('pruning_tables/corner_udslice_edge_table.json', ['corner_permutation_coordinate', 'four_edge_permutation_coordinate']),
            ],
            goal_state={
                'eight_edge_permutation_coordinate': 0,
                'four_edge_permutation_coordinate': 0,
                'corner_permutation_coordinate': 0,
            },
            max_depth=18,
            allowed_moves=Data.g2_allowed_moves  # Restricted moves for G2
        )
        
    class StageSolver:
        def __init__(self, pruning_data, goal_state, max_depth, allowed_moves):
            """
            Initialize a stage solver with specific parameters.
            """
            self.coord_tuples = [i[1] for i in pruning_data]
            self.pruning_tables = [self.load_pruning_table(i[0]) for i in pruning_data]
            self.goal_state = goal_state
            self.max_depth = max_depth
            self.allowed_moves = allowed_moves

        @staticmethod
        def load_pruning_table(file_path):
            """Load a pruning table from a JSON file."""
            with open(file_path, 'r') as file:
                return json.load(file)

        def heuristic(self, state):
            """Calculate the heuristic estimate for the given state."""
            depths = [
                table.get(str(tuple(getattr(state, attr) for attr in coord_tuple)), self.max_depth)
                for table, coord_tuple in zip(self.pruning_tables, self.coord_tuples)
            ]
            return max(map(int, depths))

        def ida_star(self, initial_state):
            """Perform IDA* search from the initial state."""
            # Check if the initial state is already in the goal state

            path = []
            threshold = self.heuristic(initial_state)

            while True:
                result = self.search(initial_state, 0, threshold, path)
                if isinstance(result, list):  # Solution found
                    return result
                if result == float('inf'):  # No solution exists within the current threshold
                    return None
                threshold = result  # Increase threshold for the next iteration

        def search(self, state, g, threshold, path):
            """Recursive search function for IDA*."""
            if g > self.max_depth:
                return float('inf')

            f = g + self.heuristic(state)
            if f > threshold:
                return f

            if all(getattr(state, attr) == value for attr, value in self.goal_state.items()):
                return path[:]

            min_cost = float('inf')
            for move in self.allowed_moves:
                if path and move == self.inverse_move(path[-1]):
                    continue  # Skip inverse of previous move
                
                next_state = cube.CoordCube(state)
                next_state.rotate_clockwise(move)

                path.append(move)
                result = self.search(next_state, g + 1, threshold, path)
                if isinstance(result, list):
                    return result
                if result < min_cost:
                    min_cost = result

                path.pop()  # Backtrack

            return min_cost

        @staticmethod
        def inverse_move(move):
            """Returns the inverse of a move."""
            if 0 <= move < 6:
                return move + 12
            elif 6 <= move < 12:
                return move
            elif 12 <= move < 18:
                return move - 12

    @staticmethod
    def contract_solution(solution):
        """
        Simplify a sequence of moves by combining consecutive rotations on the same face.
        """
        contracted_solution = []
        current_face = None
        current_turn_count = 0

        for move in solution:
            face = move % 6
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

        if current_face is not None:
            final_turn_count = current_turn_count % 4
            if final_turn_count != 0:
                contracted_move = current_face + 6 * (final_turn_count - 1)
                contracted_solution.append(contracted_move)

        return contracted_solution

    def solve_cube(self, cube_input):
        """
        Solve the given cube, starting from the G1 stage and progressing to G2.
        """
        start_time = datetime.now()

        if isinstance(cube_input, cube.CubieCube):
            cubie_input = cube_input
        elif isinstance(cube_input, str):
            cubie_input = cube.CubieCube(cube_input)
        elif isinstance(cube_input, cube.FaceletCube):
            cubie_input = cube_input.to_cubie_cube()
        else:
            raise ("Error: cube_input does not match expected type")
        
        initial_state = cube.CoordCube(cubie_input)

        # Solve G1
        g1_solution = self.g1_solver.ida_star(initial_state)
        
        #if not g1_solution:
        #   raise ValueError("Error: No G1 solution found.")
        print("G1 Solution:", [Data.move_notation[i] for i in g1_solution])

        for move in g1_solution:
            cubie_input.move(move)
            initial_state.rotate_clockwise(move)

        print(f"Time to G1: {datetime.now() - start_time}")

        # Solve G2
        initial_state_g2 = cube.CoordCube(cubie_input)
        g2_solution = self.g2_solver.ida_star(initial_state_g2)
        #if not g2_solution:
        #    raise ValueError("Error: No G2 solution found.")
        print("G2 Solution:", [Data.move_notation[i] for i in g2_solution])

        for move in g2_solution:
            cubie_input.move(move)

        print(f"Time to G2: {datetime.now() - start_time}")

        full_solution = g1_solution + g2_solution
        contracted_solution = self.contract_solution(full_solution)

        print(f"\nWhole Solution ({len(contracted_solution)} moves):", [Data.move_notation[i] for i in contracted_solution])
        #print("\nSolution Move Code:", full_solution)

        return contracted_solution, full_solution
    
if __name__ == "__main__":
    solver = Solver()

    test_cube = cube.CubieCube('YYYYWWYYYGGGGGGGGGRRRRORROROROORBOOOBBBOBBBWBWWWWYYWBW')
    contracted_solution, full_solution = solver.solve_cube(test_cube)


# i need to make this so that it can run for a specified amount of time and then return a solution