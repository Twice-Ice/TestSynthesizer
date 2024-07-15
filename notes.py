import numpy as np
import pygame
import os
import math
import globals as gb
import time
import random

class note:
	def __init__(self, samplingRate : int = 44100, frequency : float = 440, duration : float = 1.5):
		self.samplingRate = samplingRate
		self.frequency = frequency
		self.duration = duration
		self.sound = None
		self.frames = int(self.duration * self.samplingRate)
		self.start_time = None
		self.last_drawn_index = 0
	
	def makeSound(self):
		self.frames = int(self.duration * self.samplingRate)
		
		arr = np.cos(2*np.pi*self.frequency*np.linspace(0, self.duration, self.frames))*np.linspace(1, 0, self.frames) #np.linspace(start, stop, # of samples)
		
		self.sound = np.asarray([32767*arr,32767*arr]).T.astype(np.int16)
		self.sound = pygame.sndarray.make_sound(self.sound.copy())
		
	def playSound(self):
		if self.sound != None:
			self.sound.stop()
		self.makeSound()
		self.sound.play()
		self.start_time = time.time()
		self.last_drawn_index = 0

class stringNote(note):
	def __init__(self, 
				 length : float = 10,
				 n : float = 1,
				 tension : float = 345.23,
				 linearDensity : float = 5.1,
				 duration : float = 2):
		self.length = length
		self.n = n
		self.tension = tension
		self.linearDensity = linearDensity
		self.duration = duration
		self.harmonics = [.5 * self.halfRound(random.randint(0, 100)/100) for i in range(5)]
		# self.harmonics = [random.randint(0, 100)/100 for i in range(3)]
		# self.harmonics = .75 * np.cos(25 * np.linspace(0, 1, 500))

		self.printStats()
		
		super().__init__(
			frequency = ((2*self.length/self.n))*math.sqrt(self.tension/self.linearDensity),
			duration = self.duration
		)

		self.wave = np.linspace(0, self.duration, self.frames)

	"""
		A half round function with n_digits after the decimal being able to be the last digit.

		copy and pasted from codequest notes bcs I'm lazy :)
	"""
	def halfRound(self, val:float, n_digits:int = 0):
		val *= 10**n_digits
		result = int(val + (0.50002 if val >= 0 else -0.50002))
		return result / 10**n_digits

	def makeSound(self):
		self.frequency = ((2*self.length/self.n))*math.sqrt(self.tension/self.linearDensity)

		self.frames = int(self.duration * self.samplingRate)

		t = np.linspace(0, self.duration, self.frames)
		# harmonics = np.linspace(1, 0, 100)
		harmonics = self.harmonics
		self.wave = np.zeros_like(t)

		for i, amplitude in enumerate(harmonics):
			harmonic_freq = self.frequency * (i + 1)
			self.wave += amplitude * np.sin(2 * np.pi * harmonic_freq * t)
		
		decay = np.exp(-3 * t)  # Exponential decay
		self.wave *= decay

		self.wave = (32767 * self.wave).astype(np.int16)
		stereo_wave = np.asarray([self.wave, self.wave]).T
		self.sound = pygame.sndarray.make_sound(stereo_wave.copy())

	def printBaseStats(self):
		baseStatsStr = ""
		# os.system("cls")
		baseStatsStr += f"Length : {self.length}\n"
		baseStatsStr += f"N : {self.n}\n"
		baseStatsStr += f"Tension : {self.tension}\n"
		baseStatsStr += f"String Density : {self.linearDensity}\n"
		baseStatsStr += f"Duration : {self.duration}\n\n"

		return baseStatsStr
	
	def printStats(self):
		statsStr = self.printBaseStats()

		statsStr += f"String Length: {((2*self.length)/self.n)}        = (2*{self.length}/{self.n})\n"
		statsStr += f"Base Frequency: {math.sqrt(self.tension/self.linearDensity)}        = sqrt({self.tension}/{self.linearDensity})\n"
		statsStr += f"Frequency: {((2*self.length)/self.n)*math.sqrt(self.tension/self.linearDensity)}        = {((2*self.length)/self.n)}*{math.sqrt(self.tension/self.linearDensity)}\n"

		return statsStr
	
	def drawFullWave(self, screen):
		# Normalize wave to fit within the screen height
		reducedWave = self.wave[::int((self.frames)/gb.SCREEN_X)]
		normalized_wave = reducedWave / np.max(np.abs(reducedWave)) * 150  # Adjust the multiplier for appropriate scaling
		x = np.linspace(0, gb.SCREEN_X, len(reducedWave))
		y = gb.SCREEN_Y - (150*3) + normalized_wave

		for i in range(1, len(x)):
			pygame.draw.line(screen, (0, 0, 255), (x[i-1], y[i-1]), (x[i], y[i]))

	def drawMovingWave(self, screen):
		if self.start_time is None:
			return

		elapsed_time = time.time() - self.start_time
		if elapsed_time > self.duration:
			elapsed_time = self.duration

		# Calculate the number of frames to display based on elapsed time
		current_frame = int((elapsed_time / self.duration) * self.frames)
		start_frame = max(self.last_drawn_index, current_frame - int(self.samplingRate * elapsed_time))
		end_frame = min(self.frames, current_frame + int(self.samplingRate * elapsed_time))

		# Normalize wave to fit within the screen height
		normalized_wave = self.wave[start_frame:end_frame] / np.max(np.abs(self.wave)) * 150  # Adjust the multiplier for appropriate scaling
		x = np.linspace(0, gb.SCREEN_X, end_frame - start_frame)
		y = gb.SCREEN_Y - 150 + normalized_wave

		# Draw the wave segment
		for i in range(1, len(x)):
			pygame.draw.line(screen, (0, 0, 255), (x[i-1], y[i-1]), (x[i], y[i]))

		# Update the last drawn index
		self.last_drawn_index = end_frame