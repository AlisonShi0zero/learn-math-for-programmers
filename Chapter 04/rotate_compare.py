from vectors import to_polar, to_cartesian, scale, add
from teapot import load_triangles
from draw_model import draw_model
from math import pi

def polygon_map(transformation, polygons):
    return [
        [transformation(vertex) for vertex in triangle]
        for triangle in polygons
    ]

def rotate2d(angle, vector):
    l,a = to_polar(vector)
    return to_cartesian((l, a+angle))

def rotate_z(angle, vector):
    x,y,z = vector
    new_x, new_y = rotate2d(angle, (x,y))
    return new_x, new_y, z

def rotate_z_by(angle):
    def new_function(v):
        return rotate_z(angle,v)
    return new_function

def rotate_x(angle, vector):
    x,y,z = vector
    new_y, new_z = rotate2d(angle, (y, z))
    return x, new_y, new_z

def rotate_x_by(angle):
    def new_function(vector):
        return rotate_x(angle, vector)
    return new_function

def rotate_y(angle, vector):
    x,y,z = vector
    new_x, new_z = rotate2d(angle, (x,z))
    return new_x, y, new_z

def rotate_y_by(angle):
    def new_function(vector):
        return rotate_y(angle, vector)
    return new_function

def compose(*args):
    def new_function(input):
        state = input
        for f in reversed(args):
            state = f(state)
        return state
    return new_function

Ae1 = (1,1,1)
Ae2 = (1,0,-1)
Ae3 = (0,1,1)

def apply_A(v):
    return add(
        scale(v[0], Ae1),
        scale(v[1], Ae2),
        scale(v[2], Ae3)
    )

#print(compose(rotate_z_by(pi/2), rotate_x_by(pi/2))((1,1,1)))
#print(compose(rotate_x_by(pi/2), rotate_z_by(pi/2))((1,1,1))) 
print(rotate_y_by(pi/2)((1,1,1))) #(-1,1,1)
print(rotate_z_by(pi/2)((2,1,3)))
#print(rotate_y_by(-pi/2)((1,1,1)))
####################################################################
#### this code takes a snapshot to reproduce the exact figure 
#### shown in the book as an image saved in the "figs" directory
#### to run it, run this script with command line arg --snapshot
import sys
import camera
if '--snapshot' in sys.argv:
    camera.default_camera = camera.Camera('fig_4.11_rotate_teapot',[0])
####################################################################

#draw_model(polygon_map(compose(rotate_z_by(pi/2.), rotate_x_by(pi/2.)), load_triangles()))
#draw_model(polygon_map(compose(rotate_x_by(pi/2.), rotate_z_by(pi/2.)), load_triangles()))
#draw_model(polygon_map(rotate_y_by(pi/2.), load_triangles()))
#draw_model(polygon_map(apply_A, load_triangles()))
