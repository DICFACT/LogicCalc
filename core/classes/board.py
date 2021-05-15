"""Файл класса Board"""
import typing as t
from collections import namedtuple

import pygame
from pygame import Surface, Rect

from . import math2d
from .types_ import tVector2, tIVector2

DEFAULT_STYLE = {
    "background": (40, 40, 40),

    "grid-color": (76, 74, 72),

    "zoom_indicator-height": 16,
    "zoom_indicator-width": 220,
    "zoom_indicator-color": (92, 90, 88),
    "zoom_indicator-slider-color": (255, 255, 255),
    "zoom_indicator-line-thickness": 1,
    "zoom_indicator-line-width": 140,
    "zoom_indicator-font": "Segoe UI",
    "zoom_indicator-font-size": 12,
    "zoom_indicator-interval": 5,
    "zoom_indicator-pads": (5, 15),

    "selection": (255, 255, 255)
}


# TODO: До документировать
# TODO: Оптимизировать перерисовку, учитываея возможное отсутствие слоёв отрисовки
#   Реализовать redraw_render_layer и атрибут cache
# TODO: Реализовать перерисовку доски при выделении объектов
# TODO: Вшить в доску слой рендера для выделения
# TODO: Создать метод selection_begin и selection_end и совместить их со слоем рендера
# TODO: Реализовать перерисовку засчёт флагов, чтобы автоматически перерисовывать нужные слои


RLFLAG_STATIC_LAYER = 0
RLFLAG_SCALE_DEP = 1
RLFLAG_BOARD_MOVEMENT_DEP = 1 << 1
RLFLAG_OBJECT_MOVEMENT_DEP = 1 << 2
RLFLAG_SELECTION_DEP = 1 << 3
RLFLAG_ALL = (1 << 4) - 1


class BoardObject:
    """."""
    def __init__(self, original: t.Any, pos: t.Tuple[float, float]):
        self.original: t.Any = original
        self.position: t.Tuple[float, float] = pos
        self.selected: bool = False


class RenderLayer:
    """."""
    def __init__(self, layer: t.Callable[["Board", Surface], None], enabled: bool, flags: int):
        self.enabled: bool = enabled
        self.render: t.Callable[[Board, Surface], None] = layer
        self.flags: int = flags
        self.dirty: bool = True


GrabData = namedtuple('GrabData', ['object', 'gl_start', 'lc_start_pos'])


class Board:
    """."""
    def __init__(self, rect: t.Union[Rect, t.Tuple[int, int, int, int]], grid: int = None, style: dict = None):
        self.__rect: Rect = Rect(rect)  # Положение и размер доски на экране
        self.__surface: Surface = Surface(self.__rect.size)  # Изображение доски
        self.__scale: float = 1  # Отношение размера видимой области к размеру доски
        self.__pos: t.Tuple[float, float] = 0, 0  # Локальная позиция центра видимой области

        self.__objects: t.List[BoardObject] = []
        self.__zoom_presets: t.Tuple[float, ...] = (2.0, 1.5, 1.0, 0.5, 0.25, 0.2)
        self.__grid: t.Optional[int] = grid

        self.__rl_cache: t.List[t.Optional[Surface]] = []
        self.__render_layers: t.List[RenderLayer] = []
        self.__background_layer: RenderLayer = self.add_render_layer(RL_BACKGROUND, flags=RLFLAG_STATIC_LAYER)
        self.__grid_layer: RenderLayer = self.add_render_layer(RL_GRID_DOTS, flags=RLFLAG_SCALE_DEP | RLFLAG_BOARD_MOVEMENT_DEP)
        self.__object_layer: RenderLayer = self.add_render_layer(RL_OBJECT_RENDERER, flags=RLFLAG_SCALE_DEP | RLFLAG_BOARD_MOVEMENT_DEP | RLFLAG_OBJECT_MOVEMENT_DEP)
        self.__selection_layer: RenderLayer = self.add_render_layer(RL_SELECTION, flags=RLFLAG_SCALE_DEP | RLFLAG_BOARD_MOVEMENT_DEP | RLFLAG_OBJECT_MOVEMENT_DEP | RLFLAG_SELECTION_DEP)

        self.__dirty = True

        self.style = style or DEFAULT_STYLE

    # PROPERTIES ######################
    @property
    def scale(self):
        """."""
        return self.__scale

    @scale.setter
    def scale(self, value: float):
        self.__scale = value
        self.set_flags_dirty(RLFLAG_SCALE_DEP)

    @property
    def pos(self):
        """."""
        return self.__pos

    @pos.setter
    def pos(self, value: tVector2):
        self.__pos = value
        self.set_flags_dirty(RLFLAG_BOARD_MOVEMENT_DEP)

    @property
    def grid(self):
        """."""
        return self.__grid

    @property
    def grid_render_layer(self):
        """."""
        return self.__grid_layer

    @property
    def object_render_layer(self):
        """."""
        return self.__object_layer

    @property
    def selection_render_layer(self):
        """."""
        return self.__selection_layer

    # COORDINATES MANIPULATION ########
    def to_global(self, point: tVector2):
        """
        **Переводит координаты точки на доске в координаты на экране.**

        *Зависит от положения доски и приближения.*

        Используйте с BoardObject.position, чтобы получить координаты объекта на экране. Пр.:

        `print(board.to_global(obj.position))`

        :param point: точка относительно центра доски, не зависимая от приближения
        :return: точка относительно левого верхнего угла экрана
        """
        x, y = point
        sx, sy = self.__pos
        bx, by = self.__rect.center
        return (x - sx) / self.__scale + bx, (y - sy) / self.__scale + by

    def to_local(self, point: tVector2):
        """
        **Переводит координаты точки на экране в координаты на доске.**

        *Зависит от положения доски и приближения.*

        Используя с событием pygame.MOUSEBUTTONDOWN, можно получить место клика на доске. Пр.:

        `print(board.to_local(event.pos))`

        :param point: точка относительно левого верхнего угла экрана
        :return: точка относительно центра доски, не зависимая от приближения
        """
        x, y = point
        sx, sy = self.__pos
        bx, by = self.__rect.center
        return (x - bx) * self.__scale + sx, (y - by) * self.__scale + sy

    def to_objects_local(self, obj: BoardObject, point: tVector2):
        """."""
        lp = self.to_local(point)
        pos = math2d.v_sub(lp, obj.position)
        if not hasattr(obj.original, "image"):
            return pos
        w, h = obj.original.image.get_size()
        pos = math2d.v_add(pos, (w / 2, h / 2))
        return pos

    # OBJECT MANIPULATION #############
    def add(self, orig: t.Any, pos: tVector2 = None):
        """
        **Добавляет объект на доску.**

        *Делает доску "грязной", если объект добавляется в видимой области*

        На доску может быть добавлен любой объект, однако отрисовываться будут только те из них,
        что имеют атрибут image.

        Возвращает представление объекта, содержащее оригинал, локальные координаты и информацию о том выделен ли он.
        Все эти поля являются изменяемыми, однако рекомендуется пользоваться интерфейсом, предоставленным доской,
        так как это автоматизирует некоторые процессы и улучшает читамельность кода.

        :param orig: объект для добавления, может быть чем угодно
        :param pos: позиция на доске, при значении None объект будет помещён в центр видимой области
        :return: представление объекта
        """
        if pos is None:
            pos = self.__pos  # Если коорд. не указаны, создаём объект в центре видимой области
        res = BoardObject(orig, pos)
        self.__objects.append(res)
        self.set_flags_dirty(RLFLAG_OBJECT_MOVEMENT_DEP)
        # Возвращаем новое представление объекта
        return res

    def remove(self, obj: BoardObject):
        """
        **Удаляет объект с доски**

        *Делает доску "грязной", если объект удаляется в видимой области*

        При попытке удаления несуществующего объекта, возврящается ValueError

        :param obj: представление объекта к удалению
        """
        self.__objects.remove(obj)
        self.set_flags_dirty(RLFLAG_OBJECT_MOVEMENT_DEP)

    def remove_rule(self, function: t.Callable[[BoardObject], bool]):
        """
        **Удаляет объекты удовлетворяющие условию**

        *Делает доску "грязной", если объект удаляется в видимой области*

        Пример, "Удаление всех объектов, не имеющих изображения":

        `board.remove_rule(lambda x: not hasattr(x.original, 'image'))`

        :param function: функция, принимающая представление и возвращающая True для объектов, которые необходимо удалить
        """
        objects = []
        for obj in self.__objects:
            if not function(obj):
                objects.append(obj)
        self.__objects = objects
        self.set_flags_dirty(RLFLAG_OBJECT_MOVEMENT_DEP)

    def remove_selected(self):
        """
        **Удаляет выделенные объекты**

        *Делает доску "грязной", если объект удаляется в видимой области*

        НЕ вызывает исключений, если не найдёт выделенных объектов

        Синоним

        `board.remove_rule(lambda x: x.selected)`
        """
        self.remove_rule(lambda x: x.selected)

    def click(self, point: tVector2):
        """
        **Вызывает метод on_click объекта, находящегося под указанными координатами**

        Методу объекта будут переданы координаты, указывающие в какую точку изображения был произведён клик.
        (координаты относительно левого верхнего угла изображения блока, в пикселях)
        При этом, если в момент клика под мышью находятся несколько объектов, метод будет вызван только у того,
        что визуально выше.

        Предполагается использование с событием pygame.MOUSEBUTTONDOWN. Пр.:

        `board.click(event.pos)`

        :param point: точка на экране, куда был произведён клик
        """
        obj = self.get_under(point)  # Полученный объект, если не равен None, гарантированно имеет атрибут 'image'
        if obj is not None and hasattr(obj.original, "on_click"):
            w, h = obj.original.image.get_size()
            pos = self.to_local(point)
            pos = math2d.v_sub(pos, (w / 2, h / 2))  # Получаем кооринаты относительно левого верхнего угла объекта
            getattr(obj.original, "on_click")(obj, pos)

    # MOVING OBJECTS ##################
    def move_object_to(self, obj: BoardObject, pos: tVector2):
        """
        **Перемещает объект в указанную точку на доске**

        *Делает доску "грязной", если объект перемещается в пределах видимой области*

        Используйте с board.pos, чтобы переместить объект в центр видимой области. Пр.:

        `board.move_to(board.pos)`

        :param obj: представление объекта, который необходимо переместить
        :param pos: новая позиция объекта в локальных координатах доски
        """
        obj.position = pos
        self.set_flags_dirty(RLFLAG_OBJECT_MOVEMENT_DEP)

    def move_object_by(self, obj: BoardObject, rel: tVector2):
        """
        **Перемещает объект на указанный вектор**

        *Делает доску "грязной", если объект перемещается в пределах видимой области*

        X координата объекта увеличивается на rel[0], Y - на rel[1]

        :param obj: представление объекта, который необходимо переместить
        :param rel: вектор, на который объект должен быть перемещён
        """
        obj.position = math2d.v_add(obj.position, rel)
        self.set_flags_dirty(RLFLAG_OBJECT_MOVEMENT_DEP)

    def snap_to_grid(self, obj: BoardObject, pivot: str = "center"):
        """
        **Выравнивает объект по сетке**

        *Делает доску "грязной", если объект находится в видимой области*

        В качестве размеров объекта берётся размер его изображения (атрибут image).
        Объекты не имеющие данного атрибута будут выровнены по центру.

        В случае, когда размер сетки для доски не задан, возвращает AttributeError.

        Аргумент pivot должен иметь одно из следующих значений:

        `topleft, bottomleft, topright, bottomright, midtop, midleft, midbottom, midright, center`

        :param obj: представление объекта, который необходимо выровнять
        :param pivot: точка, которая будет привязана к сетке
        """
        if self.__grid is None:
            raise AttributeError("Board object been initialized without grid")
        if pivot == "center" or not hasattr(obj.original, "image"):
            obj.position = math2d.grid(obj.position, (self.__grid, self.__grid))
        elif pivot not in ["topleft", "bottomleft", "topright", "bottomright", "midtop", "midleft", "midbottom", "midright"]:
            raise ValueError(f"Value '{pivot}' is not allowed for pivot.")
        else:
            obj_rect = obj.original.image.get_rect()
            obj_rect.center = obj.position
            new_pos = math2d.grid(getattr(obj_rect, pivot), (self.__grid, self.__grid))
            setattr(obj_rect, pivot, new_pos)
            obj.position = obj_rect.center
        self.set_flags_dirty(RLFLAG_OBJECT_MOVEMENT_DEP)

    def object_grab(self, obj: BoardObject, point: tVector2):
        """
        **Начинает перемещение объекта**

        Считает и сохраняет всю необходимую информацию для перемещения объекта.

        Не предпринимает никаких специальных действий для определения положения объекта относительно места клика.
        Подобран может быть любой объект, не зависимо от его положения или положения мыши.

        Чтобы продолжить перемещение, используйте метод object_drag с событием перемещения мыши.

        Пример использования с событием pygame.MOUSEBUTTONDOWN:

        `grab: GrabData = board.object_grab(obj, event.pos)`

        Для получения объекта для перемещения, можно использовать метод get_under с тем же событием:

        `obj: BoardObject = board.get_under(event.pos)  # Вернёт None, если под мышью ничего нет`

        :param obj: представление объекта, который планируется переместить
        :param point: точка в которую был произведён клик
        :return: информация, необходимая для дальнейшего перемещения
        """
        return GrabData(obj, point, obj.position)

    def object_drag(self, point: tVector2, gd: GrabData):
        """
        **Перемещает объект по доске**

        *Делает доску "грязной", если объект находится в видимой области*

        Устанавливает объект в новую локальную позицию исходя из текущей позиции мыши и данных
        о начале перемещения.

        Обычно используется с событием перемещения мыши.

        Пример с pygame.MOUSEMOTION:

        `board.object_drag(obj, event.pos, grab_data)`

        :param point: точка в которой сейчас находится мышь
        :param gd: объект, полученный с помощью board.object_grab ранее
        """
        vec = math2d.v_sub(gd.gl_start, point)
        vec = math2d.v_mul(vec, -self.__scale)
        gd.object.position = math2d.v_add(gd.lc_start_pos, vec)
        self.set_flags_dirty(RLFLAG_OBJECT_MOVEMENT_DEP)

    def object_grab_all(self, obj_list: t.List[BoardObject], point: tVector2):
        """."""
        gd_list = []
        for obj in obj_list:
            gd_list.append(self.object_grab(obj, point))
        return gd_list

    def object_drag_all(self, point: tVector2, gds: t.List[GrabData]):
        """."""
        for gd in gds:
            self.object_drag(point, gd)

    # SELECTION MANIPULATION ##########
    def selection_add(self, obj: BoardObject):
        """
        **Добавляет объект в выделение**

        *Делает доску "грязной", если объект находится в видимой области*

        :param obj: представление объекта для выделения
        """
        obj.selected = True
        self.set_flags_dirty(RLFLAG_SELECTION_DEP)

    def selection_remove(self, obj: BoardObject):
        """
        **Снимает выделение с объекта**

        *Делает доску "грязной", если объект находится в видимой области*

        :param obj: представление объекта для снятия выделения
        """
        obj.selected = False
        self.set_flags_dirty(RLFLAG_SELECTION_DEP)

    def select(self, obj: BoardObject):
        """
        **Выделяет объект, снимая выделение с остальных**

        :param obj: представление объекта, который нужно выделить
        """
        if obj not in self.__objects:
            raise ValueError("Board.select_rule(x): x not in object list")
        self.select_rule(lambda x: x == obj)

    def select_all(self):
        """
        **Выделяет все находящиеся на доске объекты**

        *Делает доску "грязной", если хотя бы один объект находится в видимой области*
        """
        # Если не использовать select_rule, в данном случае, можно
        # избежать вызова функции и проверки условия для каждого элемента
        for obj in self.__objects:
            obj.selected = True
        self.set_flags_dirty(RLFLAG_SELECTION_DEP)

    def deselect_all(self):
        """
        **Снимает выделение со всех объектов на доске**

        *Делает доску "грязной", если хотя бы один объект находится в видимой области*
        """
        for obj in self.__objects:
            obj.selected = False
        self.set_flags_dirty(RLFLAG_SELECTION_DEP)

    def select_within(self, pos1: tVector2, pos2: tVector2, add=False):
        """
        Выделяет все объекты, центры которых попадают в прямоугольник с
        указанными координатами противоположных вершин
        pos1, pos2: tVector2 - глобальные координаты вершин
        add: bool - добавить к существующему выделению
        """
        x1, y1 = pos1
        x2, y2 = pos2
        x_min, y_min = min(x1, x2), min(y1, y2)
        x_max, y_max = max(x1, x2), max(y1, y2)
        w, h = (x_max - x_min) * self.__scale, (y_max - y_min) * self.__scale
        rect = Rect(x_min, y_min, w, h)
        for obj in self.__objects:
            obj.selected = add and obj.selected or rect.collidepoint(obj.position)
        self.set_flags_dirty(RLFLAG_SELECTION_DEP)

    def select_rule(self, function: t.Callable[[BoardObject], bool]) -> None:
        """Выделяет объекты удовлетворяющие условию"""
        for obj in self.__objects:
            sel = function(obj)
            obj.selected = sel
        self.set_flags_dirty(RLFLAG_SELECTION_DEP)

    # OBJECT GETTING ##################
    def find(self, obj: t.Any):
        """."""
        try:
            return next(self.get_rule(lambda x: x.original == obj))
        except StopIteration:
            raise ValueError("Board.get(x): x not in object list")

    def get_selected(self):
        """."""
        return self.get_rule(lambda x: x.selected)

    def get_all(self):
        """."""
        for obj in self.__objects:
            yield obj

    def get_under(self, point: tVector2):
        """
        Возвращает объект, находящийся под указанной позицией. Если таких несколько, вернёт тот, что добавлен позднее

        pos: Vector2 - точка в глобальных координатах
        """
        try:
            return next(self.get_all_under(point))
        except StopIteration:
            return None

    def get_all_under(self, point: tVector2):
        """."""
        local_pos = self.to_local(point)
        # Идём от позднее добавленных к ранее
        # При отрисовке, объекты добавленные позднее будут выше
        for obj in reversed(self.__objects):
            if not hasattr(obj.original, "image"):
                continue
            rect: Rect = obj.original.image.get_rect()
            rect.center = obj.position
            if rect.collidepoint(local_pos):
                yield obj

    def get_rule(self, function: t.Callable[[BoardObject], bool]):
        """Генератор объектов находящихся на доске и подходящих под условие"""
        for obj in self.__objects:
            if function(obj):
                yield obj

    # RENDER LAYERS ###################
    def add_render_layer(self, layer: t.Callable[["Board", Surface], None], enabled: bool = True, z_index: t.Optional[int] = None, flags: int = RLFLAG_STATIC_LAYER):
        """."""
        rl = RenderLayer(layer, enabled, flags)
        if z_index is None:
            self.__render_layers.append(rl)
            self.__rl_cache.append(None)
        else:
            self.__render_layers.insert(z_index, rl)
            self.__rl_cache.insert(z_index, None)
        self.__dirty = True
        return rl

    def remove_render_layer(self, rl: RenderLayer):
        """."""
        index = self.__render_layers.index(rl)
        self.__render_layers.pop(index)
        self.__rl_cache.pop(index)
        self.__dirty = True

    def enable_render_layer(self, rl: RenderLayer):
        """."""
        rl.enabled = True
        self.__dirty = True

    def disable_render_layer(self, rl: RenderLayer):
        """."""
        rl.enabled = False
        self.__dirty = True

    def toggle_render_layer(self, rl: RenderLayer):
        """."""
        rl.enabled = not rl.enabled
        self.__dirty = True

    def set_background_renderer(self, layer: t.Callable[["Board", Surface], None]):
        """."""
        self.__background_layer.render = layer
        self.__background_layer.dirty = True
        self.__dirty = True

    def set_grid_renderer(self, layer: t.Callable[["Board", Surface], None]):
        """."""
        self.__grid_layer.render = layer
        self.__grid_layer.dirty = True
        self.__dirty = True

    def set_object_renderer(self, layer: t.Callable[["Board", Surface], None]):
        """."""
        self.__object_layer.render = layer
        self.__object_layer.dirty = True
        self.__dirty = True

    def set_flags_dirty(self, flags: int):
        """."""
        is_all = flags == RLFLAG_ALL
        for rl in self.__render_layers:
            if rl.flags & flags or is_all:
                rl.dirty = True
        self.__dirty = True

    def set_layer_dirty(self, rl: RenderLayer):
        """."""
        rl.dirty = True
        self.__dirty = True

    # BOUNDING ########################
    def get_rect(self):
        """Возвращает копию Rect доски"""
        return Rect(self.__rect)

    def set_rect(self, rect: t.Union[Rect, t.Tuple[int, int, int, int]]):
        """."""
        self.__rect = Rect(rect)
        self.__surface = Surface(self.__rect.size)
        self.set_flags_dirty(RLFLAG_ALL)

    def get_view_rect(self):
        """Возвращает Rect видимой области на доске"""
        vs = self.__rect.w * self.__scale, self.__rect.h * self.__scale
        view_rect = Rect((0, 0), vs)
        view_rect.center = self.__pos
        return view_rect

    def get_object_global_rect(self, obj: BoardObject):
        """."""
        if not hasattr(obj.original, "image"):
            return None
        rect = Rect((0, 0, 0, 0))
        rect.size = math2d.v_mul(obj.original.image.get_size(), 1 / self.__scale)
        rect.center = self.to_global(obj.position)
        return rect

    def is_visible(self, obj: BoardObject):
        """Проверяет, находится ли изображение объекта в видимой области"""
        view_rect = self.get_view_rect()

        if hasattr(obj.original, "image"):
            rect: Rect = obj.original.image.get_rect()
            rect.center = obj.position
            return bool(view_rect.colliderect(rect))
        return False

    def is_within(self, point: tVector2):
        """Находится ли точка в пределах доски"""
        return self.__rect.collidepoint(point)

    # VISUALIZATION ###################
    def recache(self):
        """."""
        for i, rl in enumerate(self.__render_layers):
            if rl.enabled and rl.dirty:
                surf = Surface(self.__rect.size, pygame.SRCALPHA)
                rl.render(self, surf)
                self.__rl_cache[i] = surf
                rl.dirty = False

    def redraw(self):
        """."""
        for rl, rlc in zip(self.__render_layers, self.__rl_cache):
            if rl.enabled:
                self.__surface.blit(rlc, (0, 0))

    def set_dirty(self):
        """."""
        self.__dirty = True

    def blit_on(self, surface: Surface):
        """Рисует доску на поверхности в заранее заданных координатах"""
        if self.__dirty:
            self.__dirty = False
            self.recache()
            self.redraw()
        surface.blit(self.__surface, self.__rect)

    def draw_on(self, surface: Surface):
        """То же, что и blit_on, но доска будет нарисована только в случае если она успела измениться"""
        if self.__dirty:
            self.__dirty = False
            self.recache()
            self.redraw()
            surface.blit(self.__surface, self.__rect)
            return True
        return False

    # BOARD SCALING ###################
    def set_zoom_presets(self, presets: t.Tuple[float, ...]):
        """Устанавливает список преднастроенных значений увеличения"""
        prev = 0
        for p in presets:
            if p <= 0:
                raise ValueError("Zoom preset can't be equal or less than 0!")
            if p <= prev:
                raise ValueError("Presets must be sorted in descending order and can not repeat")
        self.__zoom_presets = presets

    def get_zoom_presets(self):
        """."""
        return self.__zoom_presets

    def zoom_in(self):
        """Устанавливливает увеличение на ближающую меньшую настройку не равную текущей"""
        for preset in self.__zoom_presets:
            if preset < self.__scale:
                self.__scale = preset
                break
        else:
            self.__scale = self.__zoom_presets[-1]
        self.set_flags_dirty(RLFLAG_SCALE_DEP)

    def zoom_out(self):
        """Устанавливливает увеличение на ближающую большую настройку не равную текущей"""
        for preset in reversed(self.__zoom_presets):
            if preset > self.__scale:
                self.__scale = preset
                break
        else:
            self.__scale = self.__zoom_presets[0]
        self.set_flags_dirty(RLFLAG_SCALE_DEP)

    def zoom_in_to(self, point: tVector2):
        """
        Приближает так, что указанная точка остаётся визуально неподвижной

        point: Vector2 - точка в глобальных координатах
        """
        # Находим локальные координаты точки и вектора то неё до центра видимой области
        target = self.to_local(point)
        vec = math2d.v_sub(target, self.__pos)
        # Сохраняем текущее значение увеличения
        scale = self.__scale
        # Увеличиваем (использует преднастройки, так что мы не можем точно знать какое будет увеличение)
        self.zoom_in()  # Already makes board dirty, so we don't need to do it here
        # Находим насколько увеличилось приближение и умножаем на это значение наш вектор
        n_vec = math2d.v_mul(vec, self.__scale / scale)
        self.__pos = math2d.v_sub(target, n_vec)  # Перемещаемся в рассчитанную позицию
        self.set_flags_dirty(RLFLAG_BOARD_MOVEMENT_DEP)

    def zoom_out_of(self, point: tVector2):
        """
        Отдаляет так, что указанная точка остаётся визуально неподвижной

        point: Vector2 - точка в глобальных координатах
        """
        target = self.to_local(point)
        vec = math2d.v_sub(target, self.__pos)
        scale = self.__scale
        self.zoom_out()  # Already makes board dirty, so we don't need to do it here
        n_vec = math2d.v_mul(vec, self.__scale / scale)
        self.__pos = math2d.v_sub(target, n_vec)
        self.set_flags_dirty(RLFLAG_BOARD_MOVEMENT_DEP)

    # BOARD MOVING ####################
    def move_by(self, rel: tIVector2):
        """."""
        self.__pos = math2d.v_add(self.__pos, rel)
        self.set_flags_dirty(RLFLAG_BOARD_MOVEMENT_DEP)

    def scroll_by(self, rel: tIVector2):
        """."""
        rel = math2d.v_mul(rel, self.__scale)
        rel = math2d.v_int(rel)
        self.__pos = math2d.v_add(self.__pos, rel)
        self.set_flags_dirty(RLFLAG_BOARD_MOVEMENT_DEP)

    def grab(self, point: tVector2) -> GrabData:
        """."""
        return GrabData(None, point, self.__pos)

    def drag(self, point: tVector2, gd: GrabData):
        """."""
        vec = math2d.v_sub(gd.gl_start, point)
        vec = math2d.v_mul(vec, self.__scale)
        self.__pos = math2d.v_add(gd.lc_start_pos, vec)
        self.set_flags_dirty(RLFLAG_BOARD_MOVEMENT_DEP)
    # #################################


def RL_BACKGROUND(board: Board, surface: Surface):
    """."""
    surface.fill(board.style["background"])


def RL_GRID_LINES(board: Board, surface: Surface):
    """."""
    if board.grid is None:
        return

    rect = board.get_rect()
    view_rect = board.get_view_rect()

    gx, gy = math2d.grid(view_rect.topleft, (board.grid, board.grid))
    if gy < view_rect.top:
        gy += board.grid
    if gx < view_rect.left:
        gx += board.grid

    while gx < view_rect.right:
        glx, _ = board.to_global((gx, 0))
        glx -= rect.x
        pygame.draw.line(
            surface,
            board.style["grid-color"],
            (glx, 0),
            (glx, surface.get_height())
        )
        gx += board.grid

    while gy < view_rect.bottom:
        _, gly = board.to_global((0, gy))
        gly -= rect.y
        pygame.draw.line(
            surface,
            board.style["grid-color"],
            (0, gly),
            (surface.get_width(), gly)
        )
        gy += board.grid


def RL_GRID_DOTS(board: Board, surface: Surface):
    """."""
    if board.grid is None:
        return

    rect = board.get_rect()
    view_rect = board.get_view_rect()

    gx, gy = math2d.grid(view_rect.topleft, (board.grid, board.grid))
    if gy < view_rect.top:
        gy += board.grid
    if gx < view_rect.left:
        gx += board.grid

    orig_gx = gx
    while gy < view_rect.bottom:
        _, gly = board.to_global((0, gy))
        gly -= rect.y

        while gx < view_rect.right:
            glx, _ = board.to_global((gx, 0))
            glx -= rect.x

            surface.set_at(math2d.v_int((glx, gly)), board.style["grid-color"])

            gx += board.grid

        gx = orig_gx
        gy += board.grid


def RL_OBJECT_RENDERER(board: Board, surface: Surface):
    """."""
    for obj in board.get_all():
        if board.is_visible(obj):
            gr = board.get_object_global_rect(obj)

            if board.scale > 1:
                img = pygame.transform.smoothscale(obj.original.image, gr.size)
            elif board.scale < 1:
                img = pygame.transform.scale(obj.original.image, gr.size)
            else:
                img = obj.original.image

            gr.x -= board.get_rect().x
            gr.y -= board.get_rect().y

            surface.blit(img, gr)


def RL_SELECTION(board: Board, surface: Surface):
    """."""
    for obj in board.get_all():
        if board.is_visible(obj) and obj.selected:
            gr = board.get_object_global_rect(obj)

            gr.x -= board.get_rect().x
            gr.y -= board.get_rect().y

            pygame.draw.rect(surface, board.style["selection"], gr, 1)


def RL_INDICATOR_DEFAULT(board: Board, surface: Surface):
    """."""
    def remove_zero(nam):
        """."""
        return int(nam) if float(nam).is_integer() else round(nam, 2)
    text_zoom_percent = str(int(100 / board.scale))
    text_scale1 = str(remove_zero(1 / board.scale) if board.scale < 1 else 1)
    text_scale2 = str(remove_zero(board.scale) if board.scale >= 1 else 1)

    font = pygame.font.SysFont(board.style["zoom_indicator-font"], board.style["zoom_indicator-font-size"])

    renders = [
        font.render(text_zoom_percent + '%', False, board.style["zoom_indicator-color"]),
        font.render(text_scale1 + ':' + text_scale2, False, board.style["zoom_indicator-color"]),
    ]

    interval = board.style["zoom_indicator-interval"]
    length = board.style["zoom_indicator-line-width"]
    width = board.style["zoom_indicator-width"]
    height = board.style["zoom_indicator-height"]

    indicator = Surface((width, height), pygame.SRCALPHA)
    indicator.fill((0, 0, 0, 0))

    # Линия
    pygame.draw.line(
        indicator,
        board.style["zoom_indicator-color"],
        (width // 2 - length // 2, height // 2),
        (width // 2 + length // 2, height // 2)
    )

    # Деления
    zoom_presets = board.get_zoom_presets()
    min_v, max_v = zoom_presets[-1], zoom_presets[0]
    for val in reversed(zoom_presets):
        x = (val - min_v) / (max_v - min_v) * length + width // 2 - length // 2
        pygame.draw.line(
            indicator,
            board.style["zoom_indicator-color"],
            (x, height // 2 - 2),
            (x, height // 2 + 2)
        )

    x = (1 - min_v) / (max_v - min_v) * length + width // 2 - length // 2
    pygame.draw.line(
        indicator,
        board.style["zoom_indicator-color"],
        (x, height // 2 - 3),
        (x, height // 2 + 3)
    )

    # Слайдер
    x = (board.scale - min_v) / (max_v - min_v) * length + width // 2 - length // 2
    pygame.draw.line(
        indicator,
        board.style["zoom_indicator-slider-color"],
        (x, height // 2 - 3),
        (x, height // 2 + 3),
        2
    )

    # Прибиваем текст
    rect = renders[0].get_rect()
    rect.midright = (width // 2 - length // 2 - interval, height // 2)
    indicator.blit(renders[0], rect)

    rect = renders[1].get_rect()
    rect.midleft = (width // 2 + length // 2 + interval, height // 2)
    indicator.blit(renders[1], rect)

    rect = indicator.get_rect()
    rect.bottomright = surface.get_rect().bottomright
    rect.x -= board.style["zoom_indicator-pads"][0]
    rect.y -= board.style["zoom_indicator-pads"][1]
    surface.blit(indicator, rect)
