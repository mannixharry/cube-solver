import numpy as np

# Assuming lab_data_flat is defined elsewhere in your code
data = lab_data_flat

# Initialize adjacency matrix
adjacency_matrix = np.zeros((54, 54), dtype=float)

# Calculate distances and fill the adjacency matrix
for x in range(54):
    for y in range(x + 1, 54):  # Only need to calculate for y > x (since adjacency is symmetric)
        a = data[x]
        b = data[y]
        distance = np.sqrt(np.sum((a - b) ** 2))  
        adjacency_matrix[x, y] = distance
        adjacency_matrix[y, x] = distance

largest_dist = (0,0)
for i in range(54):

    row = adjacency_matrix[i]
    row_zipped = sorted(enumerate(row), key=lambda x: x[1])
    ninth_dist = row_zipped[8]
    if ninth_dist[1] > largest_dist[1]:
        largest_dist = ninth_dist

row = adjacency_matrix[largest_dist[0]]
deleted = [i[0] for i in sorted(enumerate(row), key=lambda x: x[1])[:9]]
print(deleted)
# Initialize adjacency matrix
aadjacency_matrix = np.zeros((54, 54), dtype=float)

# Calculate distances and fill the adjacency matrix
for x in range(54):
    for y in range(x + 1, 54):  # Only need to calculate for y > x (since adjacency is symmetric)
        if x in deleted or y in deleted:
            aadjacency_matrix[x,y] = np.inf
            adjacency_matrix[y,x] = np.inf
            continue
        a = data[x]
        b = data[y]
        distance = np.sqrt(np.sum((a - b) ** 2))  
        aadjacency_matrix[x, y] = distance
        aadjacency_matrix[y, x] = distance

largest_dist = (0,0)

for i in range(54):
    if i not in deleted:
        row = aadjacency_matrix[i]
        row_zipped = sorted(enumerate(row), key=lambda x: x[1])
    
        ninth_dist = row_zipped[8]
        if ninth_dist[1] > largest_dist[1]:
            largest_dist = ninth_dist

row = adjacency_matrix[largest_dist[0]]
row_zipped = [i[0] for i in sorted(enumerate(row), key=lambda x: x[1])]

print(row_zipped)
print(len(row_zipped))

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Assuming lab_data_flat is defined elsewhere in your code
data = lab_data_flat

# Extract LAB components (assuming data is a list of 3D points in LAB space)
L = [point[0] for point in data]  # L values (lightness)
A = [point[1] for point in data]  # A values (green-red axis)
B = [point[2] for point in data]  # B values (blue-yellow axis)

# Create a 3D scatter plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Scatter plot of all points in LAB space
scatter = ax.scatter(A, B, L, c=L, cmap='viridis', s=50, label="Points in LAB Space")

# Highlight the point with index 39
highlights = [15, 14, 16, 13, 17, 47, 49, 34, 35]

for h in highlights:
    
    ax.scatter(A[h], B[h], L[h], color='red', s=100, edgecolors='black', label="Highlighted Point (Index 39)")

# Add labels and title
ax.set_xlabel('A (Green-Red Axis)')
ax.set_ylabel('B (Blue-Yellow Axis)')
ax.set_zlabel('L (Lightness)')
ax.set_title('3D LAB Color Space with Highlighted Point at Index 39')

# Add a color bar to show the Lightness values
fig.colorbar(scatter, ax=ax, label='Lightness (L)')

# Add a legend
ax.legend()

# Show the plot
plt.show()
print('done')