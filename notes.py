import numpy as np
import pygame
import math
import globals as gb
import time
import random
from text import Text

#Mwroc Camp

pygame.init()
pygame.mixer.init()

class Note:
    def __init__(self, 
                 samplingRate : int = 44100,
                 frequency : float = 440,
                 duration : float = 1.5,
                 lineStartColor : tuple = (50, 50, 255),
                 lineEndColor : tuple = (50, 255, 0),
                 circleColor : tuple = (255, 255, 255),
                 drawMode : str = "Lines"):
        
        self.samplingRate = samplingRate
        self.frequency = frequency
        self.duration = duration
        self.lineStartColor = lineStartColor
        self.lineEndColor = lineEndColor
        self.circleColor = circleColor
        self.drawMode = drawMode

        self.frames = int(self.duration * self.samplingRate)
        self.sound = None
        self.wave = None
        self.startTime = None
        self.text = Text((10, 10), True)
        self.controllerState = "Weight"

        self.stateSettings = [
            ["Frequency", pygame.K_f, 1.1, "*"],
            ["Duration", pygame.K_d, 1.1, "*"]
        ]

        self.drawModes = [
            "Lines",
            "Circles",
            "Both"
        ]

        self.baseValues = None
        self.setBaseValues()

    #MISC
    def setBaseValues(self):
        self.baseValues = [[self.stateSettings[i][0], getattr(self, gb.cammelCase(self.stateSettings[i][0]))] for i in range(len(self.stateSettings))]

    #SOUND
    def makeSound(self):
        """
            ## makeSound()
            Generates the sound wave of the selected note instance
        """

        self.frames = int(self.duration * self.samplingRate) # total instances to account for

        rawWave = np.cos(2 * np.pi * self.getFrequency() * np.linspace(0, self.duration, self.frames)) # raw waveform
        rawWave *= np.linspace(1, 0, self.frames) # basic linear fade

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
    def drawFullWave(self, screen : pygame.display):
        """
            ## drawFullWave
            draws the sound wave being played all at once to the screen. The waveform's resolution is durastically reduced for performace reasons.

            ### screen : pygame.display
            the screen to draw to
        """
        if self.sound == None: # doesn't draw if there isn't a sound hasn't been played yet
            return

        screenSize = pygame.math.Vector2(pygame.display.get_window_size()) # for scaling purposes
        offset = screenSize.y/6 # Normalizes offsets to relative screen size
        reducedWave = self.wave[::int(math.ceil(self.frames/screenSize.x))] # Reduce the amount of drawn instances to the width of the screen in pixels

        normalizedWave = reducedWave / np.max(np.abs(reducedWave)) * offset # Normalizes the min and max values of the wave (visually) to that of 1x the offset scale.
        #relative positioning lists for each instance
        x = np.linspace(0, screenSize.x, len(reducedWave))
        y = screenSize.y - (offset * 3) + normalizedWave

        self.drawArray(x, y, screen)

    def drawMovingWave(self, screen : pygame.display):
        """
            ## drawMovingWave
            draws the sound wave being played for each chunk of sound that was played over the time that it took to render the last frame.

            ### screen : pygame.display
            the screen to draw to
        """
        screenSize = pygame.math.Vector2(pygame.display.get_window_size()) #for scaling purposes
        offset = screenSize.y/6 # Normalizes offsets to relative screen size

        #if the audio isn't being played then it shouldn't render.
        if self.startTime == None:
            return
        
        elapsedTime = time.time() - self.startTime
        if elapsedTime > self.duration: # prevents calling from a range that isn't there and limits to only the frames within the duration.
            elapsedTime = self.duration

        # determines the relative end frame and relative start frame based on the time that has passed. It also detemines the current frame within the sequence of self.frames (not actual frames, instead wave indexes)
        currentFrame = int((elapsedTime / self.duration) * self.frames)
        relStartFrame = max(self.lastDrawnIndex, currentFrame - int(self.samplingRate * elapsedTime))
        relEndFrame = min(self.frames, currentFrame + int(self.samplingRate * elapsedTime))

        if relEndFrame - relStartFrame <= 0: #this equation would return a negative value occasionally when editing values, so it returns if that is the case.
            return

        #normalizes the wave size to that -1, 1. Then multiplies by the offset value to be evenly spaced.
        normalizedWave = self.wave[relStartFrame:relEndFrame] / np.max(np.abs(self.wave)) * offset
        #gets the x and y lists for rendering
        x = np.linspace(0, screenSize.x, relEndFrame - relStartFrame)
        y = screenSize.y - offset + normalizedWave

        self.drawArray(x, y, screen, startPercent=relStartFrame/self.frames, endPercent=relEndFrame/self.frames)

        #updates the last drawn index
        self.lastDrawnIndex = relEndFrame

    def drawArray(self, x : np.array, y : np.array, screen, startPercent : float = 0, endPercent : float = 1):
        """
            ## drawArray
            renders an array of x and y positions to the screen, the way they are rendered depending on self.drawMode.

            ### x : np.array
            the x positions
            
            ### y : np.array
            the y positions

            ### screen : pygame.display
            screen to draw to

            ### startPercent : float
            staring percent to use when rendering the line colors
            defaults to 0

            ### endPercent : float
            ending percent to use when rendering the line colors
            defaults to 1
        """
        length = len(x)
        for i in range(1, length):
            percent = startPercent + ((endPercent - startPercent) * i/length)
            color = gb.capColor(((self.lineEndColor[0] - self.lineStartColor[0]) * percent + self.lineStartColor[0], (self.lineEndColor[1] - self.lineStartColor[1]) * percent + self.lineStartColor[1], (self.lineEndColor[2] - self.lineStartColor[2]) * percent + self.lineStartColor[2]))
            if self.drawMode == "Lines":
                pygame.draw.line(screen, color, (x[i-1], y[i-1]), (x[i], y[i]))
            elif self.drawMode == "Circles":
                pygame.draw.circle(screen, self.circleColor, (x[i], y[i]), 1)
            elif self.drawMode == "Both":
                pygame.draw.line(screen, color, (x[i-1], y[i-1]), (x[i], y[i]))
                pygame.draw.circle(screen, self.circleColor, (x[i], y[i]), 1)
            else:
                raise NameError(f"self.drawMode ({self.drawMode}) is not a valid draw mode.")

    #USER INPUT
    def userInput(self, keys):
        if gb.cooldown == 0:
            if keys[pygame.K_p]: #play sound
                self.playButton()

            if keys[pygame.K_r]: #reset
                self.resetButton()

            drawIndex = self.drawModes.index(self.drawMode)
            if keys[pygame.K_RIGHT]:
                gb.cooldown += gb.DEFAULT_COOLDOWN
                self.drawMode = self.drawModes[drawIndex + 1 if drawIndex + 1 < len(self.drawModes) else 0]
            if keys[pygame.K_LEFT]:
                gb.cooldown += gb.DEFAULT_COOLDOWN
                self.drawMode = self.drawModes[drawIndex - 1 if drawIndex - 1 >= 0 else len(self.drawModes) - 1]

            for instance in self.stateSettings:
                name = instance[0]
                convertedName = gb.cammelCase(name) #cammelCase version of the name string for use with setattr() and getattr()

                key = instance[1]
                valueChange = instance[2]
                operation = instance[3]

                if keys[key]: #if the pressed key is in self.stateSettings then the controllerState is set to the state associated with that key.
                    self.controllerState = name
                
                if name == self.controllerState:
                    if keys[pygame.K_UP]:
                        gb.cooldown += gb.DEFAULT_COOLDOWN
                        # Sets the attribute {convertedName} which is just {name} but formated to "cammelCasing" and it's given the value of itself + or * the value change. 
                        # These are determined in self.stateSettings in the init.
                        setattr(self, convertedName, eval(f"{getattr(self, convertedName)} {operation} {valueChange}"))
                        self.makeSound()
                    if keys[pygame.K_DOWN]:
                        gb.cooldown += gb.DEFAULT_COOLDOWN
                        setattr(self, convertedName, eval(f"{getattr(self, convertedName)} {gb.inverseOpp(operation)} {valueChange}"))
                        self.makeSound()

    def playButton(self):
        gb.cooldown += gb.DEFAULT_COOLDOWN
        self.playSound()

    def resetButton(self):
        for instance in self.baseValues:
            instanceName = instance[0]
            instanceValue = instance[1]
            # resets all attributes stored in self.baseValues to what they were originally at the moment that self.baseValues was called last. (init)
            setattr(self, gb.cammelCase(instanceName), instanceValue)
        # then makes the soundwaves so that they can be properly rendered
        self.makeSound()

    def getData(self):
        returnStr = ""

        returnStr += f"-- SOUND SETTINGS --\n"
        for instance in self.stateSettings:
            name = instance[0]
            convertedName = gb.cammelCase(name)

            returnStr += f"{name}: {getattr(self, convertedName)}\n"
        returnStr += f"\n"

        returnStr += f"-- TOGGLES --\n"
        returnStr += f"Draw Mode: {self.drawMode}\n"
        returnStr += f"Controlling: {self.controllerState}\n\n"

        returnStr += f"-- FREQUENCY --\n"
        returnStr += f"{self.getFrequency()}\n\n"

        return returnStr        


    def update(self, keys, screen):
        self.userInput(keys)
        self.drawFullWave(screen)
        self.drawMovingWave(screen)
        self.text.update(screen, self.getData())

class StringNote(Note):
    def __init__(self,
                 samplingRate : int = 44100,
                 duration : float = 1.5,
                 length : float = 10,
                 n : float = 1,
                 tension : float = 345.23,
                 weight : float = 5.1,
                 strength : float = 1,
                 harmonics : list = None,
                 lineStartColor : tuple = (50, 50, 255),
                 lineEndColor : tuple = (50, 255, 0),
                 circleColor : tuple = (255, 255, 255),
                 drawMode : str = "Lines"):
       
        self.length = length
        self.n = n
        self.tension = tension
        self.weight = weight # the linear density of the string
        self.strength = strength

        if harmonics == None:
            self.setHarmonics()
        else:
            self.harmonics = harmonics

        super().__init__(
            samplingRate = samplingRate,
            frequency = self.getFrequency(),
            duration = duration,
            circleColor = circleColor,
            lineStartColor = lineStartColor,
            lineEndColor = lineEndColor,
            drawMode = drawMode
        )

        self.stateSettings = [
            ["Length", pygame.K_l, 1.1, "*"],
            ["N", pygame.K_n, .1, "+"],
            ["Tension", pygame.K_t, 1.05, "*"],
            ["Weight", pygame.K_w, 1.05, "*"],
            ["Strength", pygame.K_s, .05, "+"],
            ["Duration", pygame.K_d, 1.1, "*"]
        ]

        self.setBaseValues()

    #MISC
    def setHarmonics(self):
        harmonicsLen = random.randint(1, 50) * 2
        self.harmonics = [(.5 * (random.randint(0, 100)/100)) * (abs((i-(harmonicsLen/2))/(harmonicsLen))) if i % 2 == 0 else 0 for i in range(harmonicsLen)]
        # self.harmonics = [1 * (abs((i-(len/2))/(len))) if i % 2 == 0 else 0 for i in range(len)]
        # self.harmonics = [random.randint(0, 100)/100 for i in range(3)]
        # self.harmonics = .75 * np.cos(25 * np.linspace(0, 1, 500))

    #SOUND
    def makeSound(self):
        self.frames = int(self.duration * self.samplingRate)

        timeFrame = np.linspace(0, self.duration, self.frames) # the time at i index for all frames

        harmonics = self.harmonics.copy()
        maxHarmonicVal = max(harmonics)
        for i in range(len(harmonics)):
            # if harmonics[i]/maxHarmonicVal > self.strength: # limits the values changed to only those that exceed the max strength threshold.
                harmonics[i] = self.strength * maxHarmonicVal # just having this line alone gives more versatile and interesting results though.

        self.wave = np.zeros_like(timeFrame)

        frequency = self.getFrequency()
        for i, amplitude in enumerate(harmonics):
            harmonicFrequency = frequency * (i + 1)
            self.wave += amplitude * np.cos(2 * np.pi * harmonicFrequency * timeFrame)

        self.wave *= np.exp(-3 * timeFrame) # Exponential decay

        self.wave = (32768 * self.wave).astype(np.int16)
        stereoWave = np.asarray([self.wave, self.wave]).T
        self.sound = pygame.sndarray.make_sound(stereoWave.copy())

    def getFrequency(self):
        return ((2*self.length/self.n))*math.sqrt(self.tension/self.weight)
    
    #USER INPUT
    def resetButton(self):
        gb.cooldown += gb.DEFAULT_COOLDOWN
        super().resetButton()
        self.setHarmonics()
        self.makeSound()
        self.lineStartColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.lineEndColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
