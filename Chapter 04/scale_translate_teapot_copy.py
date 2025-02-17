from vectors import add,scale
from teapot import load_triangles
from draw_model import draw_model

def scale2(v):
    return scale(2.0, v)

def translate1left(v):
    return add((-1,0,0), v)

original_triangles = load_triangles()
scaled_translated_triangles = [
    [translate1left(scale2(vertex)) for vertex in triangles] 
    for triangles in original_triangles
]
draw_model(scaled_translated_triangles)