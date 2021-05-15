"""Файл класса GUISystem"""
import ctypes
import tkinter
from tkinter import Tk

import pygame

from core import const, style
from core.gui.gui_element import GUIElement


class GUISystem:
    """Менеджер графических элементов"""

    def __init__(self):
        self.__screen: pygame.Surface = ...

    def get_screen(self):
        """Возвращает объект Surface"""
        return self.__screen

    def get_value(self):
        """..."""
        res = ['']

        def __get_pressed():
            res[0] = widget.get()
            root.destroy()

        root = Tk()
        widget = tkinter.Entry(root, width=50)
        widget.pack(side=tkinter.LEFT)
        button = tkinter.Button(root, text=">", command=__get_pressed)
        button.pack(side=tkinter.LEFT)
        root.mainloop()

        return res[0]

    def initialize(self):
        """Создаёт окно и конфигурирует систему"""
        ctypes.windll.user32.SetProcessDPIAware()
        self.__screen = pygame.display.set_mode(const.SCREEN_SIZE)

    def setup(self):
        """Отрисовывает основные элементы"""
        GUIElement.setup_all()

        # Background
        style.draw_block('.app')
        style.draw_icon('.logo')
        pygame.display.update()

    def update(self):
        """Обновляет графическую систему. Вызывается каждый кадр"""
        GUIElement.update_all()

    def handle(self, event: pygame.event.Event):
        """Обрабатывает событие"""
        GUIElement.send_to_all(event)


GUISystem = GUISystem()
