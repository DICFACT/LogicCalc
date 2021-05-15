"""Логический процессор"""
import typing as t

from .const import ALIASES, VARIABLES, CONSTANTS, UNARY_OPERATIONS, TOK_BRO, TOK_BRC, BINARY_OPERATIONS, PRIORITIES, \
    TOK_ZERO, TOK_ONE, TOK_NEG, TOK_A, TOK_B, TOK_C, TOK_D, TOK_AND, TOK_OR, TOK_CON, TOK_EQL


class Node:
    """Класс узла логической схемы"""
    def __init__(self, type_: int, a: 'Node' = None, b: 'Node' = None, inv: bool = False):
        self.__type = type_
        self.__first = a
        self.__second = b
        self.__inverted = inv

    def __repr__(self):
        op = '&|  ~()01abcd'[self.__type]
        s1 = ' ' + self.__first.__repr__() if self.__first is not None else ''
        s2 = self.__second.__repr__() + ' ' if self.__second is not None else ''
        inv = '~' if self.__inverted else ''
        return f'{inv}({s2}{op}{s1})'

    @property
    def type(self):
        """Тип операции"""
        return self.__type

    @property
    def a(self):
        """Первый аргумент"""
        return self.__first

    @property
    def b(self):
        """Второй аргумент"""
        return self.__second

    @property
    def inverted(self):
        """Является ли операция инвертированной вариацией"""
        return self.__inverted


class LogicProcessor:
    """Логический процессор, делает за нас всю грязную работу"""
    @staticmethod
    def tokenized(exp: str):
        """Генератор токенов из строки"""
        for ch in exp:
            if ch.isspace():
                continue
            for tok, aliases in ALIASES.items():
                if ch in aliases:
                    yield tok
                    break
            else:
                raise ValueError(f'Character "{ch}" is not allowed in the equation!')

    @staticmethod
    def to_polish_notation(exp: str):
        """Преобразут выражение в польскую нотацию"""
        stack: t.List[int] = []
        for tok in LogicProcessor.tokenized(exp):
            if tok in VARIABLES + CONSTANTS:
                yield tok
            elif tok in UNARY_OPERATIONS:
                stack.append(tok)

            elif tok == TOK_BRO:
                stack.append(tok)
            elif tok == TOK_BRC:
                while (ct := stack.pop()) != TOK_BRO:
                    yield ct

            elif tok in BINARY_OPERATIONS:
                while len(stack) > 0 and (stack[-1] in UNARY_OPERATIONS or PRIORITIES.index(stack[-1]) >= PRIORITIES.index(tok)):
                    yield stack.pop()
                stack.append(tok)

        while len(stack) > 0:
            yield stack.pop()

    @staticmethod
    def to_structure(exp: str):
        """Преобразует выражение в структуру, состоящую из узлов"""
        stack: t.List[Node] = []
        for tok in LogicProcessor.to_polish_notation(exp):
            if tok in CONSTANTS + VARIABLES:
                stack.append(Node(tok))
            elif tok == TOK_NEG:
                node = stack.pop()
                stack.append(Node(node.type, node.a, node.b, not node.inverted))
            elif tok in BINARY_OPERATIONS:
                a, b = stack.pop(), stack.pop()
                stack.append(Node(tok, a, b))
        if len(stack) != 1:
            raise ValueError('Invalid expression passed!')
        return stack.pop()

    @staticmethod
    def execute(node: Node, a: bool, b: bool, c: bool, d: bool) -> bool:
        """Решает структуру для данных значений переменных"""
        res = True
        if node.type == TOK_AND:
            a_ = LogicProcessor.execute(node.a, a, b, c, d)
            b_ = LogicProcessor.execute(node.b, a, b, c, d)
            res = a_ and b_
        elif node.type == TOK_OR:
            a_ = LogicProcessor.execute(node.a, a, b, c, d)
            b_ = LogicProcessor.execute(node.b, a, b, c, d)
            res = a_ or b_
        elif node.type == TOK_CON:
            a_ = LogicProcessor.execute(node.a, a, b, c, d)
            b_ = LogicProcessor.execute(node.b, a, b, c, d)
            res = not a_ or b_
        elif node.type == TOK_EQL:
            a_ = LogicProcessor.execute(node.a, a, b, c, d)
            b_ = LogicProcessor.execute(node.b, a, b, c, d)
            res = a_ == b_
        elif node.type == TOK_ZERO:
            res = False
        elif node.type == TOK_ONE:
            res = True
        elif node.type in VARIABLES:
            res = {TOK_A: a, TOK_B: b, TOK_C: c, TOK_D: d}[node.type]
        if node.inverted:
            res = not res
        return res
