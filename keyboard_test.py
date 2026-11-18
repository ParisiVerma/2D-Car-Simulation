
import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Keyboard Input Test")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

message = "Click here and press any key!"

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            message = "Key detected: " + pygame.key.name(event.key)

            print(message)

            if event.key == pygame.K_ESCAPE:
                running = False

    screen.fill((30, 30, 30))

    text = font.render(message, True, (255, 255, 255))

    screen.blit(text, (100, 280))

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()
