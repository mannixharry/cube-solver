import time
import torch

class RubiksCube:
    def __init__(self, cube_string='WWWWWWWWWOOOOOOOOOGGGGGGGGGRRRRRRRRRBBBBBBBBBYYYYYYYYY'):
        self.cube_string = torch.tensor(list(map(ord, cube_string)), dtype=torch.uint8).cuda()  # Move to GPU

    def get_cube_string(self):
        return ''.join(map(chr, self.cube_string.cpu().tolist()))  # Move to CPU and convert to string

    def __repr__(self):
        cube_string = self.get_cube_string()
        return (f"               {cube_string[0:3]}\n"
                f"               {cube_string[3:6]}\n"
                f"               {cube_string[6:9]}\n"
                f"{cube_string[9:12]}{cube_string[18:21]}{cube_string[27:30]}{cube_string[36:39]}\n"
                f"{cube_string[12:15]}{cube_string[21:24]}{cube_string[30:33]}{cube_string[39:42]}\n"
                f"{cube_string[15:18]}{cube_string[24:27]}{cube_string[33:36]}{cube_string[42:45]}\n"
                f"               {cube_string[48:51]}\n"
                f"               {cube_string[45:48]}\n"
                f"               {cube_string[51:54]}\n")


class CubeRotations:

    def __init__(self):
        self.encoded_rotation_tables = {
            'U': ['F0', 'F1', 'F2', 'L0', 'L1', 'L2', 'B0', 'B1', 'B2', 'R0', 'R1', 'R2'],
            'L': ['F0', 'F3', 'F6', 'D0', 'D3', 'D6', 'B2', 'B5', 'B8', 'U0', 'U3', 'U6'],
            'F': ['U6', 'U7', 'U8', 'R0', 'R3', 'R6', 'D2', 'D1', 'D0', 'L8', 'L5', 'L2'],
            'R': ['F2', 'F5', 'F8', 'U2', 'U5', 'U8', 'B6', 'B3', 'B0', 'D2', 'D5', 'D8'],
            'B': ['U0', 'U1', 'U2', 'L0', 'L3', 'L6', 'D6', 'D7', 'D8', 'R8', 'R5', 'R2'],
            'D': ['F6', 'F7', 'F8', 'R6', 'R7', 'R8', 'B6', 'B7', 'B8', 'L6', 'L7', 'L8']
        }
        self.rotation_tables = {key: torch.tensor(['ULFRBD'.index(i[0]) * 9 + int(i[1]) for i in value], device='cuda') for key, value in self.encoded_rotation_tables.items()}

    def rotate(self, cube, face, is_clockwise=True):
        self._rotate_face(cube, face, is_clockwise)
        self._rotate_edges(cube, face, is_clockwise)

    def _rotate_face(self, cube, face, clockwise=True):
        face_start = 'ULFRBD'.index(face) * 9
        facelet_indices = torch.tensor([6, 3, 0, 7, 4, 1, 8, 5, 2], device='cuda')

        if clockwise:
            new_face = cube.cube_string[face_start + facelet_indices]
        else:
            new_face = cube.cube_string[face_start + facelet_indices.flip(0)]

        cube.cube_string[face_start:face_start+9] = new_face

    def _rotate_edges(self, cube, face, clockwise=True):
        rotation_table = self.rotation_tables[face]
        new_cube = cube.cube_string.clone()

        if clockwise:
            new_cube[rotation_table[(torch.arange(12, device='cuda') + 3) % 12]] = cube.cube_string[rotation_table]
        else:
            new_cube[rotation_table] = cube.cube_string[rotation_table[(torch.arange(12, device='cuda') + 3) % 12]]

        cube.cube_string.copy_(new_cube)


class Solver:

    def __init__(self, cube):
        self.rotator = CubeRotations()
        self.cube = cube

    def get_child_cubes(self):
        children = []
        for i in ['U', 'L', 'F', 'R', 'B', 'D']:
            child_cube1 = RubiksCube(self.cube.get_cube_string())
            child_cube2 = RubiksCube(self.cube.get_cube_string())

            self.rotator.rotate(child_cube1, i, True)
            self.rotator.rotate(child_cube2, i, False)

            children.append(child_cube1)
            children.append(child_cube2)

        return children

    def iterative_deepening_search(self):
        start_time = time.time()
        depth_limit = 0
        nodes_explored = 0

        while True:
            nodes_explored += self.depth_limited_search(depth_limit)
            elapsed_time = time.time() - start_time
            if elapsed_time != 0:
                nodes_per_second = nodes_explored / elapsed_time
                print(f"Depth limit: {depth_limit}, Nodes explored: {nodes_explored}, Nodes per second: {nodes_per_second:.2f}, Elapsed time: {round(elapsed_time, 1)}s")
            depth_limit += 1

    def depth_limited_search(self, depth_limit):
        if depth_limit == 0:
            return 1  # Each leaf node counts as one explored node

        total_nodes = 0
        child_cubes = self.get_child_cubes()
        for child in child_cubes:
            total_nodes += Solver(child).depth_limited_search(depth_limit - 1)

        return total_nodes


def main():
    cube = RubiksCube()
    solver = Solver(cube)
    solver.iterative_deepening_search()


if __name__ == "__main__":
    main()