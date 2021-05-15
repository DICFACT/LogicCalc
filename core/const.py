"""Глобальные константы"""

CAPTION: str = 'LogicCalc by KUCHUKOV (fps: {FPS})'
FPS: int = 50

ORIGINAL_SIZE: (int, int) = 1920, 1080
# SCALING: float = 0.5
SCALING: float = 0.75


# CALCULATED CONSTANTS ##############################################
def recalculate_screen_size():
    """."""
    global SCREEN_SIZE
    SCREEN_SIZE = int(ORIGINAL_SIZE[0] * SCALING), int(ORIGINAL_SIZE[1] * SCALING)


SCREEN_SIZE: (int, int) = ...
recalculate_screen_size()
