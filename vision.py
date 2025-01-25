
import cv2
import main
import cube
from data import *
import numpy as np 

class Capturer():
    def draw_centered_grid(self, image, grid_size=200, offset=100):
        """Draws a 3x3 grid on the image with an adjustable vertical offset."""
        h, w, _ = image.shape
        center_x, center_y = w // 2, h // 2 + offset  # Adjust vertical position with offset

        half_size = grid_size // 2
        top_left_x, top_left_y = center_x - half_size, center_y - half_size
        bottom_right_x, bottom_right_y = center_x + half_size, center_y + half_size

        cell_size = grid_size // 3
        for i in range(4):
            y = top_left_y + i * cell_size
            x = top_left_x + i * cell_size
            cv2.line(image, (top_left_x, y), (bottom_right_x, y), (255, 255, 255), 2)
            cv2.line(image, (x, top_left_y), (x, bottom_right_y), (255, 255, 255), 2)

        return image, (top_left_x, top_left_y, cell_size)

    def detect_dominant_colour(self, square, neighborhood_fraction=0.5, blur_ksize=5):
        """Detects the dominant color in a square region."""
        h, w, _ = square.shape
        center_x, center_y = w // 2, h // 2

        offset_x = int(w * neighborhood_fraction // 2)
        offset_y = int(h * neighborhood_fraction // 2)
        neighborhood = square[center_y - offset_x:center_y + offset_x, center_x - offset_y:center_y + offset_y]
        blurred = cv2.GaussianBlur(neighborhood, (blur_ksize, blur_ksize), 0)
        avg_colour = blurred.mean(axis=0).mean(axis=0)
        return tuple(map(int, avg_colour))

    def apply_overlay(self, grid_frame, grid_info, overlay_colour, alpha=0.5):
        """Applies a transparent overlay to the middle grid square."""
        top_left_x, top_left_y, cell_size = grid_info
        mid_x1 = top_left_x + cell_size
        mid_y1 = top_left_y + cell_size
        mid_x2 = mid_x1 + cell_size
        mid_y2 = mid_y1 + cell_size

        overlay_image = np.full((mid_y2 - mid_y1, mid_x2 - mid_x1, 3), overlay_colour, dtype=np.uint8)
        roi = grid_frame[mid_y1:mid_y2, mid_x1:mid_x2]
        blended = cv2.addWeighted(roi, 1 - alpha, overlay_image, alpha, 0)
        grid_frame[mid_y1:mid_y2, mid_x1:mid_x2] = blended

    def apply_top_overlay(self, grid_frame, grid_info, overlay_colour, alpha=0.5):
        """Draws a circular overlay disjoint from the grid by one cell size."""
        top_left_x, top_left_y, cell_size = grid_info

        # Center position of the circle
        circle_center_x = top_left_x + cell_size * 1.5
        circle_center_y = top_left_y - cell_size * 1.5

        # Radius of the circle
        radius = cell_size // 2

        # Draw the circle
        overlay = grid_frame.copy()
        cv2.circle(overlay, (int(circle_center_x), int(circle_center_y)), radius, overlay_colour, -1)

        # Blend the overlay with the grid frame
        cv2.addWeighted(overlay, alpha, grid_frame, 1 - alpha, 0, grid_frame)

    def capture_colour_data(self):
        """Captures color data for a Rubik's cube."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            exit()

        captured_faces = []
        colour_data = []
        capture_limit = 6

        overlay_colours = [
            (255, 255, 255),  # White
            (0, 165, 255),    # Orange
            (0, 255, 0),      # Green
            (0, 0, 255),      # Red
            (255, 0, 0),      # Blue
            (0, 255, 255)     # Yellow
        ]

        top_overlay_colours = [
            (0, 165, 255),  # Orange
            (0, 255, 255),  # Yellow
            (0, 255, 255),  # Yellow
            (0, 255, 255),  # Yellow
            (0, 255, 255),  # Yellow
            (0, 255, 0)     # Green
        ]

        overlay_index = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            grid_frame, grid_info = self.draw_centered_grid(frame.copy(), grid_size=200, offset=50)
            
            # Apply overlays
            self.apply_overlay(grid_frame, grid_info, overlay_colours[overlay_index])
            self.apply_top_overlay(grid_frame, grid_info, top_overlay_colours[overlay_index])

            cv2.imshow('Align Your Cube and Press Space', grid_frame)
            key = cv2.waitKey(1)

            if key == ord('q') or key == 27:  # Quit on 'q' or 'Esc'
                break
            elif key == ord(' '):  # Capture on spacebar
                if len(captured_faces) < capture_limit:
                    overlay_index += 1
                    captured_faces.append(frame.copy())
                    print(f"Captured face {len(captured_faces)}")

                    top_left_x, top_left_y, cell_size = grid_info
                    colours = []
                    for i in range(3):
                        for j in range(3):
                            x1 = top_left_x + j * cell_size
                            y1 = top_left_y + i * cell_size
                            x2 = x1 + cell_size
                            y2 = y1 + cell_size
                            square = frame[y1:y2, x1:x2]
                            dominant_colour = self.detect_dominant_colour(square)
                            colours.append(dominant_colour)
                    colour_data.append(colours)
                else:
                    print("All 6 faces have already been captured!")

            if len(captured_faces) == capture_limit:
                break

        cap.release()
        cv2.destroyAllWindows()

        return colour_data
    
    def cluster_colour_data(self, colour_data):
        # Assuming lab_data_flat is defined elsewhere in your code
        data = np.array(colour_data, dtype=np.uint8).reshape(-1, 3)
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

    def convert_clusters_to_cube(self, clusters):

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
            if valid:
                captured_cubie_cube = cube.CubieCube(captured_cube)
                solvable = captured_cubie_cube.verify_solvability()
                if solvable:
                    return captured_cubie_cube
                else:
                    print('Captured cube is not solvable. Please retry')
                    return False 
        if not valid:
            print('Cube capture failed. Please retry.')
            return False

    def capture_cube(self):
        
        colour_data = self.capture_colour_data()
        if len(colour_data) == 6:
            clusters = self.cluster_colour_data(colour_data)
            cube = self.convert_clusters_to_cube(clusters)
        else:
            return False
        return cube # Either returns the cube or False. 