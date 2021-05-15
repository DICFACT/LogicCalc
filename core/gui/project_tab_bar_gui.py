"""Файл класса ProjectTabBar"""
import pygame

from core import style
from core.classes.board import Board, DEFAULT_STYLE
from core.classes.project import Project
from core.engine.processor import T_A, T_B, T_C, T_D, T_E, T_F, T_AND, T_OR, T_XOR
from core.gui.gui_element import GUIElement
from core.gui.info_bar_gui import InfoBarGUI
from core.project_manager import ProjectManager
from core.utils import color
from core.utils.draw_expr import draw_scheme
from core.utils.rect import in_bounds


# TODO: Исправить, что если ни одного проекта не выделено программа вылетает


# Token to name in style
CONST_MAPPING = {True: '1', False: '0'}
VAR_MAPPING = {T_A: 'a', T_B: 'b', T_C: 'c', T_D: 'd', T_E: 'e', T_F: 'f'}
OP_MAPPING = {T_AND: 'and', T_OR: 'or', T_XOR: 'xor'}
OFFSET = 96, 48


class BoardImage:
    """..."""
    def __init__(self, image: pygame.Surface):
        self.image = image


class ProjectTabBarGUI(GUIElement):
    """Static class."""

    def __init__(self):
        super(ProjectTabBarGUI, self).__init__()
        self.__boards: dict[int, Board] = {}
        self.__board_gd = None

        self.__loaded: list[int] = []
        self.__schemes: dict[int, BoardImage] = {}

    def __new_project_listener(self, project: Project):
        """Этот listener выполняется при создании нового проекта"""

        # Привязываем listener к добавленному проекту
        project.add_scheme_event.attach(self.__new_expr_listener)

        # Создаём класс доски под проект
        rect = style.get('.projectbar-page-board', 'rect')
        background = style.get('.projectbar-page-board', 'background')
        grid = style.get('.projectbar-page-board', 'grid')
        grid_size = style.get('.projectbar-page-board', 'grid-size')
        self.__boards[project.id] = Board(
            rect,
            style=DEFAULT_STYLE.update({
                'background': color.int_to_tuple(background),
                'grid-color': color.int_to_tuple(grid)
            }),
            grid=grid_size
        )

    def __new_expr_listener(self):
        """Этот listener выполняется при добавлении в проект выражения"""
        # На текущий момент поддерживаем только одно выражение на проект
        # в будущем метод которым блоки помещаются на доску должен будет измениться

        for expr in ProjectManager.selected_project.schemes:
            if expr.id not in self.__loaded:
                self.__schemes[expr.id] = BoardImage(draw_scheme(expr.struct))

        self.__show_selected()

        # image = draw_scheme(struct)
        # if project.id not in self.__schemes:
        #     self.__schemes[project.id] = []
        # self.__schemes[project.id].append(BoardImage(image))

    def __expr_selected_listener(self):
        self.__show_selected()

    def __show_selected(self):
        self.__boards[ProjectManager.selected].remove_rule(lambda _: True)
        scheme_id = ProjectManager.selected_project.selected_scheme.id
        self.__boards[ProjectManager.selected].add(self.__schemes[scheme_id], (0, 0))

    def _setup(self):
        ProjectManager.new_project_event.attach(self.__new_project_listener)
        ProjectManager.open_project_event.attach(self.__new_project_listener)
        InfoBarGUI.get_viewer().select_expression_event.attach(self.__expr_selected_listener)
        # InfoBarGUI.get_viewer().item_selected_event.attach(self.__expr_selected_listener)

    def _update(self):
        screen = pygame.display.get_surface()

        style.draw_block('.projectbar')

        # Отрисовка вкладок
        for item, rect in style.sequence('.projectbar-tabs', of=ProjectManager.order):
            style.draw_button('.projectbar-tabs-tab', rect=rect, sel=item == ProjectManager.selected)

        style.draw_block('.projectbar-page')

        # Отрисовка доски
        self.__boards[ProjectManager.selected].blit_on(screen)
        board = style.get_element('.projectbar-page-board')
        pygame.draw.rect(screen, board.get('outline'), board.get('rect'), 1)

        pygame.display.update(style.get('.projectbar', 'rect'))

    def _handle(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:

            # Нажатие на вкладку
            for id_, rect in style.sequence('.projectbar-tabs', of=ProjectManager.order):
                if in_bounds(rect, event.pos):
                    ProjectManager.selected = id_
                    return True

            # Далее обработка кликов по доске
            on_board = in_bounds(style.get('.projectbar-page-board', 'rect'), event.pos)

            if on_board and event.button == pygame.BUTTON_LEFT:
                self.__board_gd = self.__boards[ProjectManager.selected].grab(event.pos)
                return True

            if on_board and event.button == pygame.BUTTON_WHEELUP:
                self.__boards[ProjectManager.selected].zoom_in_to(event.pos)
                return True

            if on_board and event.button == pygame.BUTTON_WHEELDOWN:
                self.__boards[ProjectManager.selected].zoom_out_of(event.pos)
                return True

        # Перемещение мыши по доске
        if event.type == pygame.MOUSEMOTION and self.__board_gd is not None:
            self.__boards[ProjectManager.selected].drag(event.pos, self.__board_gd)
            return True

        # Кнопка мыши поднята
        if event.type == pygame.MOUSEBUTTONUP:
            self.__board_gd = None
            return False  # Возвращаем False т.к. другим компонентам тоже может быть необходимо обработать это событие


ProjectTabBarGUI: ProjectTabBarGUI = ProjectTabBarGUI()
