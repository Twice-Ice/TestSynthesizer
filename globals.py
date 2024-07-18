import pygame

pygame.font.init()

SCREEN_X = 2256/2
SCREEN_Y = 1504/2
FPS = 60
BG_COLOR = (0, 0, 0)
DEFAULT_COOLDOWN = .125
cooldown = 0
FONT = pygame.font.SysFont("Arial", 15)

def updateCooldown(delta):
    global cooldown
    if cooldown > 0:
        cooldown -= delta
    elif cooldown < 0:
        cooldown = 0

def halfRound(val : float, n_digits : int = 0):
    val *= 10 ** n_digits
    result = int(val + (0.50002 if val >= 0 else -0.50002))
    return result / 10 ** n_digits

def inverseOpp(operation : str):
    inverse = {
        "+" : "-",
        "-" : "+",
        "*" : "/",
        "/" : "*"
    }

    return inverse[operation]

def cammelCase(string : str):
    string = string.replace(" ", "")
    return string[0:1].lower() + string[1:]

'''
- color
- minColor
- maxColor

caps the color values of color to minColor and maxColor values.
'''
def capColor(color : tuple, minColor : tuple = (0, 0, 0), maxColor : tuple = (255, 255, 255)):
    cappedColor = [0, 0, 0]
    for i in range(3):
        if color[i] < minColor[i]:
            cappedColor[i] = (minColor[i])
        elif color[i] > maxColor[i]:
            cappedColor[i] = (maxColor[i])
        else:
            cappedColor[i] = (color[i])

    return (cappedColor[0], cappedColor[1], cappedColor[2])