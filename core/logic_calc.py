"""Файл класса LogicCalc"""
from time import time

import pygame

from core import const
from core.classes.project import Scheme
from core.gui_system import GUISystem
from core.project_manager import ProjectManager
from resource_loader import ResourceLoader


class LogicCalc:
    """Главный класс приложения"""
    def __init__(self):
        self.__clock: pygame.time.Clock = pygame.time.Clock()
        self.__closed: bool = False

    def __setup(self):
        print('Initializing graphical components...')
        time_start = time()
        import core.gui.tool_bar_gui
        import core.gui.project_tab_bar_gui
        import core.gui.info_bar_gui
        print(f'Initialization complete: {(time() - time_start) * 1000}ms')

        GUISystem.initialize()
        ResourceLoader.load()
        GUISystem.setup()

        ProjectManager.new_project('First test')
        ProjectManager.selected_project.add_scheme(
            Scheme.from_string(ProjectManager.selected_project, '!(A or !B)'))
        ProjectManager.selected_project.add_scheme(
            Scheme.from_string(ProjectManager.selected_project, '0 xor ((!A or 1) and 1)'))
        ProjectManager.selected_project.add_scheme(
            Scheme.from_string(ProjectManager.selected_project, '(A or B) * !(C xor D)'))

        ProjectManager.new_project('Second test')
        ProjectManager.selected_project.add_scheme(
            Scheme.from_string(ProjectManager.selected_project, '(A or B) * C xor !D'))
        ProjectManager.selected_project.add_scheme(
            Scheme.from_string(ProjectManager.selected_project, '(A or B) * C xor !D'))

        print(f"Setup done in {(time() - time_start) * 1000}ms")

    def __update(self):
        GUISystem.update()

    def __handle(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            self.close()
        GUISystem.handle(event)

    # OPEN/CLOSE ##########################################

    def close(self):
        """Завершает выполнение программы"""
        self.__closed = True

    def run(self):
        """Запускает программу на исполнение"""
        self.__setup()
        while not self.__closed:
            for event in pygame.event.get():
                self.__handle(event)
            self.__update()
            self.__clock.tick(const.FPS)
            pygame.display.set_caption(const.CAPTION.format(
                FPS=round(self.__clock.get_fps())
            ))


LogicCalc: LogicCalc = LogicCalc()
