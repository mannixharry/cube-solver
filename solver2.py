import time 
class RubiksCube:
    def __init__(self):
        # Edge pieces: each element is the position (0-11) of the edge
        self.edge_permutations = list(range(12))
        # Edge orientations: 0 means correct, 1 means flipped
        self.edge_orientations = [0] * 12
        
        # Corner pieces: each element is the position (0-7) of the corner
        self.corner_permutations = list(range(8))
        # Corner orientations: 0, 1, or 2 depending on the twist of the corner
        self.corner_orientations = [0] * 8

    def copy(self):
        new_cube = RubiksCube()
        new_cube.edge_permutations = self.edge_permutations[:]
        new_cube.edge_orientations = self.edge_orientations[:]
        new_cube.corner_permutations = self.corner_permutations[:]
        new_cube.corner_orientations = self.corner_orientations[:]
        return new_cube

    def __repr__(self):
        return (f"Edges: {self.edge_permutations}, Orientations: {self.edge_orientations}\n"
                f"Corners: {self.corner_permutations}, Orientations: {self.corner_orientations}")

class CubeRotations:
    def __init__(self):
        # Rotation tables for edges and corners
        self.edge_rotation_tables = {
            'U': [0, 1, 2, 3], 'D': [8, 9, 10, 11],
            'L': [0, 4, 8, 5], 'R': [2, 6, 10, 7],
            'F': [1, 5, 9, 6], 'B': [0, 3, 11, 4]
        }
        self.edge_orientation_swap = {
            'F': [1, 0, 1, 0], 'B': [1, 0, 1, 0],
            'L': [0, 1, 0, 1], 'R': [0, 1, 0, 1],
            'U': [0, 0, 0, 0], 'D': [0, 0, 0, 0]
        }

        self.corner_rotation_tables = {
            'U': [0, 1, 2, 3], 'D': [4, 5, 6, 7],
            'L': [0, 3, 7, 4], 'R': [1, 2, 6, 5],
            'F': [0, 1, 5, 4], 'B': [2, 3, 7, 6]
        }
        self.corner_orientation_swap = {
            'F': [0, 0, 1, 1], 'B': [0, 0, 1, 1],
            'L': [1, 2, 1, 2], 'R': [1, 2, 1, 2],
            'U': [0, 0, 0, 0], 'D': [0, 0, 0, 0]
        }

    def rotate(self, cube, face, clockwise=True):
        self._rotate_edges(cube, face, clockwise)
        self._rotate_corners(cube, face, clockwise)

    def _rotate_edges(self, cube, face, clockwise=True):
        edges = self.edge_rotation_tables[face]
        orientations = self.edge_orientation_swap[face]
        
        if clockwise:
            self._rotate_pieces(cube.edge_permutations, cube.edge_orientations, edges, orientations, 2)
        else:
            self._rotate_pieces(cube.edge_permutations, cube.edge_orientations, edges[::-1], orientations[::-1], 2)

    def _rotate_corners(self, cube, face, clockwise=True):
        corners = self.corner_rotation_tables[face]
        orientations = self.corner_orientation_swap[face]
        
        if clockwise:
            self._rotate_pieces(cube.corner_permutations, cube.corner_orientations, corners, orientations, 3)
        else:
            self._rotate_pieces(cube.corner_permutations, cube.corner_orientations, corners[::-1], orientations[::-1], 3)

    def _rotate_pieces(self, permutations, orientations, indices, orientation_swaps, orientation_mod):
        temp_perm = [permutations[i] for i in indices]
        temp_orient = [orientations[i] for i in indices]

        for i in range(4):
            permutations[indices[i]] = temp_perm[(i + 3) % 4]
            orientations[indices[i]] = (temp_orient[(i + 3) % 4] + orientation_swaps[i]) % orientation_mod

class Solver:
    def __init__(self, cube):
        self.rotator = CubeRotations()
        self.cube = cube

    def get_child_cubes(self):
        faces = ['U', 'L', 'F', 'R', 'B', 'D']
        children = []
        for face in faces:
            for clockwise in [True, False]:
                child_cube = self.cube.copy()
                self.rotator.rotate(child_cube, face, clockwise)
                children.append(child_cube)
        return children

    def iterative_deepening_search(self):
        start_time = time.time()
        depth_limit = 0

        while True:
            nodes_explored = 0
            nodes_explored += self.depth_limited_search(depth_limit)
            elapsed_time = time.time() - start_time
            nodes_per_second = nodes_explored / elapsed_time if elapsed_time != 0 else 0
            print(f"Depth limit: {depth_limit}, Nodes explored: {nodes_explored}, Nodes per second: {nodes_per_second:.2f}, Elapsed time: {round(elapsed_time, 1)}s")
            depth_limit += 1

    def depth_limited_search(self, depth_limit):
        if depth_limit == 0:
            return 1  # Each leaf node counts as one explored node

        total_nodes = 0
        for child in self.get_child_cubes():
            total_nodes += Solver(child).depth_limited_search(depth_limit - 1)

        return total_nodes


def main():
    cube = RubiksCube()
    solver = Solver(cube)
    solver.iterative_deepening_search()


if __name__ == "__main__":
    main()