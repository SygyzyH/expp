import tokenizer
import tokens
import polish
import tree

import logging
import copy

MAX_SOLUTION_DEPTH = 20
SOLUTION_EPSIL = 1e-6
SOLUTION_TOLERANCE = 1e-9

class StatmentConstructor:
    def __init__(self) -> None:
        self._polish_inst = polish.PolishConstructor()
        self._stack = []

    def consume_token(self, token: tokens.Token):
        for polish_token in self._polish_inst.consume_token(token):
            logging.debug(f"Polished token {polish_token}")
            if polish_token.name == 'END_STATEMENT':
                logging.debug(f"Finished statement {self._stack}")
                assert len(self._stack) == 1, 'Disjointed expression'
                # Statement was generated
                return self._stack.pop()
            if polish_token.name == 'FUNC_R':
                logging.debug("Left sided function")
                assert len(self._stack) > 0, f'line: {polish_token.line}, column: {polish_token.column}: Function missing argument'
                self._stack.append(tree.BiTree(None, self._stack.pop(), polish_token))
            elif polish_token.name == 'FUNC_L':
                logging.debug("Right sided function")
                assert len(self._stack) > 0, f'line: {polish_token.line}, column: {polish_token.column}: Function missing argument'
                self._stack.append(tree.BiTree(self._stack.pop(), None, polish_token))
            elif polish_token.priority > 0:
                logging.debug("Two sided function")
                assert len(self._stack) > 1, f'line: {polish_token.line}, column: {polish_token.column}: Operator missing arguments'
                # NOTE: The flipped order (rhs first in stack, but second in constructor)
                rhs, lhs = self._stack.pop(), self._stack.pop()
                self._stack.append(tree.BiTree(lhs, rhs, polish_token))
            else:
                logging.debug("Polish takes no arguments")
                self._stack.append(tree.BiTree(None, None, polish_token))
        # If no statment was completed, empty yield for now
        return

def evaluate(exp: tree.BiTree):
    return exp.value.handler.evaluate(exp)

def assign(exp: tree.BiTree, **parameters):
    return exp.value.handler.assign(exp, **parameters)

def derive(exp: tree.BiTree, variable_name: str):
    return exp.value.handler.derive(exp, variable_name)

def solve(exp: tree.BiTree, variable: str, max_iter=MAX_SOLUTION_DEPTH, epsil=SOLUTION_EPSIL, tolerance=SOLUTION_TOLERANCE, **parameters):
    if exp.value.name == 'EQUAL':
        new_token = tokens.default_token('SUB')
        new_token.value = '-'
        new_token.line = exp.value.line
        new_token.column = exp.value.column
        exp = copy.copy(exp)
        exp.value = new_token
    print(exp)

    x0 = 1.0
    prime = derive(exp, variable)
    
    for _ in range(max_iter):
        y = assign(exp, **{variable: x0}, **parameters)
        y_prime = assign(prime, **{variable: x0}, **parameters)
    
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

    statment = StatmentConstructor()
    for token in tokenizer.tokenize("1 + 1 - 1 + 1 + x * x"):
        exp = statment.consume_token(token)
        if exp is not None:
            #print(exp)
            #print(derive(exp, 'x'))
            print(stringify(derive(exp, 'x')))
            #print(solve(exp, 'x'))