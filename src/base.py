import syntax_error
import tree

import logging
import copy

MAX_SOLUTION_DEPTH = 20
SOLUTION_EPSIL = 1e-6
SOLUTION_TOLERANCE = 1e-9

def evaluate(exp: tree.BiTree, *_, **__):
    return exp.value.handler.evaluate(exp)

def assign(exp: tree.BiTree, *_, **assigments):
    return exp.value.handler.assign(exp, **assigments)

def derive(exp: tree.BiTree, variable_name: str, *_, **assigments):
    return simplify(exp.value.handler.derive(exp, variable_name, **assigments))

def simplify(exp: tree.BiTree, *_, **__):
    return exp.value.handler.simplify(exp)

def solve(exp: tree.BiTree, variable: str, max_iter=MAX_SOLUTION_DEPTH, epsil=SOLUTION_EPSIL, tolerance=SOLUTION_TOLERANCE, **assigments):
    from syntax import default_token
    if exp.value.name == 'EQUAL':
        new_token = default_token('SUB')
        new_token.value = '-'
        new_token.line = exp.value.line
        new_token.column = exp.value.column
        exp = copy.copy(exp)
        exp.value = new_token

    x0 = 1.0
    prime = derive(exp, variable, **assigments)
    new_token = default_token('NUMBER')
    
    for _ in range(max_iter):
        new_token.value = x0
        logging.debug(f'Trying {x0}')
        y = assign(exp, **{variable: tree.BiTree(None, None, new_token)}, **assigments)
        y_prime = assign(prime, **{variable: tree.BiTree(None, None, new_token)}, **assigments)
        logging.debug(f'{y}, {y_prime}')
    
        if abs(y_prime) < epsil:
            logging.debug(f'Found approximate solution, stopping early')
            return x0

        x1 = x0 - y / y_prime
        
        if abs(x1 - x0) <= tolerance:
            logging.debug(f'Found approximate solution, stopping early')
            return x0

        x0 = x1

    logging.debug(f'Failed to converge in {max_iter} iterations, current estimate {x0}')
    return x0

def stringify(exp: tree.BiTree) -> str:
    lhs = rhs = ''
    if exp.lhs is not None:
        lhs = f'{stringify(exp.lhs)}'
        if exp.lhs.depth > 1:
            lhs = f'({lhs})'
    if exp.rhs is not None:
        rhs = f'{stringify(exp.rhs)}'
        if exp.rhs.depth > 1:
            rhs = f'({rhs})' 
    if exp.value.priority > 0:
        lhs = f'{lhs} '
        rhs = f' {rhs}'

    return lhs + str(exp.value.value) + rhs

def nevaluate(exp: tree.BiTree, *_, **__) -> tree.BiTree:
    return exp

def set(exp: tree.BiTree, *_, **__):
    raise syntax_error.SyntaxError(exp.value.line, exp.value.line, 'Set directive executed by base class')