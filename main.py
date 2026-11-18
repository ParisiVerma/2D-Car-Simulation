
import pygame
import sys
import math
import array
import settings

from car import Car
from track import Track
from opponent import Opponent


# ==========================================
# INITIALIZATION
# ==========================================

pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()

screen = pygame.display.set_mode(
    (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
)

pygame.display.set_caption("2D Car Race Simulation - Phase 9")

clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.Font(None, 65)
large_font = pygame.font.Font(None, 55)
font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 22)
tiny_font = pygame.font.Font(None, 18)

# Colours
DARK = (25, 30, 40)
PANEL = (20, 25, 35)
LIGHT_BLUE = (80, 170, 255)
ORANGE = (255, 160, 50)
GREEN = (60, 220, 120)
RED = (255, 75, 75)
MUTED = (180, 190, 205)
CYAN = (50, 220, 255)

game_track = Track()


# ==========================================
# SOUND SYSTEM
# ==========================================

sound_enabled = False
engine_sound = None
countdown_sound = None
collision_sound = None
finish_sound = None
nitro_sound = None

try:

    if pygame.mixer.get_init():

        sound_enabled = True

        def create_tone(frequency, duration, volume=0.3):

            sample_rate = 22050
            samples = int(sample_rate * duration)

            audio_data = array.array("h")

            for i in range(samples):

                time_value = i / sample_rate

                fade = min(
                    1,
                    i / 500,
                    (samples - i) / 1000
                )

                value = (
                    math.sin(
                        2 * math.pi * frequency * time_value
                    )
                    * volume
                    * fade
                )

                audio_data.append(int(value * 32767))

            return pygame.mixer.Sound(
                buffer=audio_data.tobytes()
            )

        engine_sound = create_tone(85, 1.0, 0.12)
        countdown_sound = create_tone(650, 0.18, 0.25)
        collision_sound = create_tone(110, 0.35, 0.4)
        finish_sound = create_tone(880, 0.65, 0.3)
        nitro_sound = create_tone(180, 0.25, 0.25)

except pygame.error:

    sound_enabled = False


def play_sound(sound):

    if sound_enabled and sound is not None:
        sound.play()


def stop_engine():

    if sound_enabled and engine_sound is not None:
        engine_sound.stop()


def update_engine():

    if not sound_enabled or engine_sound is None:
        return

    volume = min(abs(player_car.speed) / 5, 1) * 0.25

    engine_sound.set_volume(volume)

    if abs(player_car.speed) > 0.3:

        if not pygame.mixer.get_busy():
            engine_sound.play(-1)

    else:
        engine_sound.stop()


# ==========================================
# GAME VARIABLES
# ==========================================

game_state = "menu"

difficulty = "Medium"

TARGET_LAPS = 3

player_laps = 0
opponent_laps = 0

race_started = False
race_start_time = 0
elapsed_time = 0

countdown_start = 0
previous_countdown = ""

winner = ""

running = True

last_collision_time = 0
race_end_time = 0

# PHASE 9: Nitro and health
MAX_HEALTH = 100
MAX_NITRO = 100

player_health = MAX_HEALTH
nitro_energy = MAX_NITRO

NITRO_BOOST = 2.5
NITRO_DRAIN = 35
NITRO_RECHARGE = 18

COLLISION_DAMAGE = 20
COLLISION_COOLDOWN = 1000

nitro_active = False
finish_reason = ""


# ==========================================
# CREATE / RESET RACE
# ==========================================

def reset_race():

    global player_car
    global opponent_car
    global player_laps
    global opponent_laps
    global race_started
    global race_start_time
    global elapsed_time
    global winner
    global previous_x
    global previous_opponent_x
    global last_collision_time
    global race_end_time
    global player_health
    global nitro_energy
    global nitro_active
    global finish_reason

    player_car = Car(
        400,
        90,
        settings.RED
    )

    player_car.angle = 90

    opponent_car = Opponent(difficulty)

    player_laps = 0
    opponent_laps = 0

    race_started = False
    race_start_time = 0
    elapsed_time = 0

    winner = ""
    finish_reason = ""

    previous_x = player_car.x
    previous_opponent_x = opponent_car.car.x

    last_collision_time = 0
    race_end_time = 0

    player_health = MAX_HEALTH
    nitro_energy = MAX_NITRO
    nitro_active = False

    stop_engine()


reset_race()


# ==========================================
# TEXT FUNCTIONS
# ==========================================

def draw_text(text, selected_font, color, x, y):

    image = selected_font.render(
        str(text),
        True,
        color
    )

    screen.blit(image, (x, y))


def draw_centered_text(text, selected_font, color, y):

    image = selected_font.render(
        str(text),
        True,
        color
    )

    rect = image.get_rect(
        center=(settings.SCREEN_WIDTH // 2, y)
    )

    screen.blit(image, rect)


# ==========================================
# BUTTON FUNCTION
# ==========================================

def draw_button(text, rect, mouse_position):

    hovered = rect.collidepoint(mouse_position)

    color = LIGHT_BLUE if hovered else (65, 75, 95)

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=10
    )

    pygame.draw.rect(
        screen,
        settings.WHITE,
        rect,
        2,
        border_radius=10
    )

    image = font.render(
        text,
        True,
        settings.WHITE
    )

    screen.blit(
        image,
        image.get_rect(center=rect.center)
    )


# ==========================================
# PANEL FUNCTION
# ==========================================

def draw_panel(rect):

    panel_surface = pygame.Surface(
        (rect.width, rect.height),
        pygame.SRCALPHA
    )

    panel_surface.fill((15, 20, 30, 220))

    screen.blit(panel_surface, rect.topleft)

    pygame.draw.rect(
        screen,
        (100, 115, 135),
        rect,
        1,
        border_radius=10
    )


# ==========================================
# PHASE 9: HEALTH BAR
# ==========================================

def draw_health_bar():

    x = 575
    y = 105

    bar_width = 195
    bar_height = 15

    # Background
    pygame.draw.rect(
        screen,
        (65, 65, 65),
        (x, y, bar_width, bar_height),
        border_radius=5
    )

    # Health percentage
    health_width = int(
        bar_width * player_health / MAX_HEALTH
    )

    # Health colour
    if player_health > 60:
        health_color = GREEN

    elif player_health > 30:
        health_color = ORANGE

    else:
        health_color = RED

    if health_width > 0:

        pygame.draw.rect(
            screen,
            health_color,
            (x, y, health_width, bar_height),
            border_radius=5
        )

    pygame.draw.rect(
        screen,
        settings.WHITE,
        (x, y, bar_width, bar_height),
        1,
        border_radius=5
    )

    draw_text(
        f"HEALTH: {player_health}%",
        tiny_font,
        settings.WHITE,
        x,
        y - 20
    )


# ==========================================
# PHASE 9: NITRO BAR
# ==========================================

def draw_nitro_bar():

    x = 575
    y = 145

    bar_width = 195
    bar_height = 15

    # Background
    pygame.draw.rect(
        screen,
        (65, 65, 65),
        (x, y, bar_width, bar_height),
        border_radius=5
    )

    nitro_width = int(
        bar_width * nitro_energy / MAX_NITRO
    )

    if nitro_width > 0:

        pygame.draw.rect(
            screen,
            CYAN,
            (x, y, nitro_width, bar_height),
            border_radius=5
        )

    pygame.draw.rect(
        screen,
        settings.WHITE,
        (x, y, bar_width, bar_height),
        1,
        border_radius=5
    )

    draw_text(
        f"NITRO: {int(nitro_energy)}%",
        tiny_font,
        settings.WHITE,
        x,
        y - 20
    )


# ==========================================
# SPEEDOMETER
# ==========================================

def draw_speedometer(speed):

    center = (700, 70)
    radius = 43

    pygame.draw.circle(
        screen,
        PANEL,
        center,
        radius
    )

    pygame.draw.circle(
        screen,
        (130, 145, 165),
        center,
        radius,
        3
    )

    progress = min(abs(speed) / 8, 1)

    start_angle = math.radians(135)

    end_angle = (
        start_angle +
        math.radians(270) * progress
    )

    pygame.draw.arc(
        screen,
        CYAN if progress < 0.7 else ORANGE,
        (
            center[0] - radius + 7,
            center[1] - radius + 7,
            (radius - 7) * 2,
            (radius - 7) * 2
        ),
        start_angle,
        end_angle,
        5
    )

    speed_value = int(abs(speed) * 20)

    speed_image = font.render(
        str(speed_value),
        True,
        settings.WHITE
    )

    screen.blit(
        speed_image,
        speed_image.get_rect(center=center)
    )


# ==========================================
# COMPLETE HUD
# ==========================================

def draw_hud(on_road):

    # Left information panel
    draw_panel(
        pygame.Rect(10, 10, 230, 145)
    )

    draw_text(
        "RACE INFORMATION",
        small_font,
        LIGHT_BLUE,
        23,
        20
    )

    draw_text(
        f"PLAYER: {player_laps}/{TARGET_LAPS} LAPS",
        font,
        settings.WHITE,
        23,
        47
    )

    draw_text(
        f"OPPONENT: {opponent_laps}/{TARGET_LAPS}",
        small_font,
        LIGHT_BLUE,
        23,
        79
    )

    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    draw_text(
        f"TIME: {minutes:02d}:{seconds:02d}",
        small_font,
        settings.WHITE,
        23,
        108
    )

    # Right information panel
    draw_panel(
        pygame.Rect(560, 10, 230, 180)
    )

    draw_text(
        f"DIFFICULTY: {difficulty}",
        small_font,
        settings.WHITE,
        575,
        20
    )

    draw_speedometer(player_car.speed)

    draw_health_bar()
    draw_nitro_bar()

    status = "ON TRACK" if on_road else "OFF ROAD"

    status_color = GREEN if on_road else RED

    draw_text(
        status,
        tiny_font,
        status_color,
        575,
        170
    )

    # Bottom controls
    draw_panel(
        pygame.Rect(80, 550, 640, 38)
    )

    draw_centered_text(
        "ARROWS: DRIVE    SPACE: NITRO    P: PAUSE",
        tiny_font,
        settings.WHITE,
        569
    )


# ==========================================
# MENU BUTTONS
# ==========================================

easy_button = pygame.Rect(130, 310, 150, 55)
medium_button = pygame.Rect(325, 310, 150, 55)
hard_button = pygame.Rect(520, 310, 150, 55)

start_button = pygame.Rect(280, 410, 240, 60)


# ==========================================
# MAIN GAME LOOP
# ==========================================

while running:

    mouse_position = pygame.mouse.get_pos()

    # ======================================
    # EVENTS
    # ======================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                if game_state == "playing":
                    game_state = "paused"
                    stop_engine()

                elif game_state == "paused":
                    game_state = "playing"

                elif game_state == "countdown":
                    game_state = "menu"
                    stop_engine()

                elif game_state == "finished":
                    game_state = "menu"

                else:
                    running = False

            # Difficulty selection
            if game_state == "menu":

                if event.key == pygame.K_1:
                    difficulty = "Easy"

                elif event.key == pygame.K_2:
                    difficulty = "Medium"

                elif event.key == pygame.K_3:
                    difficulty = "Hard"

                elif event.key == pygame.K_RETURN:

                    reset_race()

                    countdown_start = pygame.time.get_ticks()
                    previous_countdown = ""

                    game_state = "countdown"

            # Pause and resume
            if event.key == pygame.K_p:

                if game_state == "playing":
                    game_state = "paused"
                    stop_engine()

                elif game_state == "paused":
                    game_state = "playing"

            # Restart after finishing
            if event.key == pygame.K_r:

                if game_state == "finished":

                    reset_race()

                    countdown_start = pygame.time.get_ticks()
                    previous_countdown = ""

                    game_state = "countdown"

        # Mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1 and game_state == "menu":

                if easy_button.collidepoint(event.pos):
                    difficulty = "Easy"

                elif medium_button.collidepoint(event.pos):
                    difficulty = "Medium"

                elif hard_button.collidepoint(event.pos):
                    difficulty = "Hard"

                elif start_button.collidepoint(event.pos):

                    reset_race()

                    countdown_start = pygame.time.get_ticks()
                    previous_countdown = ""

                    game_state = "countdown"

    # ======================================
    # MENU SCREEN
    # ======================================

    if game_state == "menu":

        screen.fill(DARK)

        draw_centered_text(
            "2D CAR RACING",
            title_font,
            settings.YELLOW,
            115
        )

        draw_centered_text(
            "CHOOSE YOUR DIFFICULTY",
            font,
            settings.WHITE,
            245
        )

        draw_button(
            "EASY",
            easy_button,
            mouse_position
        )

        draw_button(
            "MEDIUM",
            medium_button,
            mouse_position
        )

        draw_button(
            "HARD",
            hard_button,
            mouse_position
        )

        draw_button(
            "START RACE",
            start_button,
            mouse_position
        )

        draw_centered_text(
            f"SELECTED: {difficulty}",
            font,
            settings.YELLOW,
            500
        )

        draw_centered_text(
            "1 / 2 / 3: SELECT DIFFICULTY     ENTER: START",
            small_font,
            MUTED,
            560
        )

    # ======================================
    # COUNTDOWN SCREEN
    # ======================================

    elif game_state == "countdown":

        game_track.draw(screen)

        opponent_car.draw(screen)
        player_car.draw(screen)

        elapsed_countdown = (
            pygame.time.get_ticks() - countdown_start
        ) / 1000

        if elapsed_countdown < 1:
            countdown_text = "3"

        elif elapsed_countdown < 2:
            countdown_text = "2"

        elif elapsed_countdown < 3:
            countdown_text = "1"

        elif elapsed_countdown < 4:
            countdown_text = "GO!"

        else:

            game_state = "playing"

            race_started = True

            race_start_time = pygame.time.get_ticks()

        if game_state == "countdown":

            if countdown_text != previous_countdown:
                play_sound(countdown_sound)
                previous_countdown = countdown_text

            draw_panel(
                pygame.Rect(300, 235, 200, 120)
            )

            draw_centered_text(
                countdown_text,
                large_font,
                settings.YELLOW,
                295
            )

    # ======================================
    # PLAYING STATE
    # ======================================

    elif game_state == "playing":

        keys = pygame.key.get_pressed()

        previous_x = player_car.x
        previous_opponent_x = opponent_car.car.x

        # Update player car
        player_car.update(keys)

        # ----------------------------------
        # PHASE 9: NITRO BOOST
        # ----------------------------------

        nitro_active = (
            keys[pygame.K_SPACE]
            and nitro_energy > 0
            and player_car.speed > 0
        )

        if nitro_active:

            player_car.speed = min(
                player_car.speed + 0.08,
                player_car.max_speed + NITRO_BOOST
            )

            nitro_energy -= NITRO_DRAIN / settings.FPS

            nitro_energy = max(0, nitro_energy)

        else:

            nitro_energy += NITRO_RECHARGE / settings.FPS

            nitro_energy = min(
                MAX_NITRO,
                nitro_energy
            )

        # Play nitro sound when activated
        if nitro_active and not getattr(
            player_car, "nitro_was_active", False
        ):

            play_sound(nitro_sound)

        player_car.nitro_was_active = nitro_active

        # ----------------------------------
        # UPDATE OPPONENT
        # ----------------------------------

        opponent_car.update()

        # ----------------------------------
        # ROAD DETECTION
        # ----------------------------------

        on_road = game_track.is_on_road(
            player_car.x,
            player_car.y
        )

        # Off-road penalty
        if not on_road:

            if player_car.speed > 2:
                player_car.speed = 2

            elif player_car.speed < -1:
                player_car.speed = -1

            if player_car.speed > 0:

                player_car.speed = max(
                    0,
                    player_car.speed - 0.08
                )

            elif player_car.speed < 0:

                player_car.speed = min(
                    0,
                    player_car.speed + 0.08
                )

        # ----------------------------------
        # PLAYER LAP DETECTION
        # ----------------------------------

        if game_track.crossed_finish_line(
            previous_x,
            player_car.x,
            player_car.y,
            player_car.speed
        ):

            player_laps += 1

            print("Player lap:", player_laps)

        # ----------------------------------
        # OPPONENT LAP DETECTION
        # ----------------------------------

        if (
            previous_opponent_x < 292
            and opponent_car.car.x >= 292
            and 40 <= opponent_car.car.y <= 140
        ):

            opponent_laps += 1

            print("Opponent lap:", opponent_laps)

        # ----------------------------------
        # COLLISION DETECTION
        # ----------------------------------

        player_rect = pygame.Rect(
            player_car.x - 18,
            player_car.y - 35,
            36,
            70
        )

        opponent_rect = pygame.Rect(
            opponent_car.car.x - 18,
            opponent_car.car.y - 35,
            36,
            70
        )

        current_time = pygame.time.get_ticks()

        if player_rect.colliderect(opponent_rect):

            if (
                current_time - last_collision_time
                > COLLISION_COOLDOWN
            ):

                # Damage to player
                player_health -= COLLISION_DAMAGE

                player_health = max(
                    0,
                    player_health
                )

                # Reduce speed
                player_car.speed *= 0.3

                # Small collision push
                player_car.x -= 8

                play_sound(collision_sound)

                last_collision_time = current_time

                print(
                    "Collision! Health:",
                    player_health
                )

        # ----------------------------------
        # RACE TIMER
        # ----------------------------------

        elapsed_time = (
            pygame.time.get_ticks() - race_start_time
        ) / 1000

        # ----------------------------------
        # WINNER / GAME OVER
        # ----------------------------------

        if player_health <= 0:

            winner = "GAME OVER!"
            finish_reason = "Your car was damaged."

            game_state = "finished"

        elif player_laps >= TARGET_LAPS:

            winner = "YOU WIN!"
            finish_reason = "You completed all laps first."

            game_state = "finished"

        elif opponent_laps >= TARGET_LAPS:

            winner = "AI WINS!"
            finish_reason = "Your opponent completed all laps first."

            game_state = "finished"

        if game_state == "finished":

            race_end_time = elapsed_time

            stop_engine()

            play_sound(finish_sound)

        else:

            update_engine()

        # ----------------------------------
        # DRAW RACE
        # ----------------------------------

        game_track.draw(screen)

        opponent_car.draw(screen)
        player_car.draw(screen)

        # Nitro glow effect
        if nitro_active:

            glow = pygame.Surface(
                (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
                pygame.SRCALPHA
            )

            pygame.draw.circle(
                glow,
                (0, 200, 255, 35),
                (int(player_car.x), int(player_car.y)),
                55
            )

            screen.blit(glow, (0, 0))

        draw_hud(on_road)

        if nitro_active:

            draw_centered_text(
                "NITRO BOOST ACTIVE!",
                font,
                CYAN,
                220
            )

    # ======================================
    # PAUSED SCREEN
    # ======================================

    elif game_state == "paused":

        game_track.draw(screen)

        opponent_car.draw(screen)
        player_car.draw(screen)

        overlay = pygame.Surface(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 185))

        screen.blit(overlay, (0, 0))

        draw_panel(
            pygame.Rect(180, 195, 440, 210)
        )

        draw_centered_text(
            "GAME PAUSED",
            title_font,
            settings.YELLOW,
            250
        )

        draw_centered_text(
            "PRESS P OR ESC TO RESUME",
            font,
            settings.WHITE,
            320
        )

        draw_centered_text(
            "PRESS ESC TO RETURN TO MENU",
            small_font,
            MUTED,
            365
        )

    # ======================================
    # FINISHED SCREEN
    # ======================================

    elif game_state == "finished":

        game_track.draw(screen)

        opponent_car.draw(screen)
        player_car.draw(screen)

        overlay = pygame.Surface(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 190))

        screen.blit(overlay, (0, 0))

        draw_panel(
            pygame.Rect(145, 115, 510, 390)
        )

        if winner == "YOU WIN!":
            result_color = GREEN

        elif winner == "GAME OVER!":
            result_color = RED

        else:
            result_color = ORANGE

        draw_centered_text(
            "RACE COMPLETED",
            title_font,
            settings.WHITE,
            155
        )

        draw_centered_text(
            winner,
            large_font,
            result_color,
            225
        )

        draw_centered_text(
            finish_reason,
            small_font,
            MUTED,
            275
        )

        draw_centered_text(
            f"PLAYER LAPS: {player_laps}/{TARGET_LAPS}",
            font,
            settings.WHITE,
            330
        )

        draw_centered_text(
            f"AI LAPS: {opponent_laps}/{TARGET_LAPS}",
            font,
            LIGHT_BLUE,
            370
        )

        draw_centered_text(
            f"FINAL HEALTH: {player_health}%",
            font,
            GREEN if player_health > 30 else RED,
            410
        )

        minutes = int(race_end_time // 60)
        seconds = int(race_end_time % 60)

        draw_centered_text(
            f"FINAL TIME: {minutes:02d}:{seconds:02d}",
            font,
            settings.YELLOW,
            450
        )

        draw_centered_text(
            "R: RESTART RACE     ESC: MAIN MENU",
            small_font,
            MUTED,
            485
        )

    # ======================================
    # DISPLAY UPDATE
    # ======================================

    pygame.display.flip()

    clock.tick(settings.FPS)


# ==========================================
# QUIT
# ==========================================

stop_engine()

pygame.quit()
sys.exit()
