"""Файл класса Project"""
from uuid import uuid4
import typing as t

from sympy import S, abc, Symbol

from core.engine import processor
from core.engine.processor import TOKEN_TO_PYTHON, tokenize
from core.utils.draw_expr import t_Expr, calculate_tt
from core.utils.event import Event

SCOPE = {'true': S.true, 'false': S.false, 'A': abc.A, 'B': abc.B, 'C': abc.C, 'D': abc.D, 'E': abc.E, 'F': abc.F}


class Scheme:
    """Класс представляющий логическое выражение"""

    def __init__(self, owner, symbol, struct):
        self.__id: int = uuid4().int
        self.__owner = owner
        self.__symbol: Symbol = symbol
        self.__struct: t_Expr = struct
        self.sub = False

        # Calculating some handy stuff
        self.__truth_table = self.__calculate_tt()

    def __calculate_tt(self) -> list[int]:
        pass  # Use sympy magic here

    @property
    def id(self):
        """Идентификатор схемы"""
        return self.__id

    @property
    def owner(self):
        """Проект, содержащий схему"""
        return self.__owner

    @property
    def symbol(self):
        """Представление выражения в формате, поддерживаемом sympy"""
        return self.__symbol

    @property
    def struct(self):
        """Представление выражения в виде дерева"""
        return self.__struct

    def simplify(self):
        """Упрощённое sympy-ем выражение, возвращает Symbol"""
        pass  # Here goes sympy magic

    @staticmethod
    def from_string(owner, string: str):
        """Собирает схему из строки"""
        struct = processor.to_structure(string)
        symbol = eval(''.join(TOKEN_TO_PYTHON[tok] for tok in tokenize(string)), SCOPE)
        return Scheme(owner, symbol, struct)


class Project:
    """Класс представляющий проект (набор выражений)"""

    def __init__(self):
        self.add_scheme_event = Event()
        self.__id: int = uuid4().int
        self.name: str = ''
        self.__schemes: dict[int, Scheme] = {}
        self.order: list[int] = []
        self.selected: t.Optional[int] = None

    # PROPERTIES, GETTERS AND SETTERS #####################

    @property
    def id(self):
        """Идентификатор проекта"""
        return self.__id

    @property
    def schemes(self):
        """Итератор выражений загруженных в проект"""
        return (self.__schemes[id_] for id_ in self.order)

    @property
    def selected_scheme(self):
        """Возвращает выделенное выражение или None если такого нет"""
        try:
            return self.__schemes[self.selected]
        except IndexError:
            return None

    def get(self, id_: int):
        """..."""
        return self.__schemes[id_]

    # SCHEME SELECTION ####################################

    def deselect_scheme(self):
        """Снимает выделение с любого выражения"""
        self.selected = None

    def select_scheme_by_id(self, id_: int):
        """Выделяет схему по идетификатору"""
        if id_ not in self.__schemes:
            self.selected = None
            return
        self.selected = id_

    def select_scheme_by_index(self, index: int):
        """Выделяет выражение по индексу в order"""
        if not (0 <= index < len(self.__schemes)):
            self.selected = None
        self.selected = self.order[index]

    # SCHEMES MANIPULATION ################################

    def add_scheme(self, scheme: Scheme, index: int = None):
        """Загружает выражение в проект"""
        self.__schemes[scheme.id] = scheme
        if index:
            self.order.insert(index, scheme.id)
        else:
            self.order.append(scheme.id)
        self.selected = scheme.id
        self.add_scheme_event.invoke()

    def remove_scheme(self, scheme: Scheme):
        """Удаляет схему из проекта"""
        del self.__schemes[scheme.id]
        self.order.remove(scheme.id)
        if self.selected == scheme.id:
            self.selected = None
