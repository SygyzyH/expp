import tokenizer
import tokens
import polish
import tree

import logging

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
                assert len(self._stack) > 0, f'line: {polish_token.line}, column: {polish_token.column}: Function missing argument'
                self._stack.append(tree.BiTree(None, self._stack.pop(), polish_token))
            elif polish_token.name == 'FUNC_L':
                assert len(self._stack) > 0, f'line: {polish_token.line}, column: {polish_token.column}: Function missing argument'
                self._stack.append(tree.BiTree(self._stack.pop(), None, polish_token))
            elif polish_token.priority > 0:
                assert len(self._stack) > 1, f'line: {polish_token.line}, column: {polish_token.column}: Operator missing arguments'
                # NOTE: The flipped order (rhs first in stack, but second in constructor)
                rhs, lhs = self._stack.pop(), self._stack.pop()
                self._stack.append(tree.BiTree(lhs, rhs, polish_token))
            else:
                self._stack.append(tree.BiTree(None, None, polish_token))
        # If no statment was completed, empty yield for now
        return

def evaluate(exp: tree.BiTree):
    return exp.value.handler.evaluate(exp)

def assign(exp: tree.BiTree, **parameters):
    return exp.value.handler.assign(exp, **parameters)

def derive(exp: tree.BiTree, variable_name: str):
    return exp.value.handler.derive(exp, variable_name)

if __name__ == "__main__":
    import logging
    import sys
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG,
        format="[%(levelname)s:%(funcName)s:%(lineno)s] %(message)s"
    )

    statment = StatmentConstructor()
    for token in tokenizer.tokenize("16 * x"):
        exp = statment.consume_token(token)
        if exp is not None:
            print(derive(exp, 'x'))
            print(assign(derive(exp, 'x'), x=2))