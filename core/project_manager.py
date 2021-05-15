"""Файл класса ProjectManager"""
import typing as t

from core.classes.project import Project, Scheme
from core.utils.event import Event


class ProjectManager:
    """Менеджер проектов"""

    def __init__(self):
        self.new_project_event = Event()
        self.open_project_event = Event()

        self.__projects: dict[int, Project] = {}
        self.order: list[int] = []
        self.selected: t.Optional[int] = None

    # PROPERTIES, GETTERS AND SETTERS #####################

    @property
    def projects(self):
        """Итератор загруженных проектов"""
        return (self.__projects[id_] for id_ in self.order)

    @property
    def selected_project(self):
        """Выделенный проект"""
        try:
            return self.__projects[self.selected]
        except IndexError:
            return None

    # PROJECT SELECTION ###################################

    def deselect_project(self):
        """Снимает выделение с какого-либо проекта"""
        self.selected = None

    def select_project_by_id(self, id_: int):
        """Выделяет проект по идентификатору"""
        if id_ not in self.__projects:
            self.selected = None
            return
        self.selected = id_

    def select_project_by_index(self, index: int):
        """Выделяет проект по индексу в order"""
        if not(0 <= index < len(self.__projects)):
            self.selected = None
        self.selected = self.order[index]

    # OPENING/CLOSING PROJECTS ############################

    def new_project(self, name: str) -> Project:
        """Создаёт новый проект"""
        project = Project()
        project.name = name
        self.__projects[project.id] = project
        self.order.append(project.id)
        self.selected = project.id

        self.new_project_event.invoke(project)
        return project

    def open_project(self, path: str) -> Project:
        """Загружает проект из файла"""
        pass

    def save_project(self, path: str):
        """Сохраняет проект в файл"""
        pass

    def close_project(self, id_: int):
        """Закрывает проект"""
        pass


ProjectManager: ProjectManager = ProjectManager()

# project.add_expression('(A or B) * C xor !D')  # Default content
# project.add_expression('(A or B) * !(C xor D)')
