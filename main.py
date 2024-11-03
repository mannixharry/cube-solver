import pygame
from pygame.locals import *
import numpy as np

class RubiksCube:
    def __init__(self, cube_string='WWWWWWWWWOOOOOOOOOGGGGGGGGGRRRRRRRRRBBBBBBBBBYYYYYYYYY'):
       
        self.cube_string = list(cube_string)


    def get_cube_string(self):
        return self.cube_string
                                    
    def __repr__(self):
        cube_string = self.cube_string
       
        return (f"               {cube_string[0:3]}\n"
                f"               {cube_string[3:6]}\n"
                f"               {cube_string[6:9]}\n"
                f"{cube_string[9:12]}{cube_string[18:21]}{cube_string[27:30]}{cube_string[36:39]}\n"
                f"{cube_string[12:15]}{cube_string[21:24]}{cube_string[30:33]}{cube_string[39:42]}\n"
                f"{cube_string[15:18]}{cube_string[24:27]}{cube_string[33:36]}{cube_string[42:45]}\n"
                f"               {cube_string[48:51]}\n"
                f"               {cube_string[45:48]}\n"
                f"               {cube_string[51:54]}\n")
    
class CubeRotations:

    def __init__(self):
        # Define the rotation tables for the edges around each face
        self.encoded_rotation_tables = {
            'U' : ['F0','F1', 'F2', 'L0', 'L1', 'L2', 'B0', 'B1', 'B2', 'R0', 'R1', 'R2'],
            'L' : ['F0', 'F3', 'F6', 'D0', 'D3', 'D6', 'B8', 'B5', 'B2', 'U0', 'U3', 'U6'],
            'F' : ['U6', 'U7', 'U8', 'R0', 'R3', 'R6', 'D2', 'D1', 'D0', 'L8', 'L5', 'L2'],
            'R' : ['F2', 'F5', 'F8', 'U2', 'U5', 'U8', 'B6', 'B3', 'B0', 'D2', 'D5', 'D8'],
            'B' : ['U0', 'U1', 'U2', 'L6', 'L3', 'L0', 'D8', 'D7', 'D6', 'R2', 'R5', 'R8'],
            'D' : ['F6', 'F7', 'F8', 'R6', 'R7', 'R8', 'B6', 'B7', 'B8', 'L6', 'L7', 'L8']
        }
        self.rotation_tables = {key: ['ULFRBD'.index(i[0])*9 + int(i[1]) for i in value] for (key, value) in self.encoded_rotation_tables.items()}
        
        #print(self.encoded_rotation_tables)
        #print(self.rotation_tables)
        
    def rotate(self, cube, face, is_clockwise=True):
        # Rotate the face itself, then rotate edges around the face 
        self._rotate_face(cube, face, is_clockwise)
        self._rotate_edges(cube, face, is_clockwise)
        
    def _rotate_face(self, cube, face, clockwise=True):
        face_start = 'ULFRBD'.index(face) * 9
        facelet_indices = [6, 3, 0, 7, 4, 1, 8, 5, 2]

        if clockwise:
            # Shift the facelet positions clockwise
            new_face = [cube.cube_string[face_start + facelet_indices[i]] for i in range(9)]
        else:
            # Shift the facelet positions anticlockwise
            new_face = [cube.cube_string[face_start + facelet_indices[8-i]] for i in range(9)]
            
        for i in range(9):
            cube.cube_string[face_start + i] = new_face[i]

    def _rotate_edges (self, cube, face, clockwise = True):
        rotation_table = self.rotation_tables[face]
        new_cube = cube.cube_string[:] #creates a new list rather than creating a reference
        if clockwise:
            for i, index in enumerate(rotation_table):
                new_cube[rotation_table[(i+3)%12]] = cube.cube_string[index]
                #print(f"{index} ==> {rotation_table[(i+3)%12]}")
        else: 
            for i, index in enumerate(rotation_table):
                new_cube[index] = cube.cube_string[rotation_table[(i+3)%12]]
                #print(f"{index} <== {rotation_table[(i+3)%12]}")
                
            
        for i in range(54):
            cube.cube_string[i] = new_cube[i]
        
class Renderer:
    def __init__(self, width=800, height=800):
        pygame.init()
        self.width = width
        self.height = height
        self.thickness = 2
        self.screen = self.create_window()
        self.font = pygame.font.SysFont('Arial', 20)
        self.colour = (0, 0, 0)
        
        self.displayed_quadrilaterals = []
        self.displayed_quadrilaterals_indices = []
        
        self.faces_clicked = []

    def detect_facelet_click(self, mouse_pos):
        
        def is_point_inside_triangle(A, B, C, P):
            v0, v1, v2 = C - A, B - A, P - A
            dot00, dot01, dot02, dot11, dot12 = np.dot(v0, v0), np.dot(v0, v1), np.dot(v0, v2), np.dot(v1, v1), np.dot(v1, v2)
            invDenom = 1 / (dot00 * dot11 - dot01 * dot01)
            u, v = (dot11 * dot02 - dot01 * dot12) * invDenom, (dot00 * dot12 - dot01 * dot02) * invDenom
            return u >= 0 and v >= 0 and u + v <= 1
    
        def is_point_inside_quadrilateral(A, B, C, D, P):
            A, B, C, D, P = np.array(A), np.array(B), np.array(C), np.array(D), np.array(P)
            return is_point_inside_triangle(A, B, C, P) or is_point_inside_triangle(A, C, D, P)
        
        for i, quad in enumerate(self.displayed_quadrilaterals): 
            if is_point_inside_quadrilateral(*quad, mouse_pos):
                self.faces_clicked.append(self.displayed_quadrilaterals_indices[i])
                print(self.faces_clicked)
                break
                
    def create_window(self):
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Basic 3D Engine')
        return screen

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.detect_facelet_click(mouse_pos)
        return True
    
    def clear_screen(self):
        self.screen.fill((255, 255, 255))
    
    def draw_line(self, a, b, colour):
        pygame.draw.line(self.screen, colour, a, b, self.thicknes*3)
    
    def draw_rectangle(self, a, b, c, d, colour):
        if colour:
            pygame.draw.polygon(self.screen, colour, [a, b, c, d])
            for start, end in [(a, b), (b, c), (c, d), (d, a)]:
                pygame.draw.line(self.screen, 'black', start, end, self.thickness*2)
        else: 
            pygame.draw.polygon(self.screen, 'black', [a,b,c,d])
        
        
    def display_fps(self, fps):
        fps_text = self.font.render(f'FPS: {int(fps)}', True, self.colour)
        self.screen.blit(fps_text, (10, 10))

class Rectangle:
    def __init__(self, a, b, c, d, piece_colour=False):
        self.a = np.array(a)
        self.b = np.array(b)
        self.c = np.array(c)
        self.d = np.array(d)
        self.vertices = [self.a, self.b, self.c, self.d]
        self.piece_colour = piece_colour 

    def __getitem__(self, index):
        return self.vertices[index]
        
    def __iter__(self):
        return iter(self.vertices)
        
    def get_normal(self):
        vector_x = self.b - self.a
        vector_y = self.c - self.a
        normal = np.cross(vector_x, vector_y)
        normal /= np.linalg.norm(normal)
        return normal
    
class Cube:
    def __init__(self, translation_vector, scale=1):
        base_rectangles = [
            Rectangle([0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0]),  # Bottom face
            Rectangle([0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]),  # Top face
            Rectangle([0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1]),  # Front face
            Rectangle([0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0]),  # Back face
            Rectangle([0, 0, 0], [0, 0, 1], [0, 1, 1], [0, 1, 0]),  # Left face
            Rectangle([1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 0, 1])   # Right face
        ]

        self.rectangles = []
        for rectangle in base_rectangles:
            self.rectangles.append(Rectangle(
                (rectangle.a + translation_vector) * scale,
                (rectangle.b + translation_vector) * scale,
                (rectangle.c + translation_vector) * scale,
                (rectangle.d + translation_vector) * scale,
                rectangle.piece_colour))
    
class Projector:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.fov = 90
        self.znear, self.zfar = 0.1, 10000
        aspect = width / height
        f = 1.0 / np.tan(np.radians(self.fov) / 2.0)
        nf = 1.0 / (self.znear - self.zfar)
        self.projection_matrix = np.array([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (self.zfar + self.znear) * nf, 2 * self.zfar * self.znear * nf],
            [0, 0, -1, 0]
        ])

    def project_vector(self, vector):
        vector_homogeneous = np.append(vector, 1)
        projected_vector = self.projection_matrix @ vector_homogeneous
        if projected_vector[3] != 0:
            projected_vector /= projected_vector[3]
        projected_vector += np.array([1, 1, 0, 0])
        return (
            projected_vector[0] * 0.5 * self.width,
            projected_vector[1] * 0.5 * self.height
        )
    
def find_centre_rectangle(A, B, C, D):
    centre = (A + B + C + D) / 4.0
    return centre

class Transformer:
    def __init__(self, projector):
        self.projector = projector
        self.rotation_matrix = np.zeros((3,3))
    
    @staticmethod
    def create_rotation_matrix(angle_x, angle_y, angle_z):

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
    
        return create_rotation_matrix_x(angle_x) @ create_rotation_matrix_y(angle_y) @ create_rotation_matrix_z(angle_z)

    def set_rotation_matrix(self, angle_x, angle_y, angle_z):
        self.rotation_matrix = self.create_rotation_matrix(angle_x, angle_y, angle_z)

    def transform_vector(self, vertex):
        rotated_vertex = self.rotation_matrix @ vertex 
        translated_vertex = rotated_vertex + np.array([0, 0, 8]) 
        return translated_vertex

class CubeManager:
    def __init__(self, cubes, cube_string= 'WWWWWWWWWOOOOOOOOOGGGGGGGGGRRRRRRRRRBBBBBBBBBYYYYYYYYY'):

        self.rubiks_cube = RubiksCube(cube_string)
        self.rotator = CubeRotations()

        self.cubes = cubes
        self.outer_rectangles = []
        self.faces = []

        self.frames = 30
        self.rotating = False
        self.rotation_to_execute = False

    def process_cube_faces(self):
        rectangles_to_sort = []

        for cube_index, cube in enumerate(self.cubes):
            for rect_index, rectangle in enumerate(cube.rectangles):
                centre = self.find_centre_rectangle(*rectangle)
                dist = max(map(abs, centre))
                rectangles_to_sort.append([rectangle, dist, cube_index * 6 + rect_index, centre])

        # Sort rectangles by distance in descending order and select the top 54
        rectangles_to_sort.sort(key=lambda x: x[1], reverse=True)
        self.outer_rectangles = rectangles_to_sort[:54]
        self.set_colours()

    @staticmethod
    def find_centre_rectangle(a, b, c, d):
        return (a + b + c + d) / 4.0
    
    def set_colours(self):

        cube_string = self.rubiks_cube.get_cube_string()
        
        colour_map = {
            'R': (255, 0, 0),       # Red
            'O': (255, 100, 0),     # Orange
            'Y': (255, 255, 0),     # Yellow
            'W': (255, 255, 255),   # White
            'G': (0, 187, 0),       # Green
            'B': (0, 0, 187),       # Blue
            'T': (0,0,0)            # Test
        }
            
        faces_dict = {
            'U' : [53, 33, 20, 50, 31, 17, 48, 30, 15],
            'D' : [35, 23, 2, 37, 24, 4, 40, 26, 7],
            'F' : [47, 29, 14, 42, 27, 9, 34, 22, 1],
            #'B' : [52, 32, 19, 45, 28, 12, 39, 25, 6],
            'B' : [19, 32, 52, 12, 28, 45, 6, 25, 39],
            'L' : [54, 51, 49, 46, 44, 43, 41, 38, 36],
            'R' : [16, 18, 21, 10, 11, 13, 3, 5, 8]
        } #Gives the index of the faces 
        
        faces = [cube_string[i:i+9] for i in range(0, len(cube_string), 9)]
        face_symbols  = ['U', 'L', 'F', 'R', 'B', 'D']
        for i, symbol in enumerate(face_symbols):
            face = []
            indices = faces_dict[symbol]
            for j, colour in enumerate(cube_string[i*9:(i+1)*9]):
                index = indices[j] - 1 
                rect_info = self.outer_rectangles[index][2]
                cube_index, rect_index = divmod(rect_info, 6)
                self.cubes[cube_index].rectangles[rect_index].piece_colour = colour_map[colour]
                
                face.append(self.cubes[cube_index])
            self.faces.append(face)
            
    def set_rotation(self, notation_input):
        if not self.rotating:
            notation_arr = ['U', 'L', 'F', 'R', 'B', 'D']
            face_symbol = notation_input[0]
            face_index = notation_arr.index(face_symbol)

            if len(notation_input) == 1:
                c = 1
                clockwise = True
            elif notation_input[1] == "\'":
                c = -1
                clockwise = False

            face = self.faces[face_index]

            if face_symbol in ['R', 'D', 'F']:
                c *= -1 

            if face_symbol in ['U', 'D']:
                angle = [0,c,0]
            if face_symbol in ['L', 'R']:
                angle = [c,0,0]
            if face_symbol in ['F', 'B']:
                angle = [0,0,c]
            angle = np.multiply(angle, np.pi/2)

            self.rotating_face, self.face_index, self.target_angle, self.clockwise, self.rotation_to_execute = face, face_index, angle, clockwise, True
            return face, face_index, np.multiply(angle, np.pi/2)

    def rotate_face(self):

        if not self.rotating:
            if self.rotation_to_execute:
                self.rotating = True
            self.current_frame = 0
        else:
            if self.current_frame == self.frames:
                #Reset rotation and apply new colours
                rotation_matrix = Transformer.create_rotation_matrix(*-self.target_angle)
                for i, cube in enumerate(self.rotating_face):
                    for j, rectangle in enumerate(cube.rectangles):
                        
                        rotated_a = rectangle.a @ rotation_matrix
                        rotated_b = rectangle.b @ rotation_matrix
                        rotated_c = rectangle.c @ rotation_matrix
                        rotated_d = rectangle.d @ rotation_matrix
                        
                        self.faces[self.face_index][i].rectangles[j].a = rotated_a
                        self.faces[self.face_index][i].rectangles[j].b = rotated_b
                        self.faces[self.face_index][i].rectangles[j].d = rotated_d
                        self.faces[self.face_index][i].rectangles[j].c = rotated_c

                        self.faces[self.face_index][i].rectangles[j].vertices = [rotated_a, rotated_b, rotated_c, rotated_d]
                
                notation_arr = ['U', 'L', 'F', 'R', 'B', 'D']
                self.rotator.rotate(self.rubiks_cube, notation_arr[self.face_index], self.clockwise)
                self.set_colours()
                print(''.join(self.rubiks_cube.cube_string))

                self.rotating = False 
                self.rotation_to_execute = False
            else:
                self.current_frame += 1 
                angle = np.multiply(self.target_angle, 1 / self.frames)
                rotation_matrix = Transformer.create_rotation_matrix(*angle)  # Adjust for specific axis
                for i, cube in enumerate(self.rotating_face):
                    for j, rectangle in enumerate(cube.rectangles):
                        
                        rotated_a = rectangle.a @ rotation_matrix
                        rotated_b = rectangle.b @ rotation_matrix
                        rotated_c = rectangle.c @ rotation_matrix
                        rotated_d = rectangle.d @ rotation_matrix
                        
                        self.faces[self.face_index][i].rectangles[j].a = rotated_a
                        self.faces[self.face_index][i].rectangles[j].b = rotated_b
                        self.faces[self.face_index][i].rectangles[j].d = rotated_d
                        self.faces[self.face_index][i].rectangles[j].c = rotated_c

                        self.faces[self.face_index][i].rectangles[j].vertices = [rotated_a, rotated_b, rotated_c, rotated_d]
                        
def main(cube_string ='WWWWWWWWWOOOOOOOOOGGGGGGGGGRRRRRRRRRBBBBBBBBBYYYYYYYYY'):

    renderer = Renderer()
    projector = Projector(renderer.width, renderer.height)
    transformer = Transformer(projector)
    
    cubes = [Cube([i/2, j/2, k/2]) for i in range(-3, 3, 2) for j in range(-3, 3, 2) for k in range(-3, 3, 2)]
    cube_manager = CubeManager(cubes, cube_string)
    cube_manager.process_cube_faces()
    
    camera = np.array([0, 0, 0])

    angle_x = 0
    angle_y = 0
    angle_z = 0

    rotation_speed = 0.05

    clock = pygame.time.Clock()
    
    running = True
    while running:
        cube_manager.rotate_face()
        running = renderer.update()
        renderer.displayed_quadrilaterals = []
        renderer.displayed_quadrilaterals_indices = []
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
        if keys[K_z]:
            angle_z -= rotation_speed  # Rotate counterclockwise around Z-axis
        if keys[K_x]:
            angle_z += rotation_speed  # Rotate clockwise around Z-axis

        face = False

        if keys[K_u]:
            face = ('U')
        if keys[K_d]:
            face = ('D')
        if keys[K_l]:
            face = ('L')
        if keys[K_r]:
            face = ('R')
        if keys[K_f]:
            face = ('F')
        if keys[K_b]:
           face = ('B')

        if keys[K_LSHIFT] and face:
            face += '\''

        if face:
            cube_manager.set_rotation(face)

        renderer.screen.fill((255, 255, 255))  # Clear the screen

        transformer.set_rotation_matrix(angle_x, angle_y, angle_z)
        rectangles_to_draw = []
        index = 0
        for cube in cubes:
            for rectangle in cube.rectangles:
                rotating = cube_manager.rotating
                if not rotating and not rectangle.piece_colour:
                    continue
                if rectangle.piece_colour:
                    index += 1
                transformed_vertices = []
                projected_vertices = []

                normal = rectangle.get_normal()
            
                positioned_normal = normal + rectangle.a
                transformed_point = transformer.transform_vector(rectangle.a)
                transformed_normal = transformer.transform_vector(positioned_normal)
                
                transformed_normal -= transformed_point   
                transformed_centroid = transformed_point

                view_vector = transformed_point - camera
                normalized_view_vector = view_vector / np.linalg.norm(view_vector)

                if np.dot(transformed_normal, normalized_view_vector) < 0:

                    for vertex in rectangle:
                        transformed_vertex = transformer.transform_vector(vertex)
                        projected_vertex = projector.project_vector(transformed_vertex)
                        projected_vertices.append(projected_vertex)
                        transformed_vertices.append(transformed_vertex)

                    centre = find_centre_rectangle(*rectangle)
                    transformed_centroid = transformer.transform_vector(centre)
                    centroid_depth = np.linalg.norm(transformed_centroid - camera)
                    

                    rectangles_to_draw.append((projected_vertices, rectangle.piece_colour, centroid_depth, index))

                    draw_normals = False
                    if draw_normals: 
                    
                        positioned_normal = transformed_centroid + transformed_normal
                        projected_positioned_normal = projector.project_vector(positioned_normal)
                        projected_transformed_centroid = projector.project_vector(transformed_centroid)

                        renderer.draw_line(projected_transformed_centroid, projected_positioned_normal, 'aqua')
                
        # Sort rectangles by piece_colour and depth
        rectangles_to_draw.sort(key=lambda x: (isinstance(x[1], tuple), -x[2]))

        #Sort rectangles by depth
        #rectangles_to_draw.sort(key=lambda x: x[2])
        
        for count, (rectangle, piece_colour, _, index) in enumerate(rectangles_to_draw):
            t = count / len(rectangles_to_draw)
            colour = piece_colour
            renderer.draw_rectangle(*rectangle, colour)
            renderer.displayed_quadrilaterals.append([*rectangle])
            renderer.displayed_quadrilaterals_indices.append(index)
            
        #print(count+1) # number of rectangles rendered

        fps = clock.get_fps()
        renderer.display_fps(fps)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

