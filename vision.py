import cv2
import cv2
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
import numpy as np
from sklearn.metrics import pairwise_distances_argmin_min



class CubeCapture():
    def __init__(self):
        pass


    def balanced_k_means(self, data, k, cluster_size, max_iter=100, num_initializations=10):

        n_samples, n_features = data.shape

        best_inertia = np.inf
        best_labels = None
        best_centroids = None

        for init in range(num_initializations):
            # Use scikit-learn's KMeans to cluster data
            kmeans = KMeans(
                n_clusters=k,
                init='k-means++',
                max_iter=max_iter,
                n_init=1,
                random_state=init
            )
            kmeans.fit(data)

            # Get initial cluster labels and centroids
            initial_labels = kmeans.labels_
            centroids = kmeans.cluster_centers_

            # Enforce balance by reassigning points to clusters
            distances, _ = pairwise_distances_argmin_min(data, centroids)
            sorted_indices = np.argsort(distances)
            clusters = [[] for _ in range(k)]

            for idx in sorted_indices:
                # Assign the point to the least populated cluster
                for cluster_id in range(k):
                    if len(clusters[cluster_id]) < cluster_size:
                        clusters[cluster_id].append(idx)
                        break

            # Update labels to reflect balanced assignment
            balanced_labels = np.zeros(n_samples, dtype=int)
            for cluster_id, cluster_indices in enumerate(clusters):
                for idx in cluster_indices:
                    balanced_labels[idx] = cluster_id

            # Compute inertia for the balanced clustering
            inertia = sum(
                np.sum((data[clusters[cluster_id]] - centroids[cluster_id])**2)
                for cluster_id in range(k)
            )

            # Update best solution if this is the best inertia so far
            if inertia < best_inertia:
                best_inertia = inertia
                best_labels = balanced_labels
                best_centroids = centroids

        return best_labels, best_centroids, best_inertia
        

    # Function to draw a smaller, centered 3x3 grid on an image
    def draw_centered_grid(self, image, grid_size=100):

        h, w, _ = image.shape
        center_x, center_y = w // 2, h // 2

        # Calculate the grid boundaries
        half_size = grid_size // 2
        top_left_x, top_left_y = center_x - half_size, center_y - half_size
        bottom_right_x, bottom_right_y = center_x + half_size, center_y + half_size

        # Draw the grid
        cell_size = grid_size // 3
        for i in range(4):
            y = top_left_y + i * cell_size
            x = top_left_x + i * cell_size
            cv2.line(image, (top_left_x, y), (bottom_right_x, y), (255, 255, 255), 2)
            cv2.line(image, (x, top_left_y), (x, bottom_right_y), (255, 255, 255), 2)

        return image, (top_left_x, top_left_y, cell_size)


    # Function to detect the dominant color in a square
    def detect_dominant_color(self, square, neighborhood_fraction=0.25, blur_ksize=5):
        h, w, _ = square.shape
        center_x, center_y = w // 2, h // 2

        # Define the neighborhood size
        offset_x = int(w * neighborhood_fraction // 2)
        offset_y = int(h * neighborhood_fraction // 2)

        # Extract the neighborhood region
        neighborhood = square[center_y - offset_x:center_y + offset_x, center_x - offset_y:center_x + offset_y]

        # Apply Gaussian blur to the neighborhood
        blurred = cv2.GaussianBlur(neighborhood, (blur_ksize, blur_ksize), 0)

        # Calculate the average color in the blurred neighborhood
        avg_color = blurred.mean(axis=0).mean(axis=0)
        return tuple(map(int, avg_color))  # Convert to (B, G, R)

    def capture_cube(self):
        # Initialize webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            exit()

        captured_faces = []  # List to store captured face images
        color_data = []  # List to store color data for each face
        capture_limit = 6  # Number of faces to capture

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            # Draw the smaller, centered 3x3 grid on the frame
            grid_frame, grid_info = self.draw_centered_grid(frame.copy(), grid_size=200)

            # Display the live webcam feed with the smaller grid overlay
            cv2.imshow('Align Your Cube and Press Space', grid_frame)

            key = cv2.waitKey(1)

            if key == ord('q') or key == 27:  # Quit on 'q' or 'Esc'
                break
            elif key == ord(' '):  # Capture on spacebar
                if len(captured_faces) < capture_limit:
                    captured_faces.append(frame.copy())
                    print(f"Captured face {len(captured_faces)}")

                    # Analyze grid colors
                    top_left_x, top_left_y, cell_size = grid_info
                    colors = []
                    for i in range(3):
                        for j in range(3):
                            x1 = top_left_x + j * cell_size
                            y1 = top_left_y + i * cell_size
                            x2 = x1 + cell_size
                            y2 = y1 + cell_size
                            square = frame[y1:y2, x1:x2]
                            dominant_color = self.detect_dominant_color(square)
                            colors.append(dominant_color)
                    color_data.append(colors)
                else:
                    print("All 6 faces have already been captured!")

            # Check if all faces are captured
            if len(captured_faces) == capture_limit:
                break

        cap.release()
        cv2.destroyAllWindows()

        # Example data in BGR format

        lab_data_bgr = np.array(color_data)
        lab_data_bgr_flat = lab_data_bgr.reshape(-1, 3).astype(np.uint8)
        lab_data_bgr_image = lab_data_bgr_flat.reshape(lab_data_bgr.shape[0], lab_data_bgr.shape[1], 3)  # reshape to (height, width, 3)

        lab_data_lab = cv2.cvtColor(lab_data_bgr_image, cv2.COLOR_BGR2LAB)

        k = 6
        cluster_size = 9

        # Flatten `lab_data` into a 2D array
        lab_data_flat = np.array(lab_data_lab).reshape(-1, 3)

        # Perform Balanced K-means
        labels, centroids, inertia = self.balanced_k_means(lab_data_flat, k, cluster_size, 100, 1)

        # Define cluster-to-color mapping
        centre_indices = [4, 22, 13, 31, 40, 49]
        picture_order = [0, 2, 1, 3, 4, 5]
        color_order = ['W', 'G', 'O', 'R', 'B', 'Y']
        cluster_to_color = {}
        for i in range(6):
            cluster_to_color[labels[centre_indices[i]]] = color_order[i]

        # Example: Assuming `labels` contains the cluster labels for all 54 facelets
        # Convert cluster labels to their respective colors

        print(cluster_to_color)

        print(labels)
        facelet_colors = [cluster_to_color[label] for label in labels]

        # Reshape to a 6x9 array (6 faces, each with 9 facelets)
        facelet_array = np.array(facelet_colors).reshape(6, 9)

        new_facelet_array = [facelet_array[picture_order[i]] for i in range(6)]
        facelet_array = np.array(new_facelet_array)

        # Concatenate the facelets into a single string (row-wise for each face)
        facelet_string = ''.join(facelet_array.flatten())

        # Print the single-string representation
        print("Facelet String Representation:")
        print(facelet_string)

if __name__ == '__main__':
    cube_capture = CubeCapture()
    cube_capture.capture_cube()



        