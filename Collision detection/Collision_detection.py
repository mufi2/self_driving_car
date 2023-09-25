import pygame
import math

# utils.py
def lerp(A, B, t):
    return A + (B - A) * t

def get_intersection(A, B, C, D):
    tTop = (D['x'] - C['x']) * (A['y'] - C['y']) - (D['y'] - C['y']) * (A['x'] - C['x'])
    uTop = (C['y'] - A['y']) * (A['x'] - B['x']) - (C['x'] - A['x']) * (A['y'] - B['y'])
    bottom = (D['y'] - C['y']) * (B['x'] - A['x']) - (D['x'] - C['x']) * (B['y'] - A['y'])
    
    if bottom != 0:
        t = tTop / bottom
        u = uTop / bottom
        if 0 <= t <= 1 and 0 <= u <= 1:
            return {
                'x': lerp(A['x'], B['x'], t),
                'y': lerp(A['y'], B['y'], t),
                'offset': t
            }
    return None

def polys_intersect(poly1, poly2):
    for i in range(len(poly1)):
        for j in range(len(poly2)):
            touch = get_intersection(
                poly1[i],
                poly1[(i + 1) % len(poly1)],
                poly2[j],
                poly2[(j + 1) % len(poly2)]
            )
            if touch:
                return True
    return False

# sensor.py
class Sensor:
    def __init__(self, car):
        self.car = car
        self.ray_count = 5
        self.ray_length = 150
        self.ray_spread = math.pi / 2

        self.rays = []
        self.readings = []

    def update(self, road_borders):
        self._cast_rays()
        self.readings = []
        for i in range(len(self.rays)):
            self.readings.append(
                self._get_reading(self.rays[i], road_borders)
            )

    def _get_reading(self, ray, road_borders):
        touches = []

        for i in range(len(road_borders)):
            touch = get_intersection(
                ray[0],
                ray[1],
                road_borders[i][0],
                road_borders[i][1]
            )
            if touch:
                touches.append(touch)

        if not touches:
            return None
        else:
            offsets = [e['offset'] for e in touches]
            min_offset = min(offsets)
            return next(e for e in touches if e['offset'] == min_offset)

    def _cast_rays(self):
        self.rays = []
        for i in range(self.ray_count):
            ray_angle = lerp(
                self.ray_spread / 2,
                -self.ray_spread / 2,
                0.5 if self.ray_count == 1 else i / (self.ray_count - 1)
            ) + self.car.angle

            start = {'x': self.car.x, 'y': self.car.y}
            end = {
                'x': self.car.x - math.sin(ray_angle) * self.ray_length,
                'y': self.car.y - math.cos(ray_angle) * self.ray_length
            }
            self.rays.append([start, end])

    def draw(self, screen):
        for i in range(self.ray_count):
            end = self.rays[i][1]
            if self.readings[i]:
                end = self.readings[i]

            pygame.draw.line(screen, (255, 255, 0), (self.rays[i][0]['x'], self.rays[i][0]['y']), (end['x'], end['y']), 2)
            pygame.draw.line(screen, (0, 0, 0), (self.rays[i][1]['x'], self.rays[i][1]['y']), (end['x'], end['y']), 2)

# controls.py
class Controls:
    def __init__(self):
        self.forward = False
        self.left = False
        self.right = False
        self.reverse = False

        self._add_keyboard_listeners()

    def _add_keyboard_listeners(self):
      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.forward = True
            elif event.key == pygame.K_DOWN:
                self.reverse = True
            elif event.key == pygame.K_LEFT:
                self.left = True
            elif event.key == pygame.K_RIGHT:
                self.right = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                self.forward = False
            elif event.key == pygame.K_DOWN:
                self.reverse = False
            elif event.key == pygame.K_LEFT:
                self.left = False
            elif event.key == pygame.K_RIGHT:
                self.right = False


# car.py
class Car:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.speed = 0
        self.acceleration = 0.2
        self.max_speed = 3
        self.friction = 0.05
        self.angle = 0
        self.damaged = False

        self.sensor = Sensor(self)
        self.controls = Controls()

    def update(self, road_borders):
        if not self.damaged:
            self._move()
            self.polygon = self._create_polygon()
            self.damaged = self._assess_damage(road_borders)
        self.sensor.update(road_borders)

    def _assess_damage(self, road_borders):
        for border in road_borders:
            if polys_intersect(self.polygon, border):
                return True
        return False

    def _move(self):
        if self.controls.forward:
            self.speed += self.acceleration
        if self.controls.reverse:
            self.speed -= self.acceleration
        if self.controls.left:
            self.angle -= 0.1
        if self.controls.right:
            self.angle += 0.1

        self.speed *= (1 - self.friction)
        self.speed = max(min(self.speed, self.max_speed), -self.max_speed)

        self.x += self.speed * math.sin(self.angle)
        self.y += self.speed * math.cos(self.angle)

    def _create_polygon(self):
        half_width = self.width / 2
        half_height = self.height / 2

        return [
            {'x': self.x - half_width, 'y': self.y - half_height},
            {'x': self.x + half_width, 'y': self.y - half_height},
            {'x': self.x + half_width, 'y': self.y + half_height},
            {'x': self.x - half_width, 'y': self.y + half_height}
        ]

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0) if self.damaged else (0, 255, 0), (self.x, self.y, self.width, self.height))
        self.sensor.draw(screen)

# Main pygame loop
pygame.init()

# Set up display, clock, etc.
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Car Simulation")
clock = pygame.time.Clock()

# Initialize the road and car
road = Road(400, 540)
car = Car(road.getLaneCenter(1), 100, 30, 50)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Handle other events like KEYDOWN, KEYUP, etc.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                car.controls.left = True
            elif event.key == pygame.K_RIGHT:
                car.controls.right = True
            elif event.key == pygame.K_UP:
                car.controls.forward = True
            elif event.key == pygame.K_DOWN:
                car.controls.reverse = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                car.controls.left = False
            elif event.key == pygame.K_RIGHT:
                car.controls.right = False
            elif event.key == pygame.K_UP:
                car.controls.forward = False
            elif event.key == pygame.K_DOWN:
                car.controls.reverse = False

    # Update game state
    car.update(road.borders)

    # Draw on the screen
    screen.fill((200, 200, 200))  # Fill background color
    road.draw(screen)
    car.draw(screen)

    pygame.display.flip()
    clock.tick(60)  # Limit the frame rate to 60 FPS

pygame.quit()

