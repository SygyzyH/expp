import tokenizer
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

def derive(exp: tree.BiTree, variable_name: str, *_, **__):
    return exp.value.handler.derive(exp, variable_name)

def solve(exp: tree.BiTree, variable: str, max_iter=MAX_SOLUTION_DEPTH, epsil=SOLUTION_EPSIL, tolerance=SOLUTION_TOLERANCE, **parameters):
    from syntax import default_token
    if exp.value.name == 'EQUAL':
        new_token = default_token('SUB')
        new_token.value = '-'
        new_token.line = exp.value.line
        new_token.column = exp.value.column
        exp = copy.copy(exp)
        exp.value = new_token

    x0 = 1.0
    prime = derive(exp, variable)
    new_token = default_token('NUMBER')
    
    for _ in range(max_iter):
        new_token.value = x0
        y = assign(exp, **{variable: tree.BiTree(None, None, new_token)}, **parameters)
        y_prime = assign(prime, **{variable: tree.BiTree(None, None, new_token)}, **parameters)
    
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
    return (stringify(exp.lhs) if exp.lhs is not None else '') + str(exp.value.value) + (stringify(exp.rhs) if exp.rhs is not None else '')

if __name__ == "__main__":
    import logging
    import sys
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG,
        format="[%(levelname)s:%(funcName)s:%(lineno)s] %(message)s"
    )
    import statement

    statment = statement.StatmentConstructor()
    for token in tokenizer.tokenize("1 + 1 - 1 + 1 + x * x"):
        exp = statment.consume_token(token)
        if exp is not None:
            #print(exp)
            #print(derive(exp, 'x'))
            print(stringify(derive(exp, 'x')))
            #print(solve(exp, 'x'))