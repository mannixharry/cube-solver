import cube  # Assuming cube contains CoordCube and rotation functions
import json
from data import * 
from datetime import datetime

# Start timer
start_time = datetime.now()

class G1Solver:
    def __init__(self):
        # Load pruning tables
        with open('pruning_tables/udslice_corner_table.json', 'r') as corner_file:
            self.udslice_corner_table = json.load(corner_file)
        with open('pruning_tables/udslice_edge_table.json', 'r') as edge_file:
            self.udslice_edge_table = json.load(edge_file)

    def heuristic(self, state):
        """Get the heuristic estimate for the state based on the pruning tables."""
        coord_tuple_corner = (state.UD_slice_coordinate, state.corner_orientation_coordinate)
        coord_tuple_edge = (state.UD_slice_coordinate, state.edge_orientation_coordinate)
        
        # Get heuristic depths from both tables, defaulting to a high depth if not found
        corner_depth = self.udslice_corner_table.get(str(coord_tuple_corner), 12)  # Fallback to max depth
        edge_depth = self.udslice_edge_table.get(str(coord_tuple_edge), 12)  # Fallback to max depth

    # Use the maximum as a combined heuristic
        return max(int(corner_depth), int(edge_depth))
        
    def ida_star(self, initial_state):
        """Perform IDA* search from the initial state."""
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
        """Recursive search function for IDA* with a depth limit."""
        if g > 12:  # Stop if depth exceeds maximum limit
            return float('inf')
        
        f = g + self.heuristic(state)
        if f > threshold:
            return f  # Return the cost threshold should increase to

        # Goal check for G1 (UD slice edges correctly positioned, corners oriented)
        if state.corner_orientation_coordinate == 0 and state.edge_orientation_coordinate == 0 and state.UD_slice_coordinate == 0:
            print('Found G1 solution')
            return path[:]  # Return the current path as solution

        min_cost = float('inf')
        for move in range(18):  # Iterate through 18 possible moves
            if path and move == self.inverse_move(path[-1]):
                continue  # Skip inverse of previous move to avoid redundancy
            
            # Apply move
            next_state = cube.CoordCube(state)  # Copy current state
            next_state.rotate_clockwise(move)  # Apply move

            # Add move to path
            path.append(move)
            
            result = self.search(next_state, g + 1, threshold, path)
            if isinstance(result, list):  # Solution found
                return result
            if result < min_cost:
                min_cost = result  # Update minimum cost for next threshold

            # Backtrack
            path.pop()
        
        return min_cost
    def inverse_move(self, move):
        """Returns the inverse of a move."""
        if 0 <= move < 6:       # For moves 0 to 5, inverse is move + 12 (counterclockwise turn)
            return move + 12
        elif 6 <= move < 12:    # For moves 6 to 11, half-turns are their own inverse
            return move
        elif 12 <= move < 18:   # For moves 12 to 17, inverse is move - 12 (clockwise turn)
            return move - 12

class G2Solver:
    def __init__(self):
        # Load pruning tables for G2 stage
        with open('pruning_tables/main_edge_udslice_edge_table.json', 'r') as mainedge_file:
            self.mainedge_udslice_edge_table = json.load(mainedge_file)
        with open('pruning_tables/corner_udslice_edge_table.json', 'r') as corner_file:
            self.corner_udslice_edge_table = json.load(corner_file)

    def heuristic(self, state):
        """Get the heuristic estimate for the state based on the pruning tables."""
        coord_tuple_mainedge = (state.main_edge_permutation_coordinate, state.UD_slice_edge_permutation_coordinate)
        coord_tuple_corner = (state.corner_permutation_coordinate, state.UD_slice_edge_permutation_coordinate)
        
        # Get heuristic depths from both tables, defaulting to a high depth if not found
        mainedge_depth = self.mainedge_udslice_edge_table.get(str(coord_tuple_mainedge), 18)  # Fallback to max depth
        corner_depth = self.corner_udslice_edge_table.get(str(coord_tuple_corner), 18)  #Fallback to max depth

        # Use the maximum as a combined heuristic
        return max(int(mainedge_depth), int(corner_depth))

    def ida_star(self, initial_state):
        """Perform IDA* search from the initial state."""
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
        """Recursive search function for IDA* with a depth limit."""
        if g > 18:  # Stop if depth exceeds maximum limit
            return float('inf')
        
        f = g + self.heuristic(state)
        if f > threshold:
            return f  # Return the cost threshold should increase to

        # Goal check for G2 (solved state)
        if (
            state.main_edge_permutation_coordinate == 0 and
            state.UD_slice_edge_permutation_coordinate == 0 and
            state.corner_permutation_coordinate == 0
        ):
            print('Found G2 solution')
            return path[:]  # Return the current path as solution

        min_cost = float('inf')
        for move in Data.g2_allowed_moves:  # Only use 10 possible moves for G2 stage
            if path and move == self.inverse_move(path[-1]):
                continue  # Skip inverse of previous move to avoid redundancy
            
            # Apply move
            next_state = cube.CoordCube(state)  # Copy current state
            next_state.rotate_clockwise(move)  # Apply move

            # Add move to path
            path.append(move)
            
            result = self.search(next_state, g + 1, threshold, path)
            if isinstance(result, list):  # Solution found
                return result
            if result < min_cost:
                min_cost = result  # Update minimum cost for next threshold

            # Backtrack
            path.pop()
        
        return min_cost

    def inverse_move(self, move):
        """Returns the inverse of a move."""
        if 0 <= move < 6:       # For moves 0 to 5, inverse is move + 12 (counterclockwise turn)
            return move + 12
        elif 6 <= move < 12:    # For moves 6 to 11, half-turns are their own inverse
            return move
        elif 12 <= move < 18:   # For moves 12 to 17, inverse is move - 12 (clockwise turn)
            return move - 12
        
# Usage:
test_cube = cube.CubieCube('YBYYWWGYYWBOWGRWRWRGROOOBGBBRGBRWGOYOOBBBYGRWOYOWYGRGR')




saved_test = cube.CubieCube(test_cube)

#import main
#main.main(str(cube.FaceletCube(test_cube)))
start_time = datetime.now()
initial_state = cube.CoordCube(test_cube)  # Starting state, assuming this is an unsolved cube in G1
solver = G1Solver()
solution_moves = solver.ida_star(initial_state)

if solution_moves:
    print("Solution found (in terms of move numbers 0-17):", [Data.move_notation[i] for i in solution_moves])
    for move in solution_moves:
        test_cube.rotate_clockwise(move)
        initial_state.rotate_clockwise(move)
        #print(initial_state.get_g1_coordinates())
    #main.main(str(cube.FaceletCube(test_cube)))
    #rint(initial_state.get_g1_coordinates())
else:
    print("No solution found.")

print(f'Time to G1: {datetime.now() - start_time}')

# Usage
initial_state_g2 = cube.CoordCube(test_cube)  # Starting from the G1-solved state for G2 solving
g2_solver = G2Solver()
g2_solution_moves = g2_solver.ida_star(initial_state_g2)

if g2_solution_moves:
    print("Solution found for G2 (move numbers 0-9):", [Data.move_notation[i] for i in g2_solution_moves])
    for move in g2_solution_moves:
        test_cube.rotate_clockwise(move)
        initial_state.rotate_clockwise(move)
        
print(f'Time to G2: {datetime.now() - start_time}')

def contract_solution(moves):
    contracted_moves = []
    i = 0

    while i < len(moves):
        if i + 1 < len(moves) and moves[i] == moves[i + 1]:
            # Check for double moves
            if i + 2 < len(moves) and moves[i] == moves[i + 2]:
                # Triple move (e.g., U U U becomes U')
                contracted_moves.append(moves[i] + '3')
                i += 3
            else:
                # Double move (e.g., U U becomes U2)
                contracted_moves.append(moves[i] + '2')
                i += 2
        elif i + 1 < len(moves) and moves[i] + '3' == moves[i + 1] or moves[i] == moves[i + 1] + '3':
            # Move followed by its inverse (e.g., U U' or U' U cancels out)
            i += 2
        else:
            # Single move, add as-is
            contracted_moves.append(moves[i])
            i += 1

    return contracted_moves


import main
main.main(str(cube.FaceletCube(saved_test)))
main.main(str(cube.FaceletCube(test_cube)))
print(cube.FaceletCube(test_cube))
coord_cube = cube.CoordCube(test_cube)
print(coord_cube.get_g2_coordinates())