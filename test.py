import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import cv2

# Example color data from the Rubik's cube (replace this with actual `color_data`)
example_color_data =[[(51, 66, 25), (11, 88, 30), (75, 63, 21), (38, 84, 28), (90, 73, 23), (11, 98, 32), (69, 76, 25), (16, 104, 35), (95, 75, 27)], [(14, 108, 112), (99, 96, 108), (7, 110, 122), (98, 104, 103), (11, 123, 112), (102, 102, 103), (9, 113, 101), (82, 111, 115), (28, 123, 108)], [(14, 92, 31), (83, 66, 21), (8, 88, 29), (90, 71, 21), (9, 99, 28), (88, 69, 20), (11, 101, 32), (96, 75, 22), (17, 102, 35)], [(97, 95, 107), (6, 108, 114), (94, 91, 110), (9, 118, 101), (106, 105, 111), (9, 120, 101), (108, 106, 112), (12, 125, 121), (108, 106, 109)], [(29, 40, 159), (22, 5, 116), (23, 35, 157), (23, 7, 106), (23, 36, 168), (20, 3, 108), (26, 41, 175), (23, 
3, 126), (24, 39, 165)], [(29, 12, 104), (26, 38, 173), (23, 4, 111), (24, 42, 159), (28, 7, 121), (24, 39, 161), (26, 5, 124), (31, 46, 183), (32, 10, 129)]]

bgr_colors = []
blue, green, red = [], [], []
for face in example_color_data:
    for (b, g, r) in face:
        blue.append(b)
        green.append(g)
        red.append(r)
        bgr_colors.append((b / 255, g / 255, r / 255))  # Normalize for plotting

# Create a 3D plot for BGR color space
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Scatter plot with exact BGR colors
sc = ax.scatter(blue, green, red, c=bgr_colors, s=100, edgecolor='k')

# Label axes
ax.set_xlabel('Blue Component')
ax.set_ylabel('Green Component')
ax.set_zlabel('Red Component')
ax.set_title('3D Plot of Rubik\'s Cube Colors with Exact Colors')

# Save the plot as an image
plt.savefig("rubiks_cube_colors_exact_bgr.png")

# Convert BGR to HSV and flatten the data for plotting
hue, saturation, value = [], [], []
for face in example_color_data:
    for (b, g, r) in face:
        hsv = cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV)[0][0]
        h, s, v = hsv
        hue.append(h)
        saturation.append(s)
        value.append(v)

# Create a 3D plot for HSV color space
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Scatter plot with exact BGR colors
sc = ax.scatter(hue, saturation, value, c=bgr_colors, s=100, edgecolor='k')

# Label axes
ax.set_xlabel('Hue Component')
ax.set_ylabel('Saturation Component')
ax.set_zlabel('Value Component')
ax.set_title('3D Plot of Rubik\'s Cube Colors in HSV Space with Exact Colors')

# Save the plot as an image
plt.savefig("rubiks_cube_colors_exact_hsv.png")

# Convert BGR to LAB and flatten the data for plotting
l, a, b = [], [], []
for face in example_color_data:
    for (b_val, g_val, r_val) in face:
        lab = cv2.cvtColor(np.uint8([[[b_val, g_val, r_val]]]), cv2.COLOR_BGR2LAB)[0][0]
        l_component, a_component, b_component = lab
        l.append(l_component)
        a.append(a_component)
        b.append(b_component)

# Create a 3D plot for LAB color space
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Scatter plot with exact BGR colors
sc = ax.scatter(l, a, b, c=bgr_colors, s=100, edgecolor='k')

# Label axes
ax.set_xlabel('L Component')
ax.set_ylabel('A Component')
ax.set_zlabel('B Component')
ax.set_title('3D Plot of Rubik\'s Cube Colors in LAB Space with Exact Colors')

# Save the plot as an image
plt.savefig("rubiks_cube_colors_exact_lab.png")

print("Plots saved as 'rubiks_cube_colors_exact_bgr.png', 'rubiks_cube_colors_exact_hsv.png', and 'rubiks_cube_colors_exact_lab.png'.")
