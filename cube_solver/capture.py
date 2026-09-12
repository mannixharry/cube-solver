import cv2
import numpy as np

from . import cube
from .data import *

class Capturer:
    '''Runs the webcam capture flow: photographs each face, averages facelet colours, and
    converts the result into a CubieCube.
    '''

    def __draw_centred_grid(self, image, grid_size=200, vertical_offset=100):
        '''Draws a 3x3 alignment grid on image, centred and offset vertically.

        Returns:
            List[Tuple[int, int]]: screen coordinates of the 9 grid cell centres.
        '''
        height, width, _ = image.shape
        centre_x, centre_y = width // 2, height // 2
        cell_size = grid_size // 3
        half_grid_size = grid_size // 2
        top_left_x, top_left_y = centre_x - half_grid_size, centre_y - half_grid_size + vertical_offset

        # Unit-square line endpoints, scaled up to grid_size and moved to the grid's screen position.
        unit_lines = [[(0, i / 3), (1, i / 3)] for i in range(4)] + [[(j / 3, 0), (j / 3, 1)] for j in range(4)]
        transformed_lines = [[(int(top_left_x + grid_size * x0), int(top_left_y + grid_size * y0)),
                 (int(top_left_x + grid_size * x1), int(top_left_y + grid_size * y1))] for (x0, y0), (x1, y1) in unit_lines]

        for p1, p2 in transformed_lines:
            cv2.line(image, p1, p2, (255, 255, 255), 3)

        grid_centres = [((i - 1) * cell_size + centre_x, centre_y + vertical_offset + cell_size * (j - 1)) for j in range(3) for i in range(3)]
        return grid_centres

    def __get_average_colour(self, image, centre, detection_width):
        '''Returns the average colour of image within detection_width of centre.'''
        x0, x1 = centre[0] - detection_width, centre[0] + detection_width
        y0, y1 = centre[1] - detection_width, centre[1] + detection_width

        detection_region = image[y0:y1, x0:x1]
        return detection_region.mean(axis=(0, 1)).astype(int)

    def __apply_centre_overlay(self, image, centre, overlay_colour, cell_size, transparency=0.5):
        '''Blends overlay_colour into the central cell of the grid, to help align the cube's
        centre facelet with the camera.
        '''
        half_cell_size = cell_size // 2
        x0, x1 = centre[0] - half_cell_size, centre[0] + half_cell_size
        y0, y1 = centre[1] - half_cell_size, centre[1] + half_cell_size

        image[y0:y1, x0:x1] = (1 - transparency) * image[y0:y1, x0:x1] + transparency * np.array(overlay_colour)

    def __apply_top_overlay(self, image, centre, overlay_colour, cell_size, transparency=0.5):
        '''Blends a circular overlay above the grid, to help align the cube's upward-facing side.'''
        half_cell_size = cell_size // 2
        cx, cy = centre[0], centre[1] - 2 * cell_size - half_cell_size
        radius = cell_size // 2

        x0, x1 = cx - half_cell_size, cx + half_cell_size
        y0, y1 = cy - half_cell_size, cy + half_cell_size

        overlay = image.copy()
        cv2.circle(overlay, (cx, cy), radius, overlay_colour, -1)
        image[y0:y1, x0:x1] = (1 - transparency) * image[y0:y1, x0:x1] + transparency * np.array(overlay)[y0:y1, x0:x1]

    def __capture_colour_data(self):
        '''Opens the webcam, lets the user photograph each of the 6 faces, and averages the
        colour under each grid cell.

        Returns:
            List[List[Tuple[int, int, int]]]: average colour of each of the 9 facelets, per face (6x9).
        '''
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            exit()

        ESCAPE_KEY = 27
        CAPTURE_LIMIT = 6
        GRID_SIZE = 200
        CELL_SIZE = GRID_SIZE // 3

        overlay_colours = [Data.overlay_colour_map[i] for i in 'WOGRBY']
        top_overlay_colours = [Data.overlay_colour_map[i] for i in 'OYYYYG']

        captured_faces = 0
        colour_data = []
        while True:
            image_captured, image = cap.read()
            if not image_captured:
                print("Failed to capture image.")
                break

            grid_centres = self.__draw_centred_grid(image, GRID_SIZE, vertical_offset=50)
            centre = grid_centres[4]  # Centre cell of the grid.

            self.__apply_centre_overlay(image, centre, overlay_colours[captured_faces], CELL_SIZE)
            self.__apply_top_overlay(image, centre, top_overlay_colours[captured_faces], CELL_SIZE)

            cv2.imshow('Align Your Cube and Press Space', image)
            key = cv2.waitKey(1)

            if key == ESCAPE_KEY:
                break
            elif key == ord(' '):
                if captured_faces < CAPTURE_LIMIT:
                    captured_faces += 1
                    print(f"Captured face {captured_faces}")

                    colours = [self.__get_average_colour(image.copy(), centre, 10) for centre in grid_centres]
                    print(colours)
                    colour_data.append(colours)
                else:
                    print("All 6 faces have already been captured!")

            if captured_faces == CAPTURE_LIMIT:
                break

        cap.release()
        cv2.destroyAllWindows()

        return colour_data

    def __cluster_colour_data(self, colour_data):
        '''Groups the 54 captured facelet colours into 6 clusters of 9 by similarity.

        Returns:
            List[List[int]]: indices into colour_data for each cluster (e.g. the first list holds
                the indices of the WHITE facelets).
        '''
        data = np.array(colour_data, dtype=np.uint8).reshape(-1, 3)

        adjacency_matrix = np.zeros((54, 54), dtype=float)
        for x in range(54):
            for y in range(x, 54):  # Symmetric, so only compute for y >= x.
                distance = np.linalg.norm(data[y].astype(np.int16) - data[x].astype(np.int16))  # int16 avoids uint8 overflow.
                adjacency_matrix[x, y] = distance
                adjacency_matrix[y, x] = distance

        # Greedily pick, for each face, the unused facelet whose 9 nearest unused neighbours are
        # closest overall - this tends to find a tight cluster before noise gets grouped in.
        clusters = []
        used = []
        for c in range(6):
            lowest_weight = (0, np.inf)
            for i in range(54):
                if i in used:
                    continue
                row_zipped = sorted(
                    [(idx, val) for idx, val in enumerate(adjacency_matrix[i]) if idx not in used],
                    key=lambda x: x[1]
                )[:9]
                total_weight = sum(val for _, val in row_zipped)
                if total_weight < lowest_weight[1]:
                    lowest_weight = (i, total_weight)

            selected_index = lowest_weight[0]
            row_zipped = sorted(
                [(idx, val) for idx, val in enumerate(adjacency_matrix[selected_index]) if idx not in used],
                key=lambda x: x[1]
            )[:9]
            neighbors = [idx for idx, _ in row_zipped]

            used.append(selected_index)
            used.extend(neighbors)

            clusters.append(sorted(neighbors))

        return clusters

    def __convert_clusters_to_cube(self, clusters):
        '''Maps clusters to colours (using the known centre facelet of each), and builds a
        CubieCube if the result is valid and solvable.

        Returns:
            CubieCube: the captured cube.

        Raises:
            ValueError: the capture is not a valid cube, or not solvable.
        '''
        print(clusters)
        centre_indices = [4, 22, 13, 31, 40, 49]
        colour_order = ['W', 'G', 'O', 'R', 'B', 'Y']
        facelet_colours = [''] * 54
        for i, centre_index in enumerate(centre_indices):
            cluster = next(cluster for cluster in clusters if centre_index in cluster)
            for facelet_index in cluster:
                facelet_colours[facelet_index] = colour_order[i]

        facelet_string = ''.join(facelet_colours)
        facelet_string = facelet_string[:9] + facelet_string[18:27] + facelet_string[9:18] + facelet_string[27:]

        captured_cube = cube.FaceletCube(facelet_string)
        if not captured_cube.verify_string_validity():
            print('Cube capture failed. Please retry.')
            raise ValueError('Cube capture failed. Please retry.')

        # The capture order (W, O, G, R, B, Y with O on top) doesn't match a solved cube's facelet
        # layout, so re-orient each face in place to compensate before validating piece placement.
        captured_cube.rotate_colours_on_face(Move.U3)
        captured_cube.rotate_colours_on_face(Move.F2)
        captured_cube.rotate_colours_on_face(Move.R2)
        captured_cube.rotate_colours_on_face(Move.B2)
        captured_cube.rotate_colours_on_face(Move.L2)
        print(''.join(captured_cube.facelets))

        is_valid = captured_cube.verify_validity()
        print(is_valid)
        if not is_valid:
            print('Cube capture failed. Please retry.')
            raise ValueError('Cube capture failed. Please retry.')

        captured_cubie_cube = cube.CubieCube(captured_cube)
        if not captured_cubie_cube.verify_solvability():
            print('Captured cube is not solvable. Please retry')
            raise ValueError('Captured cube is not solvable')

        return captured_cubie_cube

    def capture_cube(self):
        '''Runs the full capture flow.

        Returns:
            CubieCube: the captured cube, or False if capture failed.
        '''
        colour_data = self.__capture_colour_data()
        if len(colour_data) != 6:
            return False

        clusters = self.__cluster_colour_data(colour_data)
        try:
            return self.__convert_clusters_to_cube(clusters)
        except ValueError:
            return False
