"""."""
import typing as t

T_AND, T_OR, T_XOR, T_NOT, T_BO, T_BC, T_FALSE, T_TRUE, T_A, T_B, T_C, T_D, T_E, T_F = range(14)
TOKEN_TO_PYTHON = '&', '|', '^', '~', '(', ')', 'false', 'true', 'A', 'B', 'C', 'D', 'E', 'F'

# Вариации в которых могут встречаться части выражений
ALIASES: dict[str, tuple[str, ...]] = {
    T_AND: ('&', 'and', r'\land', r'\wedge', '*'),
    T_OR: ('|', 'or', r'\vee', '+', 'v'),
    T_XOR: ('^', 'xor', r'\oplus', '!='),
    T_NOT: ('~', 'not', r'\bar', '!'),
    T_BO: ('(', '{'),
    T_BC: (')', '}'),
    T_FALSE: ('0', 'False', 'false'),
    T_TRUE: ('1', 'True', 'true'),
    T_A: ('A', 'a'),
    T_B: ('B', 'b'),
    T_C: ('C', 'c'),
    T_D: ('D', 'd'),
    T_E: ('E', 'e'),
    T_F: ('F', 'f'),
}

# Перед/после каких токенов 'and' может не писаться (т.е. быть скрыто)
SKIPPED_AND_BEFORE = T_NOT, T_BO, T_A, T_B, T_C, T_D, T_E, T_F
SKIPPED_AND_AFTER = T_BC, T_A, T_B, T_C, T_D, T_E, T_F

# Токены по группам
VARIABLES = T_A, T_B, T_C, T_D, T_E, T_F
CONSTANTS = T_FALSE, T_TRUE
OPERANDS = VARIABLES + CONSTANTS
UNARY = T_NOT,
BINARY = T_AND, T_OR, T_XOR

# Приоритетные операции
FOREGROUND = T_AND,


def __get_token(expr: str):
    if expr[0].isspace():
        return None, 1
    for tok, aliases in ALIASES.items():
        for alias in aliases:
            if expr.startswith(alias):
                return tok, len(alias)
    raise ValueError('Invalid expression passed')


def tokenize(expression: str):
    """Преобразует строку в набор токенов"""
    left = expression
    may_be_skipped_and = False
    while len(left) > 0:
        tok, length = __get_token(left)
        left = left[length:]

        if tok is None:  # Skipping whitespace
            continue

        # Проверяем на возможность пропущенного 'and'
        if may_be_skipped_and and tok in SKIPPED_AND_BEFORE:
            yield T_AND
        may_be_skipped_and = False
        if tok in SKIPPED_AND_AFTER:
            may_be_skipped_and = True

        yield tok


def __polish(expr: str):
    """Преобразует выражение в польскую нотацию"""
    stack: list[int] = []

    for tok in tokenize(expr):
        if tok in OPERANDS:
            yield tok
        elif tok in UNARY:
            stack.append(tok)

        elif tok == T_BO:
            stack.append(T_BO)
        elif tok == T_BC:
            while (tok := stack.pop()) != T_BO:
                yield tok

        elif tok in BINARY:
            while len(stack) > 0 and (stack[-1] in UNARY or stack[-1] in FOREGROUND):
                yield stack.pop()
            stack.append(tok)

    while len(stack) > 0:
        yield stack.pop()


class Expression:
    """Объект олицетворяющий выражение"""
    def __init__(
            self,
            operation: int,
            operand_1: t.Union['Expression', 'Variable', 'Constant'],
            operand_2: t.Union['Expression', 'Variable', 'Constant'],
            inverted: bool = False
    ):
        self.__operation: int = operation
        self.__operand_1: t.Union[Expression, Variable, Constant] = operand_1
        self.__operand_2: t.Union[Expression, Variable, Constant] = operand_2
        self.__inverted: bool = inverted

    def __str__(self):
        first: str = ('{}', '({})')[isinstance(self.__operand_1, Expression) and self.__operand_1.operation not in FOREGROUND and self.__operation in FOREGROUND]
        second: str = ('{}', '({})')[isinstance(self.__operand_2, Expression) and self.__operand_2.operation not in FOREGROUND and self.__operation in FOREGROUND]
        pref = ('', '~')[self.__inverted]
        return ' '.join((
            first.format(str(self.__operand_1)),
            pref + TOKEN_TO_PYTHON[self.__operation],
            second.format(str(self.__operand_2))
        ))

    @property
    def operation(self):
        """."""
        return self.__operation

    @property
    def operand_1(self):
        """."""
        return self.__operand_1

    @property
    def operand_2(self):
        """."""
        return self.__operand_2

    @property
    def is_inverted(self):
        """Является ли значение операции инвертированным"""
        return self.__inverted

    def inverted(self):
        """Возвращает новое инвертированное выражение"""
        return Expression(self.__operation, self.__operand_1, self.__operand_2, not self.__inverted)


class Variable:
    """Часть выражений, вместо которой при решении подставляется конкретное значение"""
    def __init__(self, type_: int, inverted: bool = False):
        self.__type: int = type_
        self.__inverted: bool = inverted

    def __str__(self):
        return ('', '~')[self.__inverted] + TOKEN_TO_PYTHON[self.__type]

    @property
    def type(self):
        """Возвращает тип переменной в виде токена"""
        return self.__type

    @property
    def is_inverted(self):
        """Является ли значение переменной инвертированным"""
        return self.__inverted

    def inverted(self):
        """Возвращает новое инвертированное выражение"""
        return Variable(self.__type, not self.__inverted)


class Constant:
    """Часть выражений, олицетворяющая постоянное значение"""
    def __init__(self, value: bool):
        self.__value: bool = value

    def __str__(self):
        return TOKEN_TO_PYTHON[self.__value]

    @property
    def value(self):
        """Возвращает значение константы"""
        return self.__value

    def inverted(self):
        """Возвращает новое инвертированное выражение"""
        return Constant(not self.__value)


def to_structure(expr: str):
    """Преобразует логическое выражение в структуру"""
    stack: list[t.Union['Expression', 'Variable', 'Constant']] = []
    for tok in __polish(expr):
        if tok in VARIABLES:
            stack.append(Variable(tok))
        elif tok in CONSTANTS:
            stack.append(Constant(tok == T_TRUE))
        elif tok == T_NOT:
            stack.append(stack.pop().inverted())
        elif tok in BINARY:
            second, first = stack.pop(), stack.pop()
            stack.append(Expression(tok, first, second))
    if len(stack) > 1:
        raise ValueError('Invalid expression!')
    return stack.pop()


def to_string(expr):
    """Преобразует структуры и наборы токенов в строку. Удобно использовать для дебаггинга"""
    return ' '.join(TOKEN_TO_PYTHON[tok] for tok in expr)


if __name__ == '__main__':
    from sympy.abc import A, B, C, D, E, F
    from sympy.logic.boolalg import S
    scope = {'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F, 'false': S.false, 'true': S.true}
    string = r'(B|C&D)!A'
    print('ORIG:  ', string)
    print('TOKENS:', to_string(tokenize(string)))
    print('POLISH:', to_string(__polish(string)))
    print('STRUCT:', to_structure(string))
