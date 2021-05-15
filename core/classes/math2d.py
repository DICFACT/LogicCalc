from .types_ import tVector, tVector2, tIVector2


# #### REAL MATH #### #
def clamp(value: float, minimum: float, maximum: float):
    return max(minimum, min(value, maximum))


def lerp(start: float, finish: float, t):
    t = clamp(t, 0, 1)
    return (finish - start) * t + start
# #### ######### #### #


# #### VECTORS #### #
def v_mul(vec: tVector, n: float):
    res = []
    for vx in vec:
        res.append(vx * n)
    return tuple(res)


def v_neg(vec: tVector):
    return v_mul(vec, -1)


def v_add(vec1: tVector, vec2: tVector):
    res = []
    for vx1, vx2 in zip(vec1, vec2):
        res.append(vx1 + vx2)
    return tuple(res)


def v_sub(vec1: tVector, vec2: tVector):
    res = []
    for vx1, vx2 in zip(vec1, vec2):
        res.append(vx1 - vx2)
    return tuple(res)
# #### ####### #### #


# #### HANDY MATH(ish) STUFF #### #
def tile(pos: tIVector2, res: tIVector2):
    """Tile coordinates by position on grid"""
    return pos[0] * res[0], pos[1] * res[1]


def grid(pos: tVector2, res: tIVector2):
    """Координаты объекта, прилепленные к сетке"""
    return int(pos[0] / res[0]) * res[0], int(pos[1] / res[1]) * res[1]


def v_int(vec: tVector):
    res = []
    for vx in vec:
        res.append(int(vx))
    return tuple(res)


def is_color(color: tVector):
    return len(color) == 3 and\
        color[0] is int and 0 <= color[0] <= 255 and\
        color[1] is int and 0 <= color[1] <= 255 and\
        color[2] is int and 0 <= color[2] <= 255
# #### ##################### #### #
