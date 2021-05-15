"""..."""
import itertools
import typing as t

import pygame
import sympy
from pygame import Surface

from core import style
from core.engine.processor import Expression, Variable, Constant, T_AND, to_structure

pygame.init()

t_Expr = t.Union[Expression, Variable, Constant]


def draw_scheme(expression: t_Expr):
    """Возвращает изображение выражения в виде схемы"""
    _, _, block_width, block_height = style.get('.board-gates', 'item-rect')
    pad_x, pad_y = style.get('.board-gates', 'shift')
    color = style.get('.board-gates-and', 'outline')
    shift = 10

    def __draw_line(surface: Surface, pos1: (int, int), pos2: (int, int)):
        x1, y1 = pos1
        x2, y2 = pos2
        pygame.draw.line(surface, color, (x1, y1), (x1 - shift, y1), 2)
        pygame.draw.line(surface, color, (x2, y2), (x2 + shift, y2), 2)
        pygame.draw.line(surface, color, (x1 - shift, y1), (x2 + shift, y2), 2)

    def __draw_block(surface: Surface, element: str, rect: (int, int, int, int)):
        style.blit_button(surface, element, rect)

    def __draw_block_constant(surface: Surface, expr: Constant, x: int, y: int):
        element = f'.board-gates-{style.CONSTANT_MAPPING[expr.value]}'
        __draw_block(surface, element, (x, y, block_width, block_height))

    def __draw_block_variable(surface: Surface, expr: Variable, x: int, y: int):
        element = f'.board-gates-{style.VARIABLE_MAPPING[(expr.type, expr.is_inverted)]}'
        __draw_block(surface, element, (x, y, block_width, block_height))

    def __draw_block_operation(surface: Surface, expr: Expression, x: int, y: int):
        element = f'.board-gates-{style.OPERATION_MAPPING[(expr.operation, expr.is_inverted)]}'
        __draw_block(surface, element, (x, y, block_width, block_height))

    def __draw_scheme(surface: t.Optional[Surface], expr: t_Expr, x: int, y: int):
        if type(expr) is Constant:
            if surface:
                __draw_block_constant(surface, expr, x, y)
            return block_width, block_height

        if type(expr) is Variable:
            if surface:
                __draw_block_variable(surface, expr, x, y)
            return block_width, block_height

        if surface:
            __draw_line(surface, (x, y + block_height // 3), (x - pad_x, y + block_height // 2))
        width1, height1 = __draw_scheme(surface, expr.operand_1, x - block_width - pad_x, y)

        if surface:
            __draw_line(surface, (x, y + block_height * 2 // 3), (x - pad_x, y + height1 + pad_y + block_height // 2))
        width2, height2 = __draw_scheme(surface, expr.operand_2, x - block_width - pad_x, y + height1 + pad_y)

        if surface:
            __draw_block_operation(surface, expr, x, y)

        return block_width + pad_x + max(width1, width2), height1 + pad_y + height2

    size = __draw_scheme(None, expression, 0, 0)
    result = Surface(size)
    result.fill(style.get('.projectbar-page-board', 'background'))
    result.set_colorkey(style.get('.projectbar-page-board', 'background'))
    __draw_scheme(result, expression, size[0] - block_width, 0)
    return result


def draw_expr(expression: t_Expr, brackets_everywhere: bool = False):
    """Возвращает изображение выражения в математическом виде"""
    bar_height = style.get('.viewer-expression', 'bar')
    font: pygame.font.Font = style.get('.viewer-expression', 'font')
    color = style.get('.viewer-expression', 'font-color')

    interval = style.get('.viewer-expression', 'font-spacing')

    def __priority(operation: int):
        return int(operation == T_AND)

    def __draw_bar(surface: Surface, width: int, height: int, x: int, y: int):
        img = Surface((width, 1))
        img.fill(color)
        surface.blit(img, (x, y - height - bar_height))

    def __draw_symbol(surface: t.Optional[Surface], symbol: str, x: int, y: int):
        img = font.render(symbol, True, color << 8)
        rect = img.get_rect()
        if surface:
            rect.bottomleft = x, y
            surface.blit(img, rect)
        return rect.size

    def __draw_constant(surface: t.Optional[Surface], expr: Constant, x: int, y: int) -> (int, int):
        return __draw_symbol(surface, style.EXPR_CONSTANT_MAPPING[expr.value], x, y)

    def __draw_variable(surface: t.Optional[Surface], expr: Variable, x: int, y: int) -> (int, int):
        return __draw_symbol(surface, style.EXPR_VARIABLE_MAPPING[expr.type], x, y)

    def __draw_operation(surface: t.Optional[Surface], expr: Expression, x: int, y: int) -> (int, int):
        return __draw_symbol(surface, style.EXPR_OPERATION_MAPPING[expr.operation], x, y)

    def __draw_open_bracket(surface: t.Optional[Surface], x: int, y: int) -> (int, int):
        return __draw_symbol(surface, style.EXPR_BRACKETS[0], x, y)

    def __draw_close_bracket(surface: t.Optional[Surface], x: int, y: int) -> (int, int):
        return __draw_symbol(surface, style.EXPR_BRACKETS[1], x, y)

    def __draw_expr(surface: t.Optional[Surface], expr: t_Expr, x: int, y: int, brackets: bool):
        if type(expr) is Constant:
            width, height = __draw_constant(surface, expr, x, y)
            return width, height

        if type(expr) is Variable:
            width, height = __draw_variable(surface, expr, x, y)
            if expr.is_inverted and surface:
                __draw_bar(surface, width, height, x, y)
            return width, height + bar_height * expr.is_inverted

        total = 0

        ob_height = 0
        if brackets:
            width, ob_height = __draw_open_bracket(surface, x, y)
            total += width

        needs_brackets = brackets_everywhere or type(expr.operand_1) is Expression and __priority(expr.operation) > __priority(expr.operand_1.operation)
        width1, height1 = __draw_expr(surface, expr.operand_1, x + total, y, needs_brackets)
        total += width1 + interval

        width, op_height = __draw_operation(surface, expr, x + total, y)
        total += width + interval

        needs_brackets = brackets_everywhere or type(expr.operand_1) is Expression and __priority(expr.operation) > __priority(expr.operand_1.operation)
        width2, height2 = __draw_expr(surface, expr.operand_2, x + total, y, needs_brackets)
        total += width2

        oc_height = 0
        if brackets:
            width, oc_height = __draw_close_bracket(surface, x + total, y)
            total += width

        height = max(ob_height, height1, op_height, height2, oc_height)

        if expr.is_inverted and surface:
            __draw_bar(surface, total, height, x, y)

        return total, height + bar_height * expr.is_inverted

    size = __draw_expr(None, expression, 0, 0, False)
    result = Surface(size, pygame.SRCALPHA)
    __draw_expr(result, expression, 0, size[1], False)
    return result


def calculate_tt(expr: sympy.Symbol):
    """..."""
    from sympy.utilities.iterables import cartes
    variables = tuple(expr.free_symbols)
    truth_table = []
    for truth_values in cartes([False, True], repeat=len(variables)):
        values = dict(zip(variables, truth_values))
        truth_table.append(expr.subs(values))
    return variables, truth_table


def draw_tt(expr: sympy.Symbol):
    """..."""
    font: pygame.font.Font = style.get('.tt-font', 'font')
    color = style.get('.tt-font', 'font-color')
    background = style.get('.tt-item', 'background')
    indent, _, cell_width, _ = style.get('.tt-item', 'rect')
    _, _, width, height = style.get('.infobar-page-tt', 'rect')
    _, sy = style.get('.tt-items', 'shift')

    variables, truth_table = calculate_tt(expr)

    result = Surface((width, height), pygame.SRCALPHA)

    back = Surface((width, (len(truth_table) + 1) * sy))
    back.fill(background)
    result.blit(back, (0, 0))

    for i, var in enumerate(variables + ('RES', )):
        letter = font.render(str(var), True, color << 8)
        result.blit(letter, (indent + i * cell_width, 0))

    # lts = {
    #     '0': font.render('0', True, color << 8),
    #     '1': font.render('1', True, color << 8)
    # }

    lts = {
        '0': style.get('.tt-false', 'icon'),
        '1': style.get('.tt-true', 'icon')
    }
    ix, iy, _, _ = style.get('.tt-false', 'icon-rect')

    for i, res in enumerate(truth_table):
        for j, char in enumerate(bin((i << 1) + bool(res))[2:].zfill(len(variables) + 1)):
            result.blit(lts[char], (indent + ix + j * cell_width, iy + (i + 1) * sy))

    return result
