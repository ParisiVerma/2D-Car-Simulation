
import pygame
import math
import settings


class Track:

    def __init__(self):

        self.outer_track = pygame.Rect(60, 40, 680, 520)
        self.inner_track = pygame.Rect(170, 140, 460, 320)
        self.center_line = pygame.Rect(115, 90, 570, 420)

        self.finish_line_x = 292

    def draw(self, screen):

        # Grass background
        screen.fill((34, 115, 55))

        # Decorative grass stripes
        for y in range(0, settings.SCREEN_HEIGHT, 45):
            pygame.draw.line(
                screen,
                (39, 125, 60),
                (0, y),
                (settings.SCREEN_WIDTH, y),
                1
            )

        # Outer kerb
        pygame.draw.ellipse(
            screen,
            (220, 55, 55),
            self.outer_track.inflate(12, 12)
        )

        # Main asphalt road
        pygame.draw.ellipse(
            screen,
            (65, 68, 73),
            self.outer_track
        )

        # Inner grass
        pygame.draw.ellipse(
            screen,
            (34, 115, 55),
            self.inner_track
        )

        # Outer and inner road boundaries
        pygame.draw.ellipse(
            screen,
            settings.WHITE,
            self.outer_track,
            4
        )

        pygame.draw.ellipse(
            screen,
            settings.WHITE,
            self.inner_track,
            4
        )

        # Dashed centre line
        for angle in range(0, 360, 20):

            start_angle = math.radians(angle)
            end_angle = math.radians(angle + 10)

            pygame.draw.arc(
                screen,
                (245, 210, 65),
                self.center_line,
                start_angle,
                end_angle,
                3
            )

        # Finish line
        square_size = 12

        for row in range(8):
            for col in range(2):

                color = (
                    settings.WHITE
                    if (row + col) % 2 == 0
                    else settings.BLACK
                )

                pygame.draw.rect(
                    screen,
                    color,
                    (
                        280 + col * square_size,
                        40 + row * 12.5,
                        square_size,
                        12.5
                    )
                )

        # Track label
        label_font = pygame.font.Font(None, 24)
        label = label_font.render(
            "RACE TRACK",
            True,
            (215, 215, 215)
        )

        screen.blit(label, (340, 290))

    def is_on_road(self, x, y):

        center_x = 400
        center_y = 300

        outer_value = (
            ((x - center_x) / 340) ** 2
            +
            ((y - center_y) / 260) ** 2
        )

        inner_value = (
            ((x - center_x) / 230) ** 2
            +
            ((y - center_y) / 160) ** 2
        )

        return outer_value <= 1 and inner_value >= 1

    def crossed_finish_line(
        self,
        previous_x,
        current_x,
        car_y,
        car_speed
    ):

        crossed = (
            previous_x > self.finish_line_x + 12
            and current_x <= self.finish_line_x + 12
        )

        within_line = 40 <= car_y <= 140

        moving_forward = car_speed > 0

        return crossed and within_line and moving_forward
