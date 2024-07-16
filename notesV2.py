import numpy as np
import pygame
import math
import globals as gb
import time
import random

pygame.init()
pygame.mixer.init()

class Note:
    def __init__(self, 
                 samplingRate : int = 44100,
                 frequency : float = 440,
                 duration : float = 1.5,
                 lineColor : tuple = (0, 0, 255),
                 circleColor : tuple = (255, 255, 255),
                 drawMode : str = "Lines"):
        
        self.samplingRate = samplingRate
        self.frequency = frequency
        self.duration = duration
        self.drawMode = drawMode
        self.lineColor = lineColor
        self.circleColor = circleColor

        self.frames = int(self.duration * self.samplingRate)
        self.sound = None
        self.wave = None
        self.startTime = None

    #SOUND
    def makeSound(self):
        """
            ## makeSound()
            Generates the sound wave of the selected note instance
        """

        self.frames = int(self.duration * self.samplingRate) # total instances to account for

        rawWave = np.cos(2 * np.pi * self.getFrequency() * np.linspace(0, self.duration, self.frames)) # raw waveform
        rawWave *= np.linspace(1, 0, self.frames) # basic linear fade

        timeFrame = np.linspace(0, self.duration, self.frames) # the time at i index for all frames
        self.wave = rawWave # sets self.wave to the actual generated wave
        self.wave = (32768 * self.wave).astype(np.int16) # maps the wave to audio min max of a 16 bit int (32768)

        stereoWave = np.asarray([self.wave, self.wave]).T # creates an array that is transposed along the y axis, self.wave is only one channel whereas this is stereo (two channels)
        self.sound = pygame.sndarray.make_sound(stereoWave.copy())

    def getFrequency(self):
        return self.frequency

    def playSound(self):
        #if the sound exists, then instead of stacking another sound into the played audio, it stops and only plays the one sound.
        if self.sound != None:
            self.sound.stop()

        #makes and plays the sound.
        self.makeSound()
        self.sound.play()
        
        #updates relevant rendering variables
        self.startTime = time.time()
        self.lastDrawnIndex = 0

    #WAVE GRAPHICS
    def drawFullWave(self, screen):
        if self.sound == None: # doesn't draw if there isn't a sound hasn't been played yet
            return

        screenSize = pygame.math.Vector2(pygame.display.get_window_size())
        offset = screenSize.y/6 # Normalizes offsets to relative screen size
        reducedWave = self.wave[::int((self.frames)/screenSize.x)] # Reduce the amount of drawn instances to the width of the screen in pixels

        normalizedWave = reducedWave / np.max(np.abs(reducedWave)) * offset # Normalizes the min and max values of the wave (visually) to that of 1x the offset scale.
        #relative positioning lists for each instance
        x = np.linspace(0, screenSize.x, len(reducedWave))
        y = screenSize.y - (offset * 3) + normalizedWave

        self.drawArray(x, y, screen)

    def drawMovingWave(self, screen):
        screenSize = pygame.math.Vector2(pygame.display.get_window_size())
        offset = screenSize.y/6 # Normalizes offsets to relative screen size

        if self.startTime == None:
            return
        
        elapsedTime = time.time() - self.startTime
        if elapsedTime > self.duration: # prevents calling from a range that isn't there and limits to only the frames within the duration.
            elapsedTime = self.duration

        # determines the relative end frame and relative start frame based on the time that has passed. It also detemines the current frame within the sequence of self.frames (not actual frames, instead wave indexes)
        currentFrame = int((elapsedTime / self.duration) * self.frames)
        relStartFrame = max(self.lastDrawnIndex, currentFrame - int(self.samplingRate * elapsedTime))
        relEndFrame = min(self.frames, currentFrame + int(self.samplingRate * elapsedTime))

        normalizedWave = self.wave[relStartFrame:relEndFrame] / np.max(np.abs(self.wave)) * offset
        x = np.linspace(0, screenSize.x, relEndFrame - relStartFrame)
        y = screenSize.y - offset + normalizedWave

        self.drawArray(x, y, screen)

        self.lastDrawnIndex = relEndFrame

    def drawArray(self, x : np.array, y : np.array, screen):
        #actual render part
        for i in range(1, len(x)):
            if self.drawMode == "Lines":
                pygame.draw.line(screen, self.lineColor, (x[i-1], y[i-1]), (x[i], y[i]))
            elif self.drawMode == "Circles":
                pygame.draw.circle(screen, self.circleColor, (x[i], y[i]), 1)
            elif self.drawMode == "Both":
                pygame.draw.line(screen, self.lineColor, (x[i-1], y[i-1]), (x[i], y[i]))
                pygame.draw.circle(screen, self.circleColor, (x[i], y[i]), 1)
            else:
                raise NameError(f"self.drawMode ({self.drawMode}) is not a valid draw mode.")

    #USER INPUT
    def userInput(self, keys):
        if gb.cooldown == 0:
            if keys[pygame.K_p]:
                gb.cooldown += gb.DEFAULT_COOLDOWN
                self.playSound()


    def update(self, keys, screen):
        self.userInput(keys)
        self.drawFullWave(screen)
        self.drawMovingWave(screen)

class StringNote(Note):
    def __init__(self,
                 samplingRate : int = 44100,
                 duration : float = 1.5,
                 length : float = 10,
                 n : float = 1,
                 tension : float = 345.23,
                 stringDensity : float = 5.1,
                 strength : float = 1,
                 harmonics : list = None,
                 lineColor : tuple = (0, 0, 255),
                 circleColor : tuple = (255, 255, 255),
                 drawMode : str = "Lines"):
        self.length = length
        self.n = n
        self.tension = tension
        self.stringDensity = stringDensity # the linear density of the string
        self.strength = strength

        if harmonics == None:
            harmonicsLen = 26
            self.harmonics = [(.5 * (random.randint(0, 100)/100)) * (abs((i-(harmonicsLen/2))/(harmonicsLen))) if i % 2 == 0 else 0 for i in range(harmonicsLen)]
			# self.harmonics = [1 * (abs((i-(len/2))/(len))) if i % 2 == 0 else 0 for i in range(len)]
			# self.harmonics = [random.randint(0, 100)/100 for i in range(3)]
			# self.harmonics = .75 * np.cos(25 * np.linspace(0, 1, 500))
        else:
            self.harmonics = harmonics

        super().__init__(
            samplingRate,
            self.getFrequency(),
            duration,
            lineColor,
            circleColor,
            drawMode
        )

    def getFrequency(self):
        return ((2*self.length/self.n))*math.sqrt(self.tension/self.stringDensity)