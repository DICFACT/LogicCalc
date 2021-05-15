"""Цвета и другие константы, отвечающие за внешний вид приложения"""
import typing as t

import pygame

from core.engine import processor
from core.utils.rect import in_bounds

CONTENT: dict[str, dict] = ...  # После вызова ResourceLoader.load() здесь хранится распаршенный стиль


def get_element(element: str):
    """Возвращает элемент"""
    return CONTENT[element]


def get(element: str, tag: str):
    """Возвращает значение тега указанного элемента"""
    return CONTENT[element][tag]


# MAPPINGS ##########################################################
CONSTANT_MAPPING = {
    True: 'true',
    False: 'false'
}
VARIABLE_MAPPING = {
    (processor.T_A, False): 'a',
    (processor.T_A, True): 'na',
    (processor.T_B, False): 'b',
    (processor.T_B, True): 'nb',
    (processor.T_C, False): 'c',
    (processor.T_C, True): 'nc',
    (processor.T_D, False): 'd',
    (processor.T_D, True): 'nd',
    (processor.T_E, False): 'e',
    (processor.T_E, True): 'ne',
    (processor.T_F, False): 'f',
    (processor.T_F, True): 'nf',
}
OPERATION_MAPPING = {
    (processor.T_AND, False): 'and',
    (processor.T_AND, True): 'nand',
    (processor.T_OR, False): 'or',
    (processor.T_OR, True): 'nor',
    (processor.T_XOR, False): 'xor',
    (processor.T_XOR, True): 'nxor',
}
EXPR_CONSTANT_MAPPING = {
    True: '1',
    False: '0'
}
EXPR_VARIABLE_MAPPING = {
    processor.T_A: 'A',
    processor.T_B: 'B',
    processor.T_C: 'C',
    processor.T_D: 'D',
    processor.T_E: 'E',
    processor.T_F: 'F'
}
EXPR_OPERATION_MAPPING = {
    processor.T_AND: '∧',
    processor.T_OR: '∨',
    processor.T_XOR: '⊕',
}
EXPR_BRACKETS = '()'
OPERATIONS = {
    processor.T_AND: lambda a, b: a and b,
    processor.T_OR: lambda a, b: a or b,
    processor.T_XOR: lambda a, b: a != b
}


# BACK ##########################################

pass


# GUI BUILDING ##################################

def sequence(__element: str, of: t.Sequence = (None,)):
    """."""
    element = get_element(__element)
    x, y, w, h = element.get('item-rect')
    dx, dy = element.get('shift')
    for i, item in enumerate(of):
        yield item, (x + i * dx, y + i * dy, w, h)


# BLIT ##########################################

def blit_block(surface, __element: str, rect: [int, int, int, int] = None):
    """."""
    background = get(__element, 'background')
    outline = get(__element, 'outline')
    rect = rect or get(__element, 'rect')
    pygame.draw.rect(surface, background, rect)
    pygame.draw.rect(surface, outline, rect, 1)


def blit_icon(surface, __element: str, rect: [int, int, int, int] = None):
    """."""
    icon = get(__element, 'icon')
    x, y, _, _ = rect or get(__element, 'icon-rect')
    surface.blit(icon, (x, y))


def blit_button(surface: pygame.Surface, __element: str, rect: [int, int, int, int] = None, sel: bool = False, hov: bool = False):
    """."""
    if sel:
        background = get(__element, 'background-sel')
        outline = get(__element, 'outline-sel')
    else:
        background = get(__element, 'background-hov' if hov else 'background')
        outline = get(__element, 'outline-hov' if hov else 'outline')

    rect = rect or get(__element, 'rect')
    pygame.draw.rect(surface, background, rect)
    pygame.draw.rect(surface, outline, rect, 1)

    if 'icon' not in get_element(__element):
        return

    icon = get(__element, 'icon-sel' if sel else 'icon')
    icon_rect = get(__element, 'icon-rect')
    x, y, _, _ = rect
    ix, iy, _, _ = icon_rect
    surface.blit(icon, (x + ix, y + iy))


# DRAW ##########################################

def draw_block(__element: str, rect: [int, int, int, int] = None):
    """."""
    screen = pygame.display.get_surface()
    blit_block(screen, __element, rect)


def draw_icon(__element: str, rect: [int, int, int, int] = None):
    """."""
    screen = pygame.display.get_surface()
    x, y, _, _ = rect or CONTENT[__element].get('rect') or (0, 0, 0, 0)
    ix, iy, _, _ = get(__element, 'icon-rect')
    blit_icon(screen, __element, (x + ix, y + iy, 0, 0))


def draw_button(__element: str, rect: [int, int, int, int] = None, sel: bool = False):
    """."""
    hov = in_bounds(rect or get(__element, 'rect'), pygame.mouse.get_pos())
    screen = pygame.display.get_surface()
    blit_button(screen, __element, rect, sel, hov)
