"""Файл класса ToolBarGUI"""
import pygame

from core import style
from core.gui.gui_element import GUIElement

GATES = ['and', 'or', 'xor', 'nand', 'nor', 'nxor']


class ToolBarGUI(GUIElement):
    """Static class."""

    def _update(self):
        style.draw_block('.toolbar')
        style.draw_block('.toolbar-panel')
        for item, rect in style.sequence('.toolbar-panel-buttons', of=GATES):
            style.draw_button(f'.toolbar-panel-buttons-{item}', rect=rect, sel=False)

        pygame.display.update(style.get('.toolbar', 'rect'))


ToolBarGUI: ToolBarGUI = ToolBarGUI()
