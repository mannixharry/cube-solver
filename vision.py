import cv2
import numpy as np

# Function to draw a smaller, centered 3x3 grid on an image
def draw_centered_grid(image, grid_size=200):
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
def detect_dominant_color(square):
    avg_color = square.mean(axis=0).mean(axis=0)
    return tuple(map(int, avg_color))  # Convert to (B, G, R)

# Function to overlay colors on a grid
def overlay_colors(image, colors, top_left_x, top_left_y, cell_size):
    for i in range(3):
        for j in range(3):
            color = colors[i * 3 + j]
            x1 = top_left_x + j * cell_size
            y1 = top_left_y + i * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            cv2.rectangle(image, (x1, y1), (x2, y2), color, -1)
    return image

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
    grid_frame, grid_info = draw_centered_grid(frame.copy(), grid_size=200)

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
                    dominant_color = detect_dominant_color(square)
                    colors.append(dominant_color)
            color_data.append(colors)
        else:
            print("All 6 faces have already been captured!")
print(color_data)

# After all captures, overlay detected colors on each image
if len(captured_faces) == capture_limit:
    for idx, face in enumerate(captured_faces):
        overlay_frame = face.copy()
        top_left_x, top_left_y, cell_size = draw_centered_grid(overlay_frame, grid_size=200)[1]
        overlay_colors(overlay_frame, color_data[idx], top_left_x, top_left_y, cell_size)
        cv2.imshow(f"Face {idx + 1} with Colors", overlay_frame)
import time 

cap.release()
cv2.destroyAllWindows()

#essentially take 6 photos. load the colour pictures in a facelet array. analyze the facelet array to find facelets with similar colours. group these facelets. and print their colours.