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

        for token in tokenizer.tokenize(string):
            logging.debug(f"Generated token {token}")
            polish_inst.consume_token(token)
        logging.debug(polish_inst.finish())

        stack = []
        for token in polish_inst.finish():
            logging.debug(token)
            if token.priority > 0:
                assert len(stack) > 1, f'line: {token.line}, column: {token.column}: Operator missing arguments'
                if token.name == 'EQUAL':
                    assert len(stack) == 2, f'line: {token.line}, column: {token.column}: Expression uses equality result'
                # NOTE: The flipped order (rhs first in stack, but second in constructor)
                rhs, lhs = stack.pop(), stack.pop()
                stack.append(tree.BiTree(lhs, rhs, token))
            elif token.name == 'FUNC_R':
                assert len(stack) > 0, f'line: {token.line}, column: {token.column}: Function missing argument'
                stack.append(tree.BiTree(None, stack.pop(), token))
            elif token.name == 'FUNC_L':
                assert len(stack) > 0, f'line: {token.line}, column: {token.column}: Function missing argument'
                stack.append(tree.BiTree(stack.pop(), None, token))
            else:
                stack.append(tree.BiTree(None, None, token))
            logging.debug(stack)

        assert len(stack) == 1, 'Disjointed expression'

        return stack.pop()

if __name__ == "__main__":
    import logging
    import sys
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.INFO,
        format="[%(levelname)s:%(funcName)s:%(lineno)s] %(message)s"
    )
    exp = Expression(" as k")
    print(exp.evaluate())