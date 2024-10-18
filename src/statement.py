import syntax
import polish
import tree

import logging

class StatmentConstructor:
    def __init__(self) -> None:
        self._polish_inst = polish.PolishConstructor()
        self._stack = []

    def consume_token(self, token: syntax.Token):
        for polish_token in self._polish_inst.consume_token(token):
            logging.debug(f"Polished token {polish_token}")
            if polish_token.name == 'END_STATEMENT':
                logging.debug(f"Finished statement {self._stack}")
                if len(self._stack) == 0:
                    # Empty expression
                    return tree.BiTree(None, None, None)
                assert len(self._stack) == 1, f'line: {polish_token.line}, column: {polish_token.column}: Disjointed expression'
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
    
    def consume_exp(self, exp: tree.BiTree):
        self._stack.append(exp)
        return