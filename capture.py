
import cv2
import cube
from data import *
import numpy as np

class Capturer():
    '''Manages the web-cam application to capture a cube.
    '''
    def __draw_centred_grid(self, image, grid_size=200, vertical_offset=100):
        '''Overlays a grid onto the input image; so that the user can align their cube with the grid squares.

        Args:
            image (np.ndarray): Image to draw grid on.
            grid_size (int, optional): Side length of the whole grid. Defaults to 200.
            vertical_offset (int, optional): Height, below the centre of the screen, at which the cube is drawn. Defaults to 100.

        Returns:
            Tuple[np.ndarray, int, List[Tuple[int, int]]]: 
                - np.ndarray: Image with the grid overlay.
                - int: Cell size (length of an individual grid square).
                - List[Tuple[int, int]]: Coordinates of the 9 grid centers.
        '''
        height, width, _ = image.shape
        centre_x, centre_y = width // 2, height // 2

        cell_size = grid_size // 3
        half_grid_size = grid_size // 2
        top_left_x, top_left_y = centre_x - half_grid_size, centre_y - half_grid_size + vertical_offset
        unit_lines = [[(0, i / 3), (1, i / 3)] for i in range(4)] + [[(j / 3, 0), (j / 3, 1)] for j in range(4)]
        transformed_lines = [[(int(top_left_x + grid_size * x0),int(top_left_y + grid_size * y0)),
                 (int(top_left_x + grid_size * x1), int(top_left_y + grid_size * y1))] for (x0, y0), (x1, y1) in unit_lines]
        
        for line in transformed_lines:
            p1, p2 = line
            cv2.line(image, p1, p2, (255, 255, 255), 3)

        grid_centres = [((i - 1) * cell_size + centre_x, centre_y + vertical_offset + cell_size * (j - 1)) for j in range(3) for i in range(3)]
        
        return image, cell_size, grid_centres

    def __get_average_colour(self, image, centre, detection_width):
        '''Computes the average colour of the image in the viscinity of given point.

        Args:
            image (np.ndarray): Image to compute average colour of.
            centre (Tuple[int, int]): Coordinate of point to calculate average at. 
            detection_width (int): Side length of the window (a square) that the average is calculated for.

        Returns:
            Tuple[int, int, int]: average colour around point.
        '''
        x0, x1 = centre[0] - detection_width, centre[0] + detection_width
        y0, y1 = centre[1] - detection_width, centre[1] + detection_width

        region = image[y0:y1, x0:x1]

        avg_colour = region.mean(axis=(0,1)) # region is a numpy array 
        return tuple(map(int, avg_colour))
    
    def __apply_centre_overlay(self, image, centre, overlay_colour, cell_size, transparency=0.5):
        '''Overlays a colour on the central square of the input image. 
        The colour is used to align the central square of the camera-facing side of the cube. 

        Args:
            image (np.ndarray): Image to draw overlay on.
            centre (Tuple[int, int]): Coordinate of centre of the central square.
            overlay_colour (Tuple[int, int, int]): Colour of the overlay.
            cell_size (int): Side length of the central cell. 
            transparency (float, optional): Blending ratio between input image and overlay. Defaults to 0.5.
        '''
        half_cell_size = cell_size // 2
        x0, x1 = centre[0] - half_cell_size, centre[0] + half_cell_size
        y0, y1 = centre[1] - half_cell_size, centre[1] + half_cell_size

        image[y0:y1, x0:x1] = (1 - transparency) * image[y0:y1, x0:x1] + transparency * np.array(overlay_colour)
        
    def __apply_top_overlay(self, image, centre, overlay_colour, cell_size, transparency=0.5):
        '''Overlays a circular region of colour above the grid on the input image. 
        The overlay is used to align the central square of the upwards pointing face.
        Args:
            image (np.ndarray): Image to draw overlay on.
            centre (Tuple[int, int]): Coordinate of centre of the central square.
            overlay_colour (Tuple[int, int, int]): Colour of the overlay.
            cell_size (int): Side length of the central cell. 
            transparency (float, optional): Blending ratio between input image and overlay. Defaults to 0.5.
        '''
        half_cell_size = cell_size // 2
        cx, cy = centre[0], centre[1] - 2 * cell_size - half_cell_size
        radius = cell_size // 2

        x0, x1 = cx - half_cell_size, cx + half_cell_size
        y0, y1 = cy - half_cell_size, cy + half_cell_size

        # Draw the circle
        overlay = image.copy()
        cv2.circle(overlay, (cx, cy), radius, overlay_colour, -1) # filled circle 

        image[y0:y1, x0:x1] = (1 - transparency) * image[y0:y1, x0:x1] + transparency * np.array(overlay)[y0:y1, x0:x1]

    def __capture_colour_data(self):
        '''Opens the web-cam application, captures an image of each face, and computes average colours.

        Returns:
            List[List[Tuple[int, int, int]]]: Colour data (6 x 9). 
            Stores average colour of each facelet on each face. (54 'colour' tuples)
        '''

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            exit()

        ESCAPE_KEY = 27
        CAPTURE_LIMIT = 6
        GRID_SIZE = 200

        overlay_colours = [Data.overlay_colour_map[i] for i in 'WOGRBY']
        top_overlay_colours = [Data.overlay_colour_map[i] for i in 'OYYYYG']

        captured_faces = 0
        colour_data = []
        while True:
            image_captured, image = cap.read()
            if not image_captured:
                print("Failed to capture image.")
                break
            
            grid_image, cell_size, grid_centres = self.__draw_centred_grid(image.copy(), GRID_SIZE, vertical_offset=50)
            centre = grid_centres[4]
            # Apply overlays
            self.__apply_centre_overlay(grid_image, centre, overlay_colours[captured_faces], cell_size)
            self.__apply_top_overlay(grid_image, centre, top_overlay_colours[captured_faces], cell_size)

            cv2.imshow('Align Your Cube and Press Space', grid_image)
            key = cv2.waitKey(1)
            
            if key == ESCAPE_KEY:  # Quit on 'Escape'
                break
            elif key == ord(' '):  # Capture on spacebar
                if captured_faces < CAPTURE_LIMIT:
                    captured_faces += 1
                    
                    print(f"Captured face {captured_faces}")

                    colours = []
                    for centre in grid_centres:
                        average_colour = self.__get_average_colour(image.copy(), centre, 10)
                        colours.append(average_colour)
                        
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
        '''Groups colours by similarity into 6 groups of 9 colours.

        Args:
            colour_data (List[List[Tuple[int, int, int]]]): captured average colours.

        Returns:
            List[[List[int]]]: Clusters. List of lists of indices of data values in colour_data that are most similar. (6*9)
            ie: first list contains indices of WHITE facelets on the captured cube. 
        '''

        data = np.array(colour_data, dtype=np.uint8).reshape(-1, 3) # flattens colour_data into an array of tuples.

        # Initialize adjacency matrix
        adjacency_matrix = np.zeros((54, 54), dtype=float)

        # Calculate distances and fill the adjacency matrix
        for x in range(54):
            for y in range(x, 54):  # Only need to calculate for y >= x (since adjacency is symmetric)
                a = data[x]
                b = data[y]
                distance = np.linalg.norm(b.astype(np.int16) - a.astype(np.int16))  # Correct overflow
                adjacency_matrix[x, y] = distance
                adjacency_matrix[y, x] = distance

        # Find groups of 9 nearest neighbors without repeating
        clusters = []
        used = []
        for c in range(6):
            lowest_weight = (0, np.inf)
            for i in range(54):
                if i in used:
                    continue  # Skip indices that are already used
                row = np.copy(adjacency_matrix[i])
                row_zipped = sorted(
                    [(idx, val) for idx, val in enumerate(row) if idx not in used], 
                    key=lambda x: x[1]
                )[:9]  # Get 9 nearest unused neighbors
                total_weight = sum(val for _, val in row_zipped)
                if total_weight < lowest_weight[1]:
                    lowest_weight = (i, total_weight)

            # Add the selected index and its neighbors to 'used' one by one
            selected_index = lowest_weight[0]
            row = np.copy(adjacency_matrix[selected_index])
            row_zipped = sorted(
                [(idx, val) for idx, val in enumerate(row) if idx not in used], 
                key=lambda x: x[1]
            )[:9]
            neighbors = [idx for idx, _ in row_zipped]
            
            # Append selected index and neighbors to 'used'
            used.append(selected_index)
            for neighbor in neighbors:
                used.append(neighbor)

            # Print the neighbors without duplicating the first index
            clusters.append(sorted(neighbors))

        return clusters

    def __convert_clusters_to_cube(self, clusters):
        '''Converts cluster data to a CubieCube object.
        Ensures processed data give rise to a valid, solvable cube. 

        Args:
            clusters (List[[List[int]]]): Cluster data to convert to a CubieCube.

        Returns:
            CubieCube, False: A CubieCube representation of the captured cube.
            Otherwise, if it is not valid or solvable, False.

        Raises: 
            ValueError: 
                - if cube is not valid (ie not equal numbers of each colour).
                - if cube is not solvable. 
        '''
        print(clusters)
        # Define cluster-to-colour mapping
        centre_indices = [4, 22, 13, 31, 40, 49]
        picture_order = [0, 1, 2, 3, 4, 5]
        colour_order = ['W', 'G', 'O', 'R', 'B', 'Y']
        facelet_colours = [''] * 54
        for i, c in enumerate(centre_indices):
            index = next((i for i, sublist in enumerate(clusters) if c in sublist), None)
            colour = colour_order[picture_order[i]]
            for j in clusters[index]:
                facelet_colours[j] = colour

        facelet_string = ''.join(facelet_colours)
        facelet_string = facelet_string[:9] + facelet_string[18:27] + facelet_string[9:18] + facelet_string[27:]

        captured_cube = cube.FaceletCube(facelet_string)
        valid = captured_cube.verify_string_validity()
        if valid:
            captured_cube.rotate_colours_on_face(Move.U3)
            captured_cube.rotate_colours_on_face(Move.F2)
            captured_cube.rotate_colours_on_face(Move.R2)
            captured_cube.rotate_colours_on_face(Move.B2)
            captured_cube.rotate_colours_on_face(Move.L2)
            print(''.join(captured_cube.facelets))

            valid = captured_cube.verify_validity()
            print(valid)
            if valid:
                captured_cubie_cube = cube.CubieCube(captured_cube)
                solvable = captured_cubie_cube.verify_solvability()
                if solvable:
                    return captured_cubie_cube
                else:
                    print('Captured cube is not solvable. Please retry')
                    raise ValueError('Captured cube is not solvable')
                    
        if not valid:
            print('Cube capture failed. Please retry.')
            raise ValueError('Cube capture failed. Please retry.')
            

    def capture_cube(self):
        '''Runs the cube capture software. 

        Returns:
            CubieCube, False: The captured CubieCube. False if there is an error.
        '''
        colour_data = self.__capture_colour_data()
        if len(colour_data) == 6:
            clusters = self.__cluster_colour_data(colour_data)
            try:
                cube = self.__convert_clusters_to_cube(clusters)
            except ValueError:
                return False 
        return cube
    
