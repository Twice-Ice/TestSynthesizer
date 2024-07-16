SCREEN_X = 2256/2
SCREEN_Y = 1504/2
FPS = 60
BG_COLOR = (0, 0, 0)
DEFAULT_COOLDOWN = .125
cooldown = 0

def updateCooldown(delta):
    global cooldown
    if cooldown > 0:
        cooldown -= delta
    elif cooldown < 0:
        cooldown = 0