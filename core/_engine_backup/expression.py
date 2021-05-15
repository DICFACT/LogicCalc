"""."""
from sympy import abc


class Expression:
    """Basic class for all expression parts"""

    def __init__(self, type_: int):
        self.__type: int = type_

    def __repr__(self):
        return ''

    def calculate(self, values):
        """."""
        eval(self.__repr__(), {
            'A': abc.A,
            'B': abc.B,
            'C': abc.C,
            'D': abc.D
        }).subs(values)


class Variable(Expression):
    """."""

    def __init__(self):
        pass
