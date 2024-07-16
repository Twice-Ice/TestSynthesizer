import pygame
import numpy as np
import os
import math
import globals as gb
from notes import note, stringNote

pygame.init()
pygame.font.init()
pygame.mixer.init()

screen = pygame.display.set_mode((gb.SCREEN_X, gb.SCREEN_Y), pygame.RESIZABLE)
clock = pygame.time.Clock()

doExit = False

playedNote = None

def redoNote():
    return stringNote(harmonics=[0,.5,1], strength=.1)

playedNote = redoNote()

ticker = 0

controllerState = "Tension"

font = pygame.font.SysFont("Arial", 15)

# pygame.display.toggle_fullscreen()

while not doExit:
    delta = (clock.tick(gb.FPS) / 1000)

    if gb.cooldown > 0:
        gb.cooldown -= delta
    elif gb.cooldown < 0:
        gb.cooldown = 0

    ticker += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            doExit = True
    screen.fill(gb.BG_COLOR)

    keys = pygame.key.get_pressed()

    controllerDict = {
        "Length" : playedNote.length/40,
        "N" : .1,
        "Tension" : playedNote.tension/20,
        "String Density" : playedNote.linearDensity/50,
        "Duration" : playedNote.duration/10,
        "Force" : .1
    }

    if gb.cooldown == 0:
        if keys[pygame.K_p]:
            gb.cooldown += gb.DEFAULT_COOLDOWN
            playedNote.playSound()
        
        elif keys[pygame.K_l]:
            controllerState = "Length"
        elif keys[pygame.K_n]:
            controllerState = "N"
        elif keys[pygame.K_t]:
            controllerState = "Tension"
        elif keys[pygame.K_s]:
            controllerState = "String Density"
        elif keys[pygame.K_d]:
            controllerState = "Duration"
        elif keys[pygame.K_f]:
            controllerState = "Force"

        if keys[pygame.K_r]:
            gb.cooldown += gb.DEFAULT_COOLDOWN
            if playedNote.sound != None:
                playedNote.sound.stop()
            playedNote = redoNote()

        if keys[pygame.K_e]:
            gb.cooldown += gb.DEFAULT_COOLDOWN
            playedNote.sound.stop()
        
        if keys[pygame.K_UP]:
            gb.cooldown += gb.DEFAULT_COOLDOWN

            match controllerState:
                case "Length":
                    playedNote.length += controllerDict[controllerState]
                    pass
                case "N":
                    playedNote.n += controllerDict[controllerState]
                case "Tension":
                    playedNote.tension += controllerDict[controllerState]
                case "String Density":
                    playedNote.linearDensity += controllerDict[controllerState]
                case "Duration":
                    playedNote.duration += controllerDict[controllerState]
                    if playedNote.sound != None:
                        playedNote.sound.stop()
                case "Force":
                    playedNote.strength += controllerDict[controllerState]
        if keys[pygame.K_DOWN]:
            gb.cooldown += gb.DEFAULT_COOLDOWN

            match controllerState:
                case "Length":
                    playedNote.length -= controllerDict[controllerState]
                case "N":
                    playedNote.n -= controllerDict[controllerState]
                case "Tension":
                    playedNote.tension -= controllerDict[controllerState]
                case "String Density":
                    playedNote.linearDensity -= controllerDict[controllerState]
                case "Duration":
                    playedNote.duration -= controllerDict[controllerState]
                    if playedNote.sound != None:
                        playedNote.sound.stop()
                case "Force":
                    playedNote.strength -= controllerDict[controllerState]
    
    playedNote.drawFullWave(screen)
    playedNote.drawMovingWave(screen)

    lines = f"{playedNote.printStats()}\nCURRENT CONTROL: {controllerState}".split("\n")
    for i, line in enumerate(lines):
        textSurface = font.render(line, True, (255, 255, 255))
        screen.blit(textSurface, (10, 10 + i * (textSurface.get_height() + 4)))
    
    pygame.display.flip()
pygame.quit()