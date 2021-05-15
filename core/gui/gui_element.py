"""."""
import pygame


class GUIElement:
    """Базовый класс для всех графических элементов"""

    __instances: list['GUIElement'] = []

    def __init__(self):
        GUIElement.__instances.append(self)

    @classmethod
    def setup_all(cls):
        """Вызывает метод _setup у всех дочерних классов"""
        for inst in cls.__instances:
            inst._setup()

    @classmethod
    def update_all(cls):
        """Вызывает _update у всех дочерних классов"""
        for inst in cls.__instances:
            inst._update()

    @classmethod
    def send_to_all(cls, event: pygame.event.Event, no_break: bool = False):
        """Вызывает _handle у всех дочерних классов"""
        for inst in cls.__instances:
            if inst._handle(event) and not no_break:
                break

    def _setup(self):
        pass

    def _update(self):
        pass

    def _handle(self, event: pygame.event.Event):
        pass
