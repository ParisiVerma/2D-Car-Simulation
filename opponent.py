
import math
import settings

from car import Car


class Opponent:

    def __init__(self, difficulty="Medium"):

        # Initial position on the oval track
        self.angle = 0

        # Difficulty settings
        difficulty_speeds = {
            "Easy": 0.008,
            "Medium": 0.012,
            "Hard": 0.017
        }

        self.angular_speed = difficulty_speeds.get(
            difficulty, 0.012
        )

        # Create opponent car
        self.car = Car(
            685,
            300,
            settings.BLUE
        )

    def update(self):

        # Move opponent along oval track
        self.angle += self.angular_speed

        # Track centre
        center_x = 400
        center_y = 300

        # Oval dimensions
        radius_x = 285
        radius_y = 210

        # Calculate position
        self.car.x = (
            center_x +
            radius_x * math.cos(self.angle)
        )

        self.car.y = (
            center_y +
            radius_y * math.sin(self.angle)
        )

        # Calculate direction
        dx = -radius_x * math.sin(self.angle)
        dy = radius_y * math.cos(self.angle)

        self.car.angle = math.degrees(
            math.atan2(dx, -dy)
        )

        self.car.speed = 3

    def draw(self, screen):

        self.car.draw(screen)
