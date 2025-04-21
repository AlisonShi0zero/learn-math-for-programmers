from random import randint,uniform
from math import pi,sqrt,cos,sin
import vectors
import pygame
import numpy as np
import sys

bounce = True


def standard_form(v1, v2): 
    x1, y1 = v1
    x2, y2 = v2
    a = y2-y1
    b = x1-x2
    c = x1*y2-x2*y1
    return a, b, c


def intersection(u1, u2, v1, v2):
        a1, b1, c1 = standard_form(u1, u2)
        a2, b2, c2 = standard_form(v1, v2)
        m = np.array(((a1, b1), (a2, b2)))
        c = np.array((c1,c2))
        return np.linalg.solve(m,c)

def do_segment_intersect(s1, s2):
    u1, u2 = s1
    v1, v2 = s2
    d1, d2 = vectors.distance(*s1), vectors.distance(*s2)
    try:
        x,y = intersection(u1, u2, v1, v2)
        return (vectors.distance(u1, (x,y)) <= d1 and
                vectors.distance(u2, (x,y)) <= d1 and 
                vectors.distance(v1, (x,y)) <= d2 and
                vectors.distance(v2, (x,y)) <= d2)
    except np.linalg.linalg.LinAlgError:
        return False

class PolygonModel():
    def __init__(self, points):
        self.points = points
        self.rotation_angle = 0
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.angular_velocity = 0
        self.draw_center = False
    def transformed(self):
        rotated = [vectors.rotate2d(self.rotation_angle, v) for v in self.points]
        return [vectors.add((self.x, self.y), v) for v in rotated]
    
    """ def move(self, milliseconds):
        dx, dy = self.vx * milliseconds / 1000.0, self.vy * milliseconds / 1000.0
        self.x, self.y = vectors.add((self.x, self.y), (dx, dy))
        if self.x < -10:
            self.x += 20
        if self.y < -10:
            self.y += 20
        if self.x > 10:
            self.x -= 20
        if self.y > 10:
            self.y -= 20
        self.rotation_angle += self.angular_velocity * milliseconds / 1000.0 """
    
    def move(self, milliseconds, thrust_vector, gravity_sources):
        tx, ty = thrust_vector
        gx, gy = gravitational_field(gravity_sources, self.x, self.y)
        ax = tx + gx
        ay = ty + gy
        self.vx += ax * milliseconds/1000
        self.vy += ay * milliseconds/1000

        self.x += self.vx * milliseconds/1000
        self.y += self.vy * milliseconds/1000

        if bounce:
            if self.x < -10 or self.x > 10:
                self.vx = -self.vx
            if self.y < -10 or self.y > 10:
                self.vy = -self.vy
        else:
            if self.x < -10:
                self.x += 20
            if self.y < -10:
                self.y += 20
            if self.x > 10:
                self.x -= 20
            if self.y > 10:
                self.y -= 20

    
    def segments(self):
        point_counts = len(self.points)
        points = self.transformed()
        segments = [(points[i], points[(i+1) % point_counts]) for i in range(0, point_counts)]
        return segments
    def does_intersect(self, other_segment):
        for segment in self.segments():
            if do_segment_intersect(other_segment, segment):
                return True
        return False
    
    def does_collide(self, other_poly):
        for other_segment in other_poly.segments():
            if self.does_intersect(other_segment):
                return True
        return False

class Ship(PolygonModel):
    def __init__(self):
        super().__init__([(0.5, 0), (-0.25, 0.25), (-0.25, -0.25)])
    def laser_segment(self):
        dist = 20. * sqrt(2)
        x,y = self.transformed()[0]
        return (x,y), (x + dist * cos(self.rotation_angle), y + dist * sin(self.rotation_angle))

class Asteriod(PolygonModel):
    def __init__(self):
        sides = randint(5,9)
        vs = [vectors.to_cartesian((uniform(0.5,1.0), 2*pi*i/sides)) for i in range(0, sides)]
        super().__init__(vs)
        self.vx = uniform(-1,1) # uniform(-1,1)
        self.vy = uniform(-1,1) # uniform(-1,1)
        self.angular_velocity = uniform(-pi/2,pi/2)

class BlackHole(PolygonModel):
    def __init__(self, gravity):
        vs = [vectors.to_cartesian((0.5, 2*pi*i/20)) for i in range(0,20)]
        super().__init__(vs)
        self.gravity = gravity


# transform points to the pygame screen 
width, height =400, 400
def to_pixel(x,y):
    return (width/2 + width*x/20, height/2 - height*y/20)

# draw a ship and 10 asteriods  in pygame screen 
ship = Ship()

black_hole = BlackHole(0.1)
black_hole1 = BlackHole(0.1)
black_hole.x, black_hole.y = -3,4
black_hole1.x, black_hole1.y = 2,1

black_holes=[
    black_hole,
    black_hole1
]

def gravitational_field(sources, x, y):
    fields = [vectors.scale(- source.gravity, (x - source.x, y - source.y)) 
              for source in sources]
    return vectors.add(*fields)


asteriod_count = 10
asteroids = [Asteriod() for _ in range(0, asteriod_count)]

for ast in asteroids:
    ast.x = randint(-9, 9)
    ast.y = randint(-9, 9)

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

width, height = 400, 400
def draw_poly(screen, polygon_model, color=BLACK, fill=False):
    pixel_points = [to_pixel(x,y) for x,y in polygon_model.transformed()]
    if fill:
        pygame.draw.polygon(screen, color, pixel_points, 0)
    else:
        pygame.draw.lines(screen, color, True, pixel_points, 2)
    if polygon_model.draw_center:
        cx, cy = to_pixel(polygon_model.x, polygon_model.y)
        pygame.draw.circle(screen, BLACK, (int(cx), int(cy)), 4, 4)

def draw_segment(screen, v1, v2, color=RED):
    pygame.draw.aaline(screen, color, to_pixel(*v1), to_pixel(*v2), 10)

screenshot_mode = False


def main():
    pygame.init()

    screen = pygame.display.set_mode([width,height])

    pygame.display.set_caption("Asteroids!")

    done = False

    clock = pygame.time.Clock()
    # p key prints screenshot (you can ignore this variable)
    p_pressed = False
    acceleration = 3

    thrust = 3

    while not done:

        clock.tick()

        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                done=True # Flag that we are done so we exit this loop

        # UPDATE THE GAME STATE

        milliseconds = clock.get_time()
        keys = pygame.key.get_pressed()

        for ast in asteroids:
            ast.move(milliseconds, (0,0), black_holes)

        if keys[pygame.K_LEFT]:
            ship.rotation_angle += milliseconds * (2*pi / 1000)

        if keys[pygame.K_RIGHT]:
            ship.rotation_angle -= milliseconds * (2*pi / 1000)

        # asteroids hit by the laser of the ship
        laser = ship.laser_segment()

        if keys[pygame.K_p] and screenshot_mode:
            p_pressed = True
        elif p_pressed:
            pygame.image.save(screen, 'figures/asteroid_screenshot_%d.png' % milliseconds)
            p_pressed = False

        ship_thrust_vector = (0,0)

        if keys[pygame.K_UP]:
            ship_thrust_vector = vectors.to_cartesian((thrust, ship.rotation_angle))
        elif keys[pygame.K_DOWN]:
            ship_thrust_vector=vectors.to_cartesian((-thrust, ship.rotation_angle))
        
        ship.move(milliseconds, ship_thrust_vector, black_holes)

        # DRAW THE SCENE

        screen.fill(WHITE)

        if keys[pygame.K_SPACE]:
            draw_segment(screen, *laser)
        
        draw_poly(screen,ship)

        for bh in black_holes:
            draw_poly(screen, bh, fill=True)

        for asteroid in asteroids:
            if keys[pygame.K_SPACE] and asteroid.does_intersect(laser):
                asteroids.remove(asteroid)
            else:
                draw_poly(screen, asteroid, color=GREEN)
        
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    if '--screenshot' in sys.argv:
        screenshot_mode = True
    main()