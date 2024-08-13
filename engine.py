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
        width, height = 800, 600
        self.width = width
        self.height = height
        self.thickness = 1
        self.screen = self.create_window(width, height)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def draw_triangle(self, triangle):

        a_coord_screen = self.transform_to_screen_coordinates(a_coord)
        b_coord_screen = self.transform_to_screen_coordinates(b_coord)
        c_coord_screen = self.transform_to_screen_coordinates(c_coord)
        pygame.draw.line(self.screen, self.colour, a_coord_screen, b_coord_screen, self.thickness)
        pygame.draw.line(self.screen, self.colour, b_coord_screen, c_coord_screen, self.thickness)
        pygame.draw.line(self.screen, self.colour, c_coord_screen, a_coord_screen, self.thickness) 
        
class triagnel√
class Cube:
    cube_vertices = [
        np.array([[-0.5], [-0.5], [2]]),  # 0: Bottom-back-left
        np.array([[0.5], [-0.5], [2]]),   # 1: Bottom-back-right
        np.array([[0.5], [0.5], [2]]),    # 2: Top-back-right
        np.array([[-0.5], [0.5], [2]]),   # 3: Top-back-left
        np.array([[-0.5], [-0.5], [1]]),  # 4: Bottom-front-left
        np.array([[0.5], [-0.5], [1]]),   # 5: Bottom-front-right
        np.array([[0.5], [0.5], [1]]),    # 6: Top-front-right
        np.array([[-0.5], [0.5], [1]])    # 7: Top-front-left
    ]

    cube_edges = [
        (0, 1),  # Bottom-back-left to Bottom-back-right
        (1, 2),  # Bottom-back-right to Top-back-right
        (2, 3),  # Top-back-right to Top-back-left
        (3, 0),  # Top-back-left to Bottom-back-left

        (4, 5),  # Bottom-front-left to Bottom-front-right
        (5, 6),  # Bottom-front-right to Top-front-right
        (6, 7),  # Top-front-right to Top-front-left
        (7, 4),  # Top-front-left to Bottom-front-left

        (0, 4),  # Bottom-back-left to Bottom-front-left
        (1, 5),  # Bottom-back-right to Bottom-front-right
        (2, 6),  # Top-back-right to Top-front-right
        (3, 7)   # Top-back-left to Top-front-left
    ]

    def __init__(self, coord=np.zeros((3, 1))):
        self.vertices = [i + coord for i in self.cube_vertices]
        self.edges = self.cube_edges
        self.rotation = np.zeros(3)  # [x_rotation, y_rotation, z_rotation]

    def rotate(self, x_angle, y_angle, z_angle):
        self.rotation[0] += x_angle
        self.rotation[1] += y_angle
        self.rotation[2] += z_angle

    def get_rotated_vertices(self):
        rotated_vertices = []
        for vertex in self.vertices:
            rotated_vertex = rotate_vector(vertex.flatten(), *self.rotation)
            rotated_vertices.append(rotated_vertex)
        return rotated_vertices

    def render(self, renderer):
        rotated_vertices = self.get_rotated_vertices()
        projected_points = []

        # Display the projected points
        for vertex in rotated_vertices:
            projected_point = renderer.project_3D_point(vertex)
            projected_points.append(projected_point)
            renderer.display_point(projected_point)
        
        for i, j in self.edges:
            renderer.draw_line(projected_points[i], projected_points[j])

def rotate_vector(vector, x_angle, y_angle, z_angle):
    # Convert angles to radians
    x_angle = np.radians(x_angle)
    y_angle = np.radians(y_angle)
    z_angle = np.radians(z_angle)

    # Rotation matrix for X-axis
    R_x = np.array([
        [1, 0, 0],
        [0, np.cos(x_angle), -np.sin(x_angle)],
        [0, np.sin(x_angle), np.cos(x_angle)]
    ])

    # Rotation matrix for Y-axis
    R_y = np.array([
        [np.cos(y_angle), 0, np.sin(y_angle)],
        [0, 1, 0],
        [-np.sin(y_angle), 0, np.cos(y_angle)]
    ])

    # Rotation matrix for Z-axis
    R_z = np.array([
        [np.cos(z_angle), -np.sin(z_angle), 0],
        [np.sin(z_angle), np.cos(z_angle), 0],
        [0, 0, 1]
    ])

    # Combined rotation matrix
    R = R_z @ R_y @ R_x

    # Rotate the vector
    rotated_vector = R @ vector.reshape(3, 1)

    return rotated_vector

def main():
    renderer = Render()
    cube1 = Cube()  # Initialize Cube
    cube2 = Cube(np.array([1,1,0]))

    running = True
    while running:
        running = renderer.update()
        
        cube1.rotate(renderer.x_rotation, renderer.y_rotation, renderer.z_rotation)
        renderer.screen.fill((255, 255, 255))  # Clear the screen
        cube1.render(renderer)
        cube2.render(renderer)
        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()