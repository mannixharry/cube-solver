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
        self.thickness = 2
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
    
    def draw_line(self, a, b, colour):
        pygame.draw.line(self.screen, colour, a, b, self.thickness)

    def draw_triangle(self, a, b, c, colour):
        # Draw filled triangle
        if colour:
            pygame.draw.polygon(self.screen, colour, [a, b, c])
        # Draw the edges
        pygame.draw.line(self.screen, (0, 0, 0), a, b, self.thickness)
        pygame.draw.line(self.screen, (0, 0, 0), b, c, self.thickness)
        pygame.draw.line(self.screen, (0, 0, 0), c, a, self.thickness)

    def display_fps(self, fps):
        fps_text = self.font.render(f'FPS: {int(fps)}', True, self.colour)
        self.screen.blit(fps_text, (10, 10))  # Display at the top-left corner

class Triangle:
    def __init__(self, a, b, c, layer=False):
        self.a = np.array(a)
        self.b = np.array(b)
        self.c = np.array(c)
        self.vertices = [self.a, self.b, self.c]
        self.layer = layer 

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
            Triangle([1, 0, 1], [0, 0, 0], [1, 0, 0])
        ]

        # Apply translation and scaling to each triangle's vertices
        self.triangles = []
        for triangle in base_triangles:
            new_a = (triangle.a + translation_vector) * scale
            new_b = (triangle.b + translation_vector) * scale
            new_c = (triangle.c + translation_vector) * scale
            self.triangles.append(Triangle(new_a, new_b, new_c, triangle.layer))
    
class Projector:
    def __init__(self, renderer):
        self.width, self.height = renderer.width, renderer.height
        self.fov = 90
        self.znear, self.zfar = 0.1, 10000

        # Aspect ratio
        aspect = self.width / self.height
        # Calculate projection matrix components
        f = 1.0 / np.tan(np.radians(self.fov) / 2.0)
        nf = 1.0 / (self.znear - self.zfar)
        
        self.projection_matrix = np.array([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (self.zfar + self.znear) * nf, 2 * self.zfar * self.znear * nf],
            [0, 0, -1, 0]
        ])


    def project_vector(self, vector):
        vector_homogeneous = np.append(vector, 1)  # Convert to 4D
        projected_vector = self.projection_matrix @ vector_homogeneous

        if projected_vector[3] != 0:
            projected_vector /= projected_vector[3]  # Normalize by w

        projected_vector += np.array([1, 1, 0, 0])  # Adjust for screen coordinates
        projected_vector = (
            projected_vector[0] * 0.5 * self.width,
            projected_vector[1] * 0.5 * self.height
        )

        return projected_vector # Return only x and y for 2D coordinates

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
        translated_vertex = rotated_vertex + np.array([0, 0, 8])  # Translate in Z-axis
        projected_vertex = self.projector.project_vector(translated_vertex)
        return projected_vertex, translated_vertex

    def transform_normal(self, normal):
        rotated_normal = self.rotation_matrix_x @ normal
        rotated_normal = self.rotation_matrix_y @ rotated_normal
        rotated_normal = self.rotation_matrix_z @ rotated_normal
    
        return rotated_normal
    
# Function to interpolate between two colours
def interpolate_colour(start_colour, end_colour, t):
    r = int(start_colour[0] + (end_colour[0] - start_colour[0]) * t)
    g = int(start_colour[1] + (end_colour[1] - start_colour[1]) * t)
    b = int(start_colour[2] + (end_colour[2] - start_colour[2]) * t)
    return (r, g, b)


def main():
    rotating = True
    renderer = Render()
    projector = Projector(renderer)
    transformer = Transformer(projector)

    cubes = [Cube([i/2, j/2, k/2]) for i in range(-3, 3, 2) for j in range(-3, 3, 2) for k in range(-3, 3, 2)]

    #Work out which triangles are on the outer surface of the cube 
    triangles_to_sort = []
    distances = []
    index = 0 
    for cube in cubes:
        for triangle in cube.triangles: 
            centroid = find_centroid_triangle(*triangle)
            dist = max([*map(abs, centroid)])
            distances.append(dist)
            triangles_to_sort.append([Triangle, dist, index])
            index += 1
    triangles_to_sort.sort(key=lambda x : x[1], reverse=True)

    for i in range(108): # Number of triangle on outer surface of the cube 
        index = triangles_to_sort[i][2] 
        cubes[index//12].triangles[index%12].layer = True

    camera = np.array([0, 0, 0])
    angle_x = 0
    angle_y = 0
    angle_z = 0

    rotation_speed = 0.05

    clock = pygame.time.Clock()

    running = True
    while running:
        running = renderer.update()

        # Handle key presses for rotation
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            angle_y -= rotation_speed  # Rotate left around Y-axis
        if keys[K_RIGHT]:
            angle_y += rotation_speed  # Rotate right around Y-axis
        if keys[K_UP]:
            angle_x -= rotation_speed  # Rotate up around X-axis
        if keys[K_DOWN]:
            angle_x += rotation_speed  # Rotate down around X-axis
        if keys[K_a]:
            angle_z -= rotation_speed  # Rotate counterclockwise around Z-axis
        if keys[K_d]:
            angle_z += rotation_speed  # Rotate clockwise around Z-axis

        renderer.screen.fill((255, 255, 255))  # Clear the screen

        transformer.update_rotation_matrices(angle_x, angle_y, angle_z)
        triangles_to_draw = []

        for cube in cubes[:]:
            for triangle in cube.triangles:
                if not rotating and not triangle.layer:
                    continue
                transformed_vertices = []
                projected_vertices = []

                '''
                for vertex in triangle:
                    projected_vertex, transformed_vertex = transformer.transform_vector(vertex)
                    projected_vertices.append(projected_vertex)
                    transformed_vertices.append(transformed_vertex)

                transformed_triangle = Triangle(*transformed_vertices)
                transformed_normal = transformed_triangle.get_normal()

                transformed_centroid = find_centroid_triangle(*transformed_vertices)
                '''

                # calculate the normal
                # transform normal + a point 
                # subtract the transformed point from the normal to get the new normal
                # calculate teh view vector and take the dot product

                normal = triangle.get_normal()
            
                positioned_normal = normal + triangle.a
                _, transformed_point = transformer.transform_vector(triangle.a)
                _, transformed_normal = transformer.transform_vector(positioned_normal)
                
                transformed_normal -= transformed_point   
                transformed_centroid = transformed_point

                view_vector = transformed_point - camera
                normalized_view_vector = view_vector / np.linalg.norm(view_vector)

                if np.dot(transformed_normal, normalized_view_vector) < 0:

                    for vertex in triangle:
                        projected_vertex, transformed_vertex = transformer.transform_vector(vertex)
                        projected_vertices.append(projected_vertex)
                        transformed_vertices.append(transformed_vertex)

                    centroid = find_centroid_triangle(*triangle)
                    _, transformed_centroid = transformer.transform_vector(centroid)
                    centroid_depth = np.linalg.norm(transformed_centroid - camera)

                    triangles_to_draw.append((projected_vertices, triangle.layer, centroid_depth))

                    draw_normals = False
                    if draw_normals: 
                    
                        positioned_normal = transformed_centroid + transformed_normal
                        projected_positioned_normal = projector.project_vector(positioned_normal)
                        projected_transformed_centroid = projector.project_vector(transformed_centroid)

                        renderer.draw_line(projected_transformed_centroid, projected_positioned_normal, 'aqua')
                    

        # Sort triangles by layer and depth
        triangles_to_draw.sort(key=lambda x: (x[1], -x[2]))

        #Sort triangles by depth
        #triangles_to_draw.sort(key=lambda x: x[2])
        count = 0
        for count, (triangle, layer, _) in enumerate(triangles_to_draw):
            t = count / len(triangles_to_draw)
            colour = interpolate_colour((0, 0, 255), (255, 0, 0), t)
            renderer.draw_triangle(*triangle, colour)
        print(count+1) # number of triangles rendered

        fps = clock.get_fps()
        renderer.display_fps(fps)

        pygame.display.flip()

        clock.tick(120)

    pygame.quit()

if __name__ == "__main__":
    main()