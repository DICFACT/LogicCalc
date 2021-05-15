"""работа с векторами"""


def mul(vec: tuple, val: float):
    """Умножает каждую координату вектора на указанное значение"""
    return tuple(map(lambda x: x * val, vec))


def imul(vec: tuple, val: float):
    """Умножает каждую координату вектора на указанное значение"""
    return tuple(map(lambda x: int(x * val), vec))
