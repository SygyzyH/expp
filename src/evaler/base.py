import tokenizer
import polish
import tree

import logging


class Expression:
    def __init__(self, string) -> None:
        self.string = string
        self.tree = self._build_expression(string)

    def evaluate(self):
        return self.tree.value.handler.evaluate(self.tree)

    def assign(self, **parameters):
        return self.tree.value.handler.assign(self.tree, parameters)
    
    @staticmethod
    def _build_expression(string: str) -> tree.BiTree:
        polish_inst = polish.PolishConstructor()
        stack = []

        for token in tokenizer.tokenize(string):
            logging.debug(f"Generated token {token}")
            for polish_token in polish_inst.consume_token(token):
                logging.debug(f"Polished token {polish_token}")
                if polish_token.priority > 0:
                    assert len(stack) > 1, f'line: {polish_token.line}, column: {polish_token.column}: Operator missing arguments'
                    if polish_token.name == 'EQUAL':
                        assert len(stack) == 2, f'line: {polish_token.line}, column: {polish_token.column}: Expression uses equality result'
                    # NOTE: The flipped order (rhs first in stack, but second in constructor)
                    rhs, lhs = stack.pop(), stack.pop()
                    stack.append(tree.BiTree(lhs, rhs, polish_token))
                elif polish_token.name == 'FUNC_R':
                    assert len(stack) > 0, f'line: {polish_token.line}, column: {polish_token.column}: Function missing argument'
                    stack.append(tree.BiTree(None, stack.pop(), polish_token))
                elif polish_token.name == 'FUNC_L':
                    assert len(stack) > 0, f'line: {polish_token.line}, column: {polish_token.column}: Function missing argument'
                    stack.append(tree.BiTree(stack.pop(), None, polish_token))
                else:
                    stack.append(tree.BiTree(None, None, polish_token))

        assert len(stack) == 1, 'Disjointed expression'

        return stack.pop()

if __name__ == "__main__":
    import logging
    import sys
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG,
        format="[%(levelname)s:%(funcName)s:%(lineno)s] %(message)s"
    )
    exp = Expression("2 + 5 as k * 3 + 2 * 2; 2 + 2")
    print(exp.evaluate())