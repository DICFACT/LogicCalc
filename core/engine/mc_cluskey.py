"""..."""
import math


class Term:
    """..."""
    def __init__(self, form, indexes):
        self.form = form
        if isinstance(indexes, set):
            self.indexes = indexes
        else:
            self.indexes = {indexes}
        self.combinable = False


def set_cover(universe, terms):
    """..."""
    subsets = []
    for term in terms:
        subsets.append(term.indexes)

    covered = set()
    cover = []
    # Greedily add the subsets with the most uncovered points
    while len(universe - covered) > 0:
        subset = min(subsets, key=lambda s: len(universe - covered - s))
        cover.append(subset)
        covered |= subset

    result = []
    for s in cover:
        for term in terms:
            if term.indexes == s:
                result.append(term)
                break

    return result


def tokenize_terms(terms):
    """..."""
    tokens = []
    for term in terms:
        for i in range(len(term.form)):
            if term.form[i] == '1':
                tokens.append(8 + i)
            elif term.form[i] == '0':
                tokens.append(3)
                tokens.append(8 + i)
        tokens.append(1)
    tokens.pop()

    return tokens


def get_pdnf(vector):
    """..."""
    length = len(vector)
    format_string = "{0:0" + str(int(math.log(length, 2))) + "b}"
    terms = []
    for i in range(length):
        if str(vector[i]) != '0':
            terms.append(Term(list(format_string.format(i)), i))
    return terms


def combine(term1, term2):
    """..."""
    index = -1
    length = len(term1.form)
    for i in range(length):
        if term1.form[i] != term2.form[i]:
            if index == -1:
                index = i
            else:
                return None

    form = list.copy(term1.form)
    form[index] = '-'
    indexes = set.union(term1.indexes, term2.indexes)
    return Term(form, indexes)


def get_mdnf(vector):
    """..."""
    if 1 not in vector and '1' not in vector:
        return [6]
    elif 0 not in vector and '0' not in vector:
        return [7]

    not_combinable = []
    need_to_cover = set()
    for i in range(len(vector)):
        if str(vector[i]) == '1':
            need_to_cover.add(i)

    terms = get_pdnf(vector)

    i = 0
    new_terms = []
    while len(terms) > 0:
        new_terms = []
        length = len(terms)
        for i in range(length - 1):
            j = i + 1
            while j < length:
                term = combine(terms[i], terms[j])
                if term is not None:
                    new_terms.append(term)
                    terms[i].combinable = True
                    terms[j].combinable = True
                j += 1

        for elem in terms:
            if not elem.combinable:
                not_combinable.append(elem)

        i = 0
        while i < len(new_terms) - 1:
            j = i + 1
            while j < len(new_terms):
                if new_terms[i].indexes == new_terms[j].indexes:
                    new_terms.pop(j)
                else:
                    j += 1
            i += 1

        terms = new_terms

    while i < len(new_terms) - 1:
        j = i + 1
        while j < len(new_terms):
            if new_terms[i].indexes in new_terms[j].indexes:
                new_terms.pop(j)
            else:
                j += 1
        i += 1

    essentials = []
    while i < len(not_combinable):
        for index in not_combinable[i].indexes:
            unique = False
            if index in need_to_cover:
                unique = True
                for j in range(len(not_combinable)):
                    if j != i:
                        if index in not_combinable[j].indexes:
                            unique = False
                            break
            if unique:
                essentials.append(not_combinable[i])
                need_to_cover -= not_combinable[i].indexes
                not_combinable.pop(i)
                break
        i += 1

    while i < len(not_combinable):
        useful = False
        for index in not_combinable[i].indexes:
            if index in need_to_cover:
                useful = True
                break

        if not useful:
            not_combinable.pop(i)
        else:
            i += 1

    not_combinable.sort(key=lambda x: len(x.indexes), reverse=True)

    min_terms = essentials + set_cover(need_to_cover, not_combinable)

    return tokenize_terms(min_terms)


TOKEN_TO_PYTHON = '&', '|', '^', '~', '(', ')', 'false', 'true', 'A', 'B', 'C', 'D', 'E', 'F'
print(''.join(TOKEN_TO_PYTHON[i] for i in get_mdnf([0, 0, 0, 0, 1, 0, 0, 0, 1, '-', 1, 1, 1, 0, '-', 1])))
