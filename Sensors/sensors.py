import pygame
import math

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
LIGHTGRAY = (200, 200, 200)
DARKGRAY = (50, 50, 50)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Road dimensions
ROAD_WIDTH = 300
LANE_COUNT = 3

# Car dimensions
CAR_WIDTH = 30
CAR_HEIGHT = 50


class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = CAR_WIDTH
        self.height = CAR_HEIGHT
        self.speed = 0
        self.acceleration = 0.2
        self.max_speed = 3
        self.friction = 0.05
        self.angle = 0

    def update(self, controls):
        self.move(controls)

    def move(self, controls):
        if controls.forward:
            self.speed += self.acceleration
        if controls.reverse:
            self.speed -= self.acceleration

        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < -self.max_speed / 2:
            self.speed = -self.max_speed / 2

        if self.speed > 0:
            self.speed -= self.friction
        if self.speed < 0:
            self.speed += self.friction
        if abs(self.speed) < self.friction:
            self.speed = 0

        if self.speed != 0:
            flip = 1 if self.speed > 0 else -1
            if controls.left:
                self.angle += 0.03 * flip
            if controls.right:
                self.angle -= 0.03 * flip

        self.x -= math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, DARKGRAY, (self.x - self.width / 2, self.y - self.height / 2, self.width, self.height))


class Controls:
    def __init__(self):
        self.forward = False
        self.left = False
        self.right = False
        self.reverse = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.left = True
            elif event.key == pygame.K_RIGHT:
                self.right = True
            elif event.key == pygame.K_UP:
                self.forward = True
            elif event.key == pygame.K_DOWN:
                self.reverse = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.left = False
            elif event.key == pygame.K_RIGHT:
                self.right = False
            elif event.key == pygame.K_UP:
                self.forward = False
            elif event.key == pygame.K_DOWN:
                self.reverse = False


class Road:
    def __init__(self, x, width, lane_count=LANE_COUNT):
        self.x = x
        self.width = width
        self.lane_count = lane_count

    def get_lane_center(self, lane_index):
        lane_width = self.width / self.lane_count
        return self.x - self.width / 2 + lane_width / 2 + min(lane_index, self.lane_count - 1) * lane_width

    def draw(self, screen):
        for i in range(1, self.lane_count):
            x = self.x - self.width / 2 + i * (self.width / self.lane_count)
            pygame.draw.line(screen, WHITE, (x, 0), (x, SCREEN_HEIGHT), 2)


class Sensor:
    def __init__(self, car):
        self.car = car
        self.ray_count = 5
        self.ray_length = 150
        self.ray_spread = math.pi / 2
        self.rays = []
        self.readings = []

    def update(self, road_borders):
        self.cast_rays()
        self.readings = []
        for ray in self.rays:
            self.readings.append(self.get_reading(ray, road_borders))

    def get_reading(self, ray, road_borders):
        touches = []
        for border in road_borders:
            touch = self.get_intersection(ray[0], ray[1], border[0], border[1])
            if touch:
                touches.append(touch)

        if not touches:
            return None
        else:
            offsets = [touch["offset"] for touch in touches]
            min_offset = min(offsets)
            return next(touch for touch in touches if touch["offset"] == min_offset)

    def get_intersection(self, p1, p2, p3, p4):
        A1 = p2["y"] - p1["y"]
        B1 = p1["x"] - p2["x"]
        C1 = A1 * p1["x"] + B1 * p1["y"]

        A2 = p4["y"] - p3["y"]
        B2 = p3["x"] - p4["x"]
        C2 = A2 * p3["x"] + B2 * p3["y"]

        determinant = A1 * B2 - A2 * B1

        if determinant == 0:
            return None
        else:
            x = (B2 * C1 - B1 * C2) / determinant
            y = (A1 * C2 - A2 * C1) / determinant
            if (min(p1["x"], p2["x"]) <= x <= max(p1["x"], p2["x"]) and
                    min(p1["y"], p2["y"]) <= y <= max(p1["y"], p2["y"]) and
                    min(p3["x"], p4["x"]) <= x <= max(p3["x"], p4["x"]) and
                    min(p3["y"], p4["y"]) <= y <= max(p3["y"], p4["y"])):
                offset = math.sqrt((p1["x"] - x) ** 2 + (p1["y"] - y) ** 2)
                return {"x": x, "y": y, "offset": offset}
            else:
                return None

    def cast_rays(self):
        self.rays = []
        for i in range(self.ray_count):
            ray_angle = (self.ray_spread / 2 - i * self.ray_spread / (self.ray_count - 1)) + self.car.angle
            start = {"x": self.car.x, "y": self.car.y}
            end = {
                "x": self.car.x - math.sin(ray_angle) * self.ray_length,
                "y": self.car.y - math.cos(ray_angle) * self.ray_length
            }
            self.rays.append([start, end])

    def draw(self, screen):
        for i in range(self.ray_count):
            end = self.rays[i][1]
            if self.readings[i]:
                end = self.readings[i]

            pygame.draw.line(screen, YELLOW, (self.rays[i][0]["x"], self.rays[i][0]["y"]), (end["x"], end["y"]), 2)
            pygame.draw.line(screen, BLACK, (self.rays[i][1]["x"], self.rays[i][1]["y"]), (end["x"], end["y"]), 2)
def doPolygonsIntersect(a, b):
    polygons = [a, b]
    minA, maxA = 0, 0
    projected = []
    for i in range(len(polygons)):
        polygon = polygons[i]
        for i1 in range(len(polygon)):
            i2 = (i1 + 1) % len(polygon)
            p1 = polygon[i1]
            p2 = polygon[i2]
            normal = {'x': p2['y'] - p1['y'], 'y': p1['x'] - p2['x']} # Fixed this line
            minA, maxA = None, None
            for j in range(len(a)):
                projected = normal['x'] * a[j]['x'] + normal['y'] * a[j]['y']
                if minA is None or projected < minA:
                    minA = projected
                if maxA is None or projected > maxA:
                    maxA = projected
            minB, maxB = None, None
            for j in range(len(b)):
                projected = normal['x'] * b[j]['x'] + normal['y'] * b[j]['y']
                if minB is None or projected < minB:
                    minB = projected
                if maxB is None or projected > maxB:
                    maxB = projected
            if maxA < minB or maxB < minA:
                return False
    return True


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Self Driving Car with Sensors")
    clock = pygame.time.Clock()

    car = Car(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    controls = Controls()
    road = Road(SCREEN_WIDTH / 2, ROAD_WIDTH)
    sensor = Sensor(car)

    running = True
    while running:
        screen.fill(LIGHTGRAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            controls.handle_event(event)

        car.update(controls)
        road.draw(screen)
        car.draw(screen)

        road_borders = [
            [{"x": road.x - road.width / 2, "y": 0}, {"x": road.x - road.width / 2, "y": SCREEN_HEIGHT}],
            [{"x": road.x + road.width / 2, "y": 0}, {"x": road.x + road.width / 2, "y": SCREEN_HEIGHT}]
        ]

        sensor.update(road_borders)
        sensor.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
