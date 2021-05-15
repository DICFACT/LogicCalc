"""Файл класса Rect"""
import typing as t

from core import const
from core.utils import vec


class Rect:
    """."""

    def __init__(self, x: float, y: int, w: int, h: int):
        self.__rect: (int, int, int, int) = x, y, w, h

    @property
    def rect(self):
        """Возвращает область соответствующую данному прямоугольнику при текущем параметре scale для проекта"""
        return vec.imul(self.__rect, const.SCALING)

    @property
    def size(self):
        """Возвращает размеры области в соответствии с параметром scale выставленным для проекта"""
        return vec.imul((self.__rect[2], self.__rect[3]), const.SCALING)

    @property
    def pos(self):
        """Возвращает позицию верхнего левого угла области в соответствии с параметром scale выставленным для проекта"""
        return vec.imul((self.__rect[0], self.__rect[1]), const.SCALING)


def in_bounds(rect: [int, int, int, int], point: [int, int]):
    """."""
    px, py = point
    x, y, w, h = rect
    return x <= px <= w + x and y <= py <= h + y
