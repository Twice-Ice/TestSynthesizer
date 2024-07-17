import pygame
from pygame import Vector2
import globals as gb

class Text:
    def __init__(self, 
                 pos : tuple|Vector2 = None,
                 staticPos : bool = False,
                 lineSpacing : int = 4,
                 color : tuple = (255, 255, 255)):
        self.text = ""
        self.pos = pos
        self.staticPos = staticPos
        self.lineSpacing = lineSpacing
        self.color = color

    def draw(self, screen):
        lines = self.text.split("\n")
        for i, line in enumerate(lines):
            renderedText = gb.FONT.render(line, True, self.color)
            screen.blit(renderedText, self.pos + Vector2(0, i * renderedText.get_height() + self.lineSpacing))

    def update(self, 
               screen,
               text : str, 
               pos : Vector2 = None):
        self.text = text
        if not self.staticPos:
            self.pos = Vector2(pos)
        self.draw(screen)