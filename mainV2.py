import pygame
import globals as gb

from notesV2 import Note, StringNote

pygame.init()
pygame.font.init()
pygame.mixer.init()

screen = pygame.display.set_mode((gb.SCREEN_X, gb.SCREEN_Y), pygame.RESIZABLE)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 15)

doExit = False

note = StringNote(drawMode="Lines")

while not doExit:
    delta = (clock.tick(gb.FPS) / 1000)

    gb.updateCooldown(delta)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            doExit = True

    screen.fill(gb.BG_COLOR)

    keys = pygame.key.get_pressed()

    note.update(keys, screen)

    pygame.display.flip()
pygame.quit()