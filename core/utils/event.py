"""Файл класса Event"""
import inspect
import typing as t


# def bugged_method(function):
#     """Декоратор, позволяющий привязывать дополнительную логику к вызову функции"""
#     class __Wrapper:
#         def __init__(self, func):
#             self.__func = func
#             self.__listeners = []
#
#         def __call__(self, *args, **kwargs):
#             res = self.__func(self, *args, **kwargs)
#             for listener in self.__listeners:
#                 listener(res)
#
#         def attach(self, func):
#             """Добавляет слушателя к вызову метода"""
#             self.__listeners.append(func)
#
#         def detach(self, func):
#             """Удаляет слушателя"""
#             self.__listeners.remove(func)
#
#     return __Wrapper(function)


# class BuggedMethod:
#     """Декоратор, позволяющий привязывать дополнительную логику к вызову функции"""
#
#     def __init__(self, function):
#         self.__func = function
#         self.__listeners = []
#
#     def __call__(self, *args, **kwargs):
#         print(inspect.signature(self.__func).parameters['self'].kind)
#         res = self.__func(*args, **kwargs)
#         for listener in self.__listeners:
#             listener(res)
#
#     def attach(self, func):
#         """Добавляет слушателя к вызову метода"""
#         self.__listeners.append(func)
#
#     def detach(self, func):
#         """Удаляет слушателя"""
#         self.__listeners.remove(func)


class Event:
    """..."""

    def __init__(self):
        self.__listeners = []

    def invoke(self, *args, **kwargs):
        """..."""
        for listener in self.__listeners:
            listener(*args, **kwargs)

    def attach(self, func):
        """Добавляет слушателя к вызову метода"""
        self.__listeners.append(func)

    def detach(self, func):
        """Удаляет слушателя"""
        self.__listeners.remove(func)
