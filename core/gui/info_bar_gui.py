"""Файл класса InfoBarGUI"""
import pygame
import sympy

from core import style
from core.classes.project import Project, Scheme
from core.gui.gui_element import GUIElement
from core.gui_system import GUISystem
from core.project_manager import ProjectManager
from core.utils.draw_expr import draw_expr, draw_tt
from core.utils.event import Event
from core.utils.rect import in_bounds


class Viewer:
    """Панель для отображения выражений в проекте"""
    def __init__(self):
        self.select_expression_event = Event()

        self.__content: pygame.Surface = pygame.Surface((1, 1))
        self.__struct_images: dict[int, pygame.Surface] = {}

    def __new_expr_listener(self):
        for expr in ProjectManager.selected_project.schemes:
            if expr.id not in self.__struct_images:
                self.__struct_images[expr.id] = draw_expr(expr.struct)

    def __new_project_listener(self, project: Project):
        project.add_scheme_event.attach(self.__new_expr_listener)

    def setup(self):
        """..."""
        _, _, width, height = style.get('.infobar-page-viewer', 'rect')
        self.__content = pygame.Surface((width, height))

        ProjectManager.new_project_event.attach(self.__new_project_listener)

    def update(self):
        """..."""
        self.__content.fill(style.get('.infobar-page-viewer', 'background'))

        indent, _, _, _ = style.get('.viewer-item', 'rect')

        for id_, rect in style.sequence('.viewer-items', of=ProjectManager.selected_project.order):
            x, y, w, h = rect
            sub = ProjectManager.selected_project.get(id_).sub
            style.blit_button(self.__content, '.viewer-item', rect=(x + sub * indent, y, w - sub * indent, h), sel=ProjectManager.selected_project.selected == id_)
            img_rect: pygame.Rect = self.__struct_images[id_].get_rect()
            img_rect.centery = y + h // 2
            img_rect.x = style.get('.viewer-item', 'indent')
            self.__content.blit(self.__struct_images[id_], img_rect)

        style.blit_block(self.__content, '.viewer-sidebar')

        style.blit_block(self.__content, '.viewer-sidebar-add')

        return self.__content

    def handle(self, event):
        """..."""
        vx, vy, _, _ = style.get('.infobar-page-viewer', 'rect')
        for id_, rect in style.sequence('.viewer-items', of=ProjectManager.selected_project.order):
            x, y, w, h = rect
            if in_bounds((x + vx, y + vy, w, h), event.pos):
                ProjectManager.selected_project.selected = id_
                self.select_expression_event.invoke()
                return True

        x, y, w, h = style.get('.viewer-sidebar-add', 'rect')
        if in_bounds((x + vx, y + vy, w, h), event.pos):
            try:
                val = GUISystem.get_value()
                scheme = Scheme.from_string(ProjectManager.selected_project, val)
            except ValueError:
                pass
            else:
                ProjectManager.selected_project.add_scheme(scheme)


class TruthTable:
    """..."""

    def __init__(self):
        self.__content: pygame.Surface = pygame.Surface((1, 1))
        self.__tt_images: dict[int, pygame.Surface] = {}

    def __new_expr_listener(self):
        for expr in ProjectManager.selected_project.schemes:
            if expr.id not in self.__tt_images:
                self.__tt_images[expr.id] = draw_tt(expr.symbol)

    def __new_project_listener(self, project: Project):
        project.add_scheme_event.attach(self.__new_expr_listener)

    def setup(self):
        """..."""
        _, _, width, height = style.get('.infobar-page-tt', 'rect')
        self.__content = pygame.Surface((width, height))

        ProjectManager.new_project_event.attach(self.__new_project_listener)

    def update(self):
        """..."""
        self.__content.fill(style.get('.infobar-page-tt', 'background'))

        self.__content.blit(self.__tt_images[ProjectManager.selected_project.selected], (0, 0))

        return self.__content


class InfoBarGUI(GUIElement):
    """Static class."""

    def __init__(self):
        super(InfoBarGUI, self).__init__()
        self.__open_tab = 0
        self.__viewer = Viewer()
        self.__truth_table = TruthTable()

    def _setup(self):
        self.__viewer.setup()
        self.__truth_table.setup()

    def _update(self):
        screen = pygame.display.get_surface()
        cursor = pygame.mouse.get_pos()

        style.draw_block('.infobar')

        for i, rect in style.sequence('.infobar-tabs', of=range(1)):
            style.draw_button('.infobar-tabs-expr', rect, sel=i == self.__open_tab)

        style.draw_block('.infobar-page')

        x, y, _, _ = style.get('.infobar-page-viewer', 'rect')
        screen.blit(self.__viewer.update(), (x, y))
        pygame.draw.rect(
            screen,
            style.get('.infobar-page-viewer', 'outline'),
            style.get('.infobar-page-viewer', 'rect'), 1
        )

        x, y, _, _ = style.get('.infobar-page-tt', 'rect')
        screen.blit(self.__truth_table.update(), (x, y))
        pygame.draw.rect(
            screen,
            style.get('.infobar-page-tt', 'outline'),
            style.get('.infobar-page-tt', 'rect'), 1
        )

        style.draw_button('.infobar-page-simplify')

        pygame.display.update(style.get('.infobar', 'rect'))

    def _handle(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.__viewer.handle(event):
                return True

            if in_bounds(style.get('.infobar-page-simplify', 'rect'), event.pos):
                scheme = ProjectManager.selected_project.selected_scheme
                res = sympy.to_dnf(scheme.symbol, simplify=True)

                index = ProjectManager.selected_project.order.index(ProjectManager.selected_project.selected)
                index += 1
                if index == len(ProjectManager.selected_project.order):
                    index = None
                simplified = Scheme.from_string(ProjectManager.selected_project, str(res))
                simplified.sub = True

                ProjectManager.selected_project.add_scheme(simplified, index=index)

    def get_viewer(self):
        """..."""
        return self.__viewer


InfoBarGUI = InfoBarGUI()
