import json
import time
from abc import ABC, abstractmethod
from datetime import datetime

from . import cube
cube.import_tables()
from .data import *
from .paths import PRUNING_TABLES_DIR

# Coordinate-space sizes, used to flatten (coordinate_1, coordinate_2) pairs into a single
# index into a dense pruning table array: index = coordinate_1 * dim2 + coordinate_2.
CORNER_ORIENTATION_SIZE = 3 ** 7   # 2187
EDGE_ORIENTATION_SIZE = 2 ** 11    # 2048
FOUR_EDGE_PERMUTATION_SIZE = 24

class PruningTables:
    '''Loads pruning tables from local files.

    Attributes:
        UD_slice_corner_table (list): UD slice position, corner orientation table (g1 heuristic).
        UD_slice_edge_table (list): UD slice position, edge orientation table (g1 heuristic).
        corner_four_edge_table (list): corner permutation, four edge permutation table (g2 heuristic).
        eight_edge_four_edge_table (list): eight edge permutation, four edge permutation table (g2 heuristic).
    '''
    def __init__(self):
        with open(PRUNING_TABLES_DIR / 'UD_slice_corner_table.json', 'r') as file:
            self.UD_slice_corner_table = json.load(file)
        with open(PRUNING_TABLES_DIR / 'UD_slice_edge_table.json', 'r') as file:
            self.UD_slice_edge_table = json.load(file)
        with open(PRUNING_TABLES_DIR / 'corner_four_edge_table.json', 'r') as file:
            self.corner_four_edge_table = json.load(file)
        with open(PRUNING_TABLES_DIR / 'eight_edge_four_edge_table.json', 'r') as file:
            self.eight_edge_four_edge_table = json.load(file)

def import_tables():
    '''Loads pruning tables into the global pruning_tables.

    Deferred to a function since solver.py would otherwise try to load pruning tables before
    pruning_table_generator.py has had a chance to generate them.
    '''
    global pruning_tables
    pruning_tables = PruningTables()

class Solver:
    '''Solves the cube using Kociemba's two-phase algorithm: first to the g1 subset, then to solved.'''
    def __init__(self):
        self.__g1_solver = self.g1Solver()
        self.__g2_solver = self.g2Solver()

    class StageSolver(ABC):
        '''Abstract parent for g1Solver and g2Solver.
        Each child implements _heuristic_function and _is_solved_function; search_for_solutions is shared.
        '''
        def __init__(self, max_depth, allowed_moves):
            self.max_depth = max_depth
            self.allowed_moves = allowed_moves

        @abstractmethod
        def _heuristic_function(self, state):
            '''Looks up the admissible heuristic (lower bound on moves to solve) for state.'''
            pass

        @abstractmethod
        def _is_solved_function(self, state):
            '''Checks whether state meets this stage's solved condition.'''
            pass

        def search_for_solutions(self, state, threshold=0, deadline=None, max_depth=None):
            '''IDA* search, yielding solutions in increasing order of length.
            Iterative (stack-based) DFS to avoid Python's recursion depth limit, pruned by the
            heuristic function; each recursive pass raises the threshold to the smallest f-score
            that was pruned in the previous pass.

            Args:
                state (CoordCube): state to search from.
                threshold (int, optional): f-score cutoff for this pass. Defaults to 0.
                deadline (float, optional): perf_counter() time to give up by. Defaults to no deadline.
                max_depth (int, optional): overrides self.max_depth for this call (and its deepening
                    passes). Callers pass a tighter cap once they already have a solution to beat, so
                    the search doesn't waste time exploring depths that can't possibly improve on it.

            Yields:
                List[Move]: each solution found, in increasing order of length.
            '''
            effective_max_depth = self.max_depth if max_depth is None else min(max_depth, self.max_depth)
            if effective_max_depth < 0:
                return # No depth can possibly improve on the caller's bound.

            stack = [(state, [])]
            min_f = float('inf')
            nodes_checked = 0
            while stack:  # Hot path
                nodes_checked += 1
                if deadline is not None and nodes_checked % 1000 == 0 and time.perf_counter() > deadline:
                    return  # Timeout mid-pass

                current_state, current_path = stack.pop()
                g_score = len(current_path)
                h_score = self._heuristic_function(current_state)
                f_score = g_score + h_score

                if f_score > threshold or g_score > effective_max_depth:
                    if f_score < min_f:
                        min_f = f_score
                    continue

                coord = cube.CoordCube(current_state)
                if self._is_solved_function(coord):
                    yield current_path
                    continue

                for move in self.allowed_moves:
                    if current_path:
                        last_face = current_path[-1] % 6
                        face = move % 6
                        if face == last_face:  # Ignore same-face moves.
                            continue
                        if face == Data.opposite_face[last_face] and face < last_face:
                            continue  # Canonical ordering for opposite-face moves (which commute).

                    next_state = cube.CoordCube(current_state)
                    next_state.move(move)
                    stack.append((next_state, current_path + [move]))

            if deadline is not None and time.perf_counter() > deadline:
                return
            if min_f == float('inf') or min_f > effective_max_depth:
                return

            yield from self.search_for_solutions(state, min_f, deadline, max_depth)

    class g1Solver(StageSolver):
        '''Solves the cube to the g1 subset.'''
        def __init__(self):
            max_depth = 12
            allowed_moves = Data.g1_allowed_moves
            super().__init__(max_depth, allowed_moves)

            self.__UD_slice_corner_table = pruning_tables.UD_slice_corner_table
            self.__UD_slice_edge_table = pruning_tables.UD_slice_edge_table

        def _heuristic_function(self, state):
            d1 = self.__UD_slice_corner_table[state.UD_slice_coordinate * CORNER_ORIENTATION_SIZE + state.corner_orientation_coordinate]
            d2 = self.__UD_slice_edge_table[state.UD_slice_coordinate * EDGE_ORIENTATION_SIZE + state.edge_orientation_coordinate]
            return max(d1, d2)

        def _is_solved_function(self, state):
            return sum(state.g1_coordinates) == 0

    class g2Solver(StageSolver):
        '''Solves the g1-subset cube the rest of the way to solved.'''
        def __init__(self):
            max_depth = 18
            allowed_moves = Data.g2_allowed_moves
            super().__init__(max_depth, allowed_moves)

            self.__corner_four_edge_table = pruning_tables.corner_four_edge_table
            self.__eight_edge_four_edge_table = pruning_tables.eight_edge_four_edge_table

        def _heuristic_function(self, state):
            d1 = self.__corner_four_edge_table[state.corner_permutation_coordinate * FOUR_EDGE_PERMUTATION_SIZE + state.four_edge_permutation_coordinate]
            d2 = self.__eight_edge_four_edge_table[state.eight_edge_permutation_coordinate * FOUR_EDGE_PERMUTATION_SIZE + state.four_edge_permutation_coordinate]
            return max(d1, d2)

        def _is_solved_function(self, state):
            return sum(state.g2_coordinates) == 0

    def __contract_solution(self, solution):
        '''Merges consecutive same-face moves in solution into a single turn (e.g. U, U -> U2).

        Returns:
            List[Move]: contracted solution.
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

    def solve_cube(self, cube_input, time_limit=1.0):
        '''Solves cube_input to g1, then to solved, and contracts the combined solution.
        Unsolvable cubes aren't handled here since capture.py already rules them out.

        Args:
            cube_input (CubieCube, FaceletCube, str): cube to solve.

        Returns:
            List[Move]: contracted solution.
        '''
        start_time = datetime.now()
        deadline = time.perf_counter() + time_limit

        cubie_input = cube.CubieCube(cube_input)
        initial_state = cube.CoordCube(cubie_input)

        ATTEMPT_BUDGET = 0.1
        GRACE_BUDGET = 3.0  # extra time to guarantee a result if nothing was found by the deadline

        best_solution = None
        best_length = float('inf')
        candidates_tried = 0

        def try_candidates(search_deadline):
            nonlocal best_solution, best_length, candidates_tried

            for g1_solution in self.__g1_solver.search_for_solutions(initial_state, deadline=search_deadline):
                now = time.perf_counter()
                if now > search_deadline:
                    break

                if len(g1_solution) >= best_length:
                    continue

                g1_cubie = cube.CubieCube(cubie_input)
                for move in g1_solution:
                    g1_cubie.move(move)
                g1_state = cube.CoordCube(g1_cubie)

                g2_lower_bound = self.__g2_solver._heuristic_function(g1_state)
                if len(g1_solution) + g2_lower_bound >= best_length:
                    continue  # Cheap admissible bound prunes this.

                depth_cap = None if best_length == float('inf') else best_length - len(g1_solution) - 1
                attempt_deadline = min(search_deadline, now + ATTEMPT_BUDGET)

                g2_solution = next(
                    self.__g2_solver.search_for_solutions(g1_state, deadline=attempt_deadline, max_depth=depth_cap),
                    None
                )
                if g2_solution is None:
                    continue  # g2 search didn't improve on best_length within its budget; try the next g1 candidate.

                total_length = len(g1_solution) + len(g2_solution)
                candidates_tried += 1

                if total_length < best_length:
                    best_length = total_length
                    best_solution = g1_solution + g2_solution

        try_candidates(deadline)

        if best_solution is None:
            try_candidates(time.perf_counter() + GRACE_BUDGET)

        if best_solution is None:
            try_candidates(time.perf_counter() + 60.0)

        contracted_solution = self.__contract_solution(best_solution or [])
        print(f"Tried {candidates_tried} candidates in {datetime.now() - start_time}")
        print(f"\nWhole Solution ({len(contracted_solution)} moves):", [Data.move_notation[i] for i in contracted_solution])

        return contracted_solution
