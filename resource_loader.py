"""Файл класса ResourceLoader"""
import typing as t

import pygame
import yaml

from core import const, style
from core.utils import color


class ResourceLoader:
    """Закгрузщик ресурсов"""

    __ICON_TAG: str = 'icon'  # This tag will be added to element and will contain icon surface
    __ICON_SEL_TAG: str = 'icon-sel'  # Selected variant
    __BACKGROUND_TAG: str = 'background'  # If this tag is in element icon (for element) will be loaded with background
    __BACKGROUND_SEL_TAG: str = 'background-sel'  # This thing will do the same
    __FONT_TAG: str = 'font'
    __FONT_COLOR_TAG: str = 'font-color'

    __ICON_RECT_TAG: str = 'icon-rect'
    __FONT_SIZE_TAG: str = 'font-size'

    __SCALE_DEPENDENT_TAGS: list[str] = [
        'rect', 'item-rect', 'shift', 'icon-rect',
        'font-size', 'bar', 'font-spacing', 'indent'
    ]
    __IMAGE_LOADING_TAGS: list[str] = ['icon-path']
    __FONT_LOADING_TAGS: list[str] = ['font-path']

    def __init__(self):
        pass

    def __scaled_tag_value(self, value: t.Union[int, list[int, ...]]):
        if type(value) is int:
            return int(value * const.SCALING)
        return list(map(lambda x: int(x * const.SCALING), value))

    def __load_image(self, path: str, rect: [int, int, int, int], background: int = None, fit: int = None):
        _, _, width, height = rect
        try:
            image = pygame.image.load(path)
        except FileNotFoundError:
            raise FileNotFoundError(f'No such file as \'{path}\'')

        iw, ih = width, height
        if fit:
            size = width, height
            i_size = image.get_size()
            kof = size[fit], size[fit] * i_size[1 - fit] / i_size[fit]
            iw, ih = int(kof[fit]), int(kof[1 - fit])

        if background is None:
            return pygame.transform.smoothscale(image, (iw, ih))

        back = pygame.Surface(image.get_size())
        back.fill(color.int_to_tuple(background))
        back.blit(image, (0, 0))

        return pygame.transform.smoothscale(back, (iw, ih))

    def load(self):
        """Загружает ресурсы"""
        with open('core/resources/style.yaml') as file:
            content = yaml.load(file, Loader=yaml.FullLoader)

        # Подгоняем размеры всех тегов описывающих размеры под масштаб приложения
        for elem, tags in content.items():
            for tag, value in tags.items():
                if tag in self.__SCALE_DEPENDENT_TAGS:
                    tags[tag] = self.__scaled_tag_value(value)

        loaded_fonts = {}
        for elem, tags in content.items():
            changes = {}
            for tag, value in tags.items():
                # Загружаем изображения
                if tag in self.__IMAGE_LOADING_TAGS and value != '':
                    rect = tags[self.__ICON_RECT_TAG]

                    fit = None
                    if 'fit' in tags:
                        fit = ['width', 'height'].index(tags['fit'])

                    if self.__BACKGROUND_TAG in tags:
                        color_ = tags[self.__BACKGROUND_TAG]
                        changes[self.__ICON_TAG] = self.__load_image(value, rect, color_, fit)
                    else:
                        changes[self.__ICON_TAG] = self.__load_image(value, rect, fit)
                        continue

                    if self.__BACKGROUND_SEL_TAG in tags:
                        color_ = tags[self.__BACKGROUND_SEL_TAG]
                        changes[self.__ICON_SEL_TAG] = self.__load_image(value, rect, color_, fit)
                    continue

                # Загружаем шрифты
                if tag in self.__FONT_LOADING_TAGS and value != '':
                    size = tags[self.__FONT_SIZE_TAG]
                    if (value, size) not in loaded_fonts:  # Если шрифт ещё не был загружен - загружаем
                        loaded_fonts[value, size] = pygame.font.Font(value, size)
                    changes[self.__FONT_TAG] = loaded_fonts[value, size]
                    continue

            tags.update(changes)

        style.CONTENT = content


ResourceLoader = ResourceLoader()
