import pygame
import numpy as np
import os
import math

pygame.init()
pygame.mixer.init()

doExit = False

"""
    asks the user a question, along with a list of possible answer options. 
    Then if the user says something that isn't an option, the question is asked again, otherwise, the user's answer is returned.

    default is the default answer option

    Int or Float answerOptions:
        [str : operation, int/float : comparisonValue]
        [[str : operation, int/float : comparisonValue], [etc.]]
        No settings defaults to no comparison, and only checks if the value is a valid input for the selected answer type.
"""
def question(questionStr : str, answerType : any, answerOptions : list = [],  default : any = None, clearScreen : bool = True, firstInstanceCall : bool = True) -> any:
    if clearScreen:
        os.system("cls")

    command = input(questionStr)

    #so that the user is always a line down and corrects the dev's mistake
    if firstInstanceCall:
        if questionStr[len(questionStr)-2:len(questionStr)] != "\n":
            questionStr += "\n"

    def fail(qStr, aType, aOptions, failMsg : str = f"{command} is not a valid option.\n\n"):
        os.system("cls")
        print(failMsg)
        return question(qStr, aType, aOptions, firstInstanceCall = False)

    try:
        #default answer option
        if command == "":
            if default != None:
                return default
            else:
                fail(questionStr, answerType, answerOptions, f"There is no default answer, please choose a valid option.\n\n")

        elif answerType == str:
            return str(command)
        elif answerType == int or answerType == float:
            #if there's settings
            if len(answerOptions) > 0:
                try:
                    #mutiple settings
                    if type(answerOptions[0]) == list:
                        #loops through all answer options and if none of them make you fail, then command is returned.
                        for case in answerOptions:
                            if not eval(f"{command} {case[0]} {case[1]}"):
                                return fail(questionStr, answerType, answerOptions, f"{command} should be {case[0]} than {case[1]}.\n\n")
                        return answerType(command)
                    #single setting
                    else:
                        #evaluates the single setting case to see if a value is returned or not.
                        if eval(f"{command} {answerOptions[0]} {answerOptions[1]}"):
                            return answerType(command)
                        else:
                            return fail(questionStr, answerType, answerOptions, f"{command} should be {answerOptions[0]} than {answerOptions[1]}.\n\n")
                except:
                    raise TypeError(f"{answerOptions[0]} is not a valid operation.")
            else:
                #no settings
                return answerType(command)
        elif answerType == list or answerType == dict:
            #so that dicts can work properly and not have to format before calling self.question(), 
            #the following code is required to properly return the user's choice.
            #answerOptionNames stores the raw unformated names, whereas formatedAnswerOptionNames is all lowercase.
            answerOptionNames = []
            formatedAnswerOptionNames = []
            for i in answerOptions:
                answerOptionNames.append(i)
                formatedAnswerOptionNames.append(str.lower(i))
            
            if command.lower() in formatedAnswerOptionNames:
                if answerType == dict:
                    #returns the original format answer version based on the user's command.
                    return answerOptionNames[formatedAnswerOptionNames.index(command.lower())]
                else:
                    return command.lower()
            
        #if the function gets to this point then it's because none of the options chosen were valid so therefor the option was invalid.
        return fail(questionStr, answerType, answerOptions)
    except:
        return fail(questionStr, answerType, answerOptions)

"""
    Prompts the user with a yes or no question. The user can always press enter to just use the default option.
"""
def yesNo(questionStr, clearScreen : bool = True, default : bool = True) -> bool:
    if clearScreen:
        os.system("cls")
    command = input(questionStr)
    try:
        command = command.lower()
        match command:
            case "y":
                return True
            case "n":
                return False
            case "":
                return default
            case _:
                return yesNo(f"{command} is not a valid option, please try again.\n\n{questionStr}")
    except:
        return yesNo(f"{command} is not a valid option, please try again.\n\n{questionStr}")

class note:
    def __init__(self, samplingRate : int = 44100, frequency : float = 440, duration : float = 1.5):
        self.samplingRate = samplingRate
        self.frequency = frequency
        self.duration = duration
    
    def makeSound(self):
        frames = int(self.duration * self.samplingRate)
        arr = np.cos(2*np.pi*self.frequency*np.linspace(0, self.duration, frames)) #np.linspace(start, stop, # of samples)
        sound = np.asarray([32767*arr,32767*arr]).T.astype(np.int16)
        sound = pygame.sndarray.make_sound(sound.copy())
        
        return sound
    
    def playSound(self):
        os.system("cls")
        print("playing...")
        self.makeSound().play()
        os.system("cls")

class manualSinNote(note):
    def __init__(self):
        super().__init__(
            #samplingRate = question("Sampling Rate?\n[default 44100]\n", int, default = 44100),
            frequency = question("Frequency?\n", float, default = 440),
            duration = question("Duration?\n", float, default = 1.5)
        )
        self.playSound()

class manualStringNote(note):
    def __init__(self):
        self.length = 10
        self.n = 1
        self.tension = 500
        self.linearDensity = .5
        self.duration = 1.5

        self.printStats()
        
        super().__init__(
            frequency = ((2*self.length/self.n))*math.sqrt(self.tension/self.linearDensity),
            duration = self.duration
        )

        # self.playSound()

    def setValue(self):
        options = {
            "Length" : "length",
            "N" : "n",
            "Tension" : "tension",
            "String Density" : "linearDensity",
            "Duration" : "duration",
        }

        self.printStats()

        case = question("Choose one: [Length, N, Tension, String Density, Duration]\n", dict, options, clearScreen = False)

        self.printStats()

        setattr(self, options[case], question(f"{case}?\n", float, clearScreen = False))
        self.frequency = ((2*self.length/self.n))*math.sqrt(self.tension/self.linearDensity)
        
            
    def printBaseStats(self):
        os.system("cls")
        print(f"Length : {self.length}")
        print(f"N : {self.n}")
        print(f"Tension : {self.tension}")
        print(f"String Density : {self.linearDensity}")
        print(f"Duration : {self.duration}\n")
    
    def printStats(self):
        self.printBaseStats()

        print(f"String Length: {((2*self.length)/self.n)}        = (2*{self.length}/{self.n})")
        print(f"Base Frequency: {math.sqrt(self.tension/self.linearDensity)}        = sqrt({self.tension}/{self.linearDensity})")
        print(f"Frequency: {((2*self.length)/self.n)*math.sqrt(self.tension/self.linearDensity)}        = {((2*self.length)/self.n)}*{math.sqrt(self.tension/self.linearDensity)}\n")

playedNote = manualStringNote()
while doExit != True:
    os.system("cls")
    playedNote.playSound()
    playedNote.printStats()
    match question("[Enter] to continue or \"Edit\" to edit values\n", str, default = "", clearScreen = False):
        case "edit":
            playedNote.setValue()
        case "e":
            playedNote.setValue()
        case "play":
            playedNote.playSound()
        case "p":
            playedNote.playSound()
        case _:
            pass