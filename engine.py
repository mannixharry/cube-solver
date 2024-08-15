import pygame
from pygame.locals import *
import numpy as np

class Render:
    def create_window(self, width, height):
        pygame.init()
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Basic 3D Engine')
        screen.fill((255, 255, 255))  # Fill the screen with white
        pygame.display.flip()  # Update the display
        return screen

    def __init__(self):
        width, height = 800, 800
        self.width = width
        self.height = height
        self.thickness = 1
        self.screen = self.create_window(width, height)
        self.colour = (0, 0, 0)
        self.font = pygame.font.SysFont('Arial', 20)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
        return True
    
    def draw_line(self, a, b):
        pygame.draw.line(self.screen, 'aqua', a, b, self.thickness)

    def draw_triangle(self, a, b, c):
        pygame.draw.line(self.screen, self.colour, a, b, self.thickness)
        pygame.draw.line(self.screen, self.colour, b, c, self.thickness)
        pygame.draw.line(self.screen, self.colour, c, a, self.thickness)

    def display_fps(self, fps):
        fps_text = self.font.render(f'FPS: {int(fps)}', True, self.colour)
        self.screen.blit(fps_text, (10, 10))  # Display at the top-left corner

class Triangle:
    def __init__(self, a, b, c):
        self.a = np.array(a)
        self.b = np.array(b)
        self.c = np.array(c)
        self.vertices = [self.a, self.b, self.c]

    def __getitem__(self, index):
        if 0 <= index <= 2:
            return self.vertices[index]
        else:
            raise IndexError("Index out of range. Valid indices are 0, 1, or 2.")

    def __iter__(self):
        return iter(self.vertices)
    
    def get_normal(self):

        vector_x = self.b - self.a
        vector_y = self.c - self.a
        normal = np.cross(vector_x, vector_y)
        x, y, z = normal
        m = np.sqrt(x**2 + y**2 + z**2)
        normalised_normal = np.array([x/m, y/m, z/m])
        return normalised_normal
    
    
class Cube:
    def __init__(self, translation_vector, scale=1):
        # Define base triangles for a unit cube
        base_triangles = [
            Triangle([0, 0, 0], [0, 1, 0], [1, 1, 0]),
            Triangle([0, 0, 0], [1, 1, 0], [1, 0, 0]),
            Triangle([1, 0, 0], [1, 1, 0], [1, 1, 1]),
            Triangle([1, 0, 0], [1, 1, 1], [1, 0, 1]),
            Triangle([1, 0, 1], [1, 1, 1], [0, 1, 1]),
            Triangle([1, 0, 1], [0, 1, 1], [0, 0, 1]),
            Triangle([0, 0, 1], [0, 1, 1], [0, 1, 0]),
            Triangle([0, 0, 1], [0, 1, 0], [0, 0, 0]),
            Triangle([0, 1, 0], [0, 1, 1], [1, 1, 1]),
            Triangle([0, 1, 0], [1, 1, 1], [1, 1, 0]),
            Triangle([1, 0, 1], [0, 0, 1], [0, 0, 0]),
            Triangle([1, 0, 1], [0, 0, 0], [1, 0, 0]),
        ]

        # Apply translation and scaling to each triangle's vertices
        self.triangles = []
        for triangle in base_triangles:
            new_a = (triangle.a + translation_vector) * scale
            new_b = (triangle.b + translation_vector) * scale
            new_c = (triangle.c + translation_vector) * scale
            self.triangles.append(Triangle(new_a, new_b, new_c))
    
class Projector:
    def __init__(self, renderer):
        self.width, self.height = renderer.width, renderer.height
        self.fov = 90
        self.znear, self.zfar = 0.1, 1000

        x = self.height / self.width
        y = 1 / np.tan(self.fov * np.pi / 360)
        z = self.zfar / (self.zfar - self.znear)

        self.projection_matrix = np.array([
            [x * y, 0, 0, 0],
            [0, y, 0, 0],
            [0, 0, z, 1],
            [0, 0, -self.znear * z, 0]
        ])

    def project_vector(self, vector):
        vector_homogeneous = np.append(vector, 1)  # Convert to 4D
        projected_vector = self.projection_matrix @ vector_homogeneous

        if projected_vector[3] != 0:
            projected_vector /= projected_vector[3]  # Normalize by w

        return projected_vector[:2]  # Return only x and y for 2D coordinates

def create_rotation_matrix_x(angle):
    cos_theta, sin_theta = np.cos(angle), np.sin(angle)
    return np.array([
        [1, 0, 0],
        [0, cos_theta, -sin_theta],
        [0, sin_theta, cos_theta]
    ])

def create_rotation_matrix_y(angle):
    cos_theta, sin_theta = np.cos(angle), np.sin(angle)
    return np.array([
        [cos_theta, 0, sin_theta],
        [0, 1, 0],
        [-sin_theta, 0, cos_theta]
    ])

def create_rotation_matrix_z(angle):
    cos_theta, sin_theta = np.cos(angle), np.sin(angle)
    return np.array([
        [cos_theta, -sin_theta, 0],
        [sin_theta, cos_theta, 0],
        [0, 0, 1]
    ])

def find_centroid_triangle(A, B, C):
    centroid = (A + B + C) / 3.0
    return centroid


import pygame
from pygame.locals import *
import numpy as np

import pygame
from pygame.locals import *
import numpy as np

class Transformer:
    def __init__(self, projector):
        self.projector = projector

    def update_rotation_matrices(self, angle_x, angle_y, angle_z):
        self.rotation_matrix_x = create_rotation_matrix_x(angle_x)
        self.rotation_matrix_y = create_rotation_matrix_y(angle_y)
        self.rotation_matrix_z = create_rotation_matrix_z(angle_z)

    def transform_vector(self, vertex):
        rotated_vertex = self.rotation_matrix_x @ vertex  # Rotate around X-axis
        rotated_vertex = self.rotation_matrix_y @ rotated_vertex  # Rotate around Y-axis
        rotated_vertex = self.rotation_matrix_z @ rotated_vertex  # Rotate around Z-axis
        translated_vertex = rotated_vertex + np.array([0, 0, 50])  # Translate in Z-axis
        projected_vertex = self.projector.project_vector(translated_vertex)
        projected_vertex += np.array([1, 1])  # Adjust for screen coordinates
        projected_vertex = (
            projected_vertex[0] * 0.5 * self.projector.width,
            projected_vertex[1] * 0.5 * self.projector.height
        )
        return projected_vertex, translated_vertex

    def transform_normal(self, normal):
        rotated_normal = self.rotation_matrix_x @ normal
        rotated_normal = self.rotation_matrix_y @ rotated_normal
        rotated_normal = self.rotation_matrix_z @ rotated_normal
        return rotated_normal

def main():
    renderer = Render()
    projector = Projector(renderer)
    transformer = Transformer(projector)

    cubes = [Cube([i, j, k]) for i in range(-1, 2) for j in range(-1, 2) for k in range(-1, 2)]

    camera = np.array([0, 0, 0])
    angle_x = 0
    angle_y = 0  
    angle_z = 0

    clock = pygame.time.Clock()

    running = True
    while running:
        running = renderer.update()

        renderer.screen.fill((255, 255, 255))  # Clear the screen
        
        transformer.update_rotation_matrices(angle_x, angle_y, angle_z)
        projected_triangles = []
        triangle_depths = []
        for cube in cubes[:]:
            for triangle in cube.triangles:
                # Compute the centroid and the normal
                centroid = find_centroid_triangle(*triangle)
                normal = triangle.get_normal()

                # Transform the normal
                transformed_normal = transformer.transform_normal(normal)
                transformed_centroid, translated_centroid = transformer.transform_vector(centroid)
                
                # Perform back-face culling
                if np.dot(transformed_normal, translated_centroid - camera) > 0:
                    projected_vertices = []
                    vertex_depths = []
                    transformed_vertices = []
                    obscured = False
                    for vertex in triangle:
                        projected_vertex, transformed_vertex = transformer.transform_vector(vertex)
                        projected_vertices.append(projected_vertex)
                        transformed_vertices.append(transformed_vertex)
                    centroid_depth = find_centroid_triangle(*transformed_vertices)[2]
                    projected_triangles.append(projected_vertices)
                    triangle_depths.append(centroid_depth)

                    # Draw the normal line
                    positioned_normal = centroid + normal
                    projected_positioned_normal, _ = transformer.transform_vector(positioned_normal)
                    renderer.draw_line(transformed_centroid, projected_positioned_normal)

        # Sort the triangles by depth 
        zipped = list(zip(projected_triangles, triangle_depths))
        sorted_zipped = sorted(zipped, key=lambda x : x[1])
        sorted_triangles = [i[0] for i in sorted_zipped]
        for triangle in sorted_triangles:
            renderer.draw_triangle(*triangle)



        # Calculate and display FPS
        fps = clock.get_fps()
        renderer.display_fps(fps)

        pygame.display.flip()

        # Update rotation angles for smooth rotation
        angle_x += 0.005  # Slow rotation around X-axis
        angle_y += 0.003  # Rotation around Y-axis
        angle_z += 0.001  # Slightly faster rotation around Z-axis

        clock.tick(60)  # Limit to 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()