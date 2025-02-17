from teapot import load_triangles
from draw_model import draw_model
from math import sin,cos

def get_rotation_matrix(t):
    seconds = t/1000
    return (
        (cos(seconds), 0, -sin(seconds)),
        (0,1,0),
        (sin(seconds),0,cos(seconds))
    )

draw_model(load_triangles(), get_matrix=get_rotation_matrix)
