"""Константы логического движка"""
TOK_AND, TOK_OR, TOK_CON, TOK_EQL, TOK_NEG, TOK_BRO, TOK_BRC, TOK_ZERO, TOK_ONE, TOK_A, TOK_B, TOK_C, TOK_D = range(13)

ALIASES = {
    TOK_AND: '&*^',
    TOK_OR: '+v',
    TOK_CON: '>',
    TOK_EQL: '=~',
    TOK_NEG: '!',
    TOK_BRO: '(',
    TOK_BRC: ')',
    TOK_ZERO: '0',
    TOK_ONE: '1',
    TOK_A: 'Aa',
    TOK_B: 'Bb',
    TOK_C: 'Cc',
    TOK_D: 'Dd'
}

VARIABLES = [TOK_A, TOK_B, TOK_C, TOK_D]
CONSTANTS = [TOK_ZERO, TOK_ONE]
BINARY_OPERATIONS = [TOK_EQL, TOK_CON, TOK_OR, TOK_AND]
UNARY_OPERATIONS = [TOK_NEG]

PRIORITIES = TOK_BRO, TOK_BRC, TOK_EQL, TOK_CON, TOK_OR, TOK_AND, TOK_NEG

