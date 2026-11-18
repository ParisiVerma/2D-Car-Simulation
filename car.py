
import pygame
import math
import settings


class Car:

    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)

        self.color = color
        self.width = 36
        self.height = 70

        self.angle = 0
        self.speed = 0

        self.acceleration = 0.12
        self.max_speed = 5
        self.friction = 0.04
        self.steering_speed = 3

    def update(self, keys):

        if keys[pygame.K_UP]:
            self.speed += self.acceleration

        if keys[pygame.K_DOWN]:
            self.speed -= self.acceleration

        self.speed = max(-2, min(self.speed, self.max_speed))

        if not keys[pygame.K_UP] and not keys[pygame.K_DOWN]:

            if self.speed > 0:
                self.speed = max(0, self.speed - self.friction)

            elif self.speed < 0:
                self.speed = min(0, self.speed + self.friction)

        if abs(self.speed) > 0.1:

            steering = self.steering_speed * min(
                abs(self.speed) / 2, 1
            )

            if keys[pygame.K_LEFT]:
                self.angle -= steering

            if keys[pygame.K_RIGHT]:
                self.angle += steering

        radians = math.radians(self.angle)

        self.x += self.speed * math.sin(radians)
        self.y -= self.speed * math.cos(radians)

    def draw(self, screen):

        car_surface = pygame.Surface((60, 90), pygame.SRCALPHA)

        # Soft shadow
        pygame.draw.ellipse(
            car_surface,
            (0, 0, 0, 90),
            (11, 15, 42, 68)
        )

        # Wheels
        wheel_positions = [
            (8, 19), (45, 19),
            (8, 53), (45, 53)
        ]

        for wx, wy in wheel_positions:
            pygame.draw.rect(
                car_surface,
                (20, 20, 20),
                (wx, wy, 8, 17),
                border_radius=3
            )

        # Main body
        body_points = [
            (30, 8),
            (45, 22),
            (49, 65),
            (42, 81),
            (18, 81),
            (11, 65),
            (15, 22)
        ]

        pygame.draw.polygon(
            car_surface,
            self.color,
            body_points
        )

        # Body outline
        pygame.draw.polygon(
            car_surface,
            (230, 230, 230),
            body_points,
            2
        )

        # Front windshield
        pygame.draw.polygon(
            car_surface,
            (25, 45, 65),
            [(18, 26), (42, 26), (44, 43), (16, 43)]
        )

        # Rear windshield
        pygame.draw.polygon(
            car_surface,
            (25, 45, 65),
            [(18, 55), (42, 55), (40, 68), (20, 68)]
        )

        # Headlights
        pygame.draw.rect(
            car_surface,
            (255, 245, 150),
            (17, 11, 7, 5),
            border_radius=2
        )

        pygame.draw.rect(
            car_surface,
            (255, 245, 150),
            (36, 11, 7, 5),
            border_radius=2
        )

        # Rear lights
        pygame.draw.rect(
            car_surface,
            (255, 40, 40),
            (16, 76, 8, 4)
        )

        pygame.draw.rect(
            car_surface,
            (255, 40, 40),
            (36, 76, 8, 4)
        )

        rotated_car = pygame.transform.rotate(
            car_surface,
            -self.angle
        )

        car_rect = rotated_car.get_rect(
            center=(int(self.x), int(self.y))
        )

        screen.blit(rotated_car, car_rect)
