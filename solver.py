import cube  # Assuming cube contains CoordCube and rotation functions
import json
from data import * 

class G1Solver:
    def __init__(self):
        # Load pruning tables
        with open('udslice_corner_table.json', 'r') as corner_file:
            self.udslice_corner_table = json.load(corner_file)
        with open('udslice_edge_table.json', 'r') as edge_file:
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
            print('Found')
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

# Usage:
test_cube = cube.CubieCube()
test_cube.rotate_clockwise(Move.R)
test_cube.rotate_clockwise(Move.L3)
test_cube.rotate_clockwise(Move.U2)
test_cube.rotate_clockwise(Move.F)



import main
main.main(str(cube.FaceletCube(test_cube)))
initial_state = cube.CoordCube(test_cube)  # Starting state, assuming this is an unsolved cube in G1
solver = G1Solver()
solution_moves = solver.ida_star(initial_state)

if solution_moves:
    print("Solution found (in terms of move numbers 0-17):", [Data.move_notation[i] for i in solution_moves])
    for move in solution_moves:
        test_cube.rotate_clockwise(move)
        initial_state.rotate_clockwise(move)
        #print(initial_state.get_g1_coordinates())

    #rint(initial_state.get_g1_coordinates())


else:
    print("No solution found.")

print(cube.CoordCube(test_cube).corner_orientation_coordinate, cube.CoordCube(test_cube).edge_orientation_coordinate, cube.CoordCube(test_cube).UD_slice_coordinate)
import main
main.main(str(cube.FaceletCube(test_cube)))