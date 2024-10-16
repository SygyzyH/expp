import tokenizer
import polish
import tree

import logging

def build_expression(string: str):
        polish_inst = polish.PolishConstructor()
        stack = []

        for token in tokenizer.tokenize(string):
            logging.debug(f"Generated token {token}")
            for polish_token in polish_inst.consume_token(token):
                logging.debug(f"Polished token {polish_token}")
                if polish_token.name == 'END_STATEMENT':
                    logging.debug(f"Finished statement {stack}")
                    assert len(stack) == 1, 'Disjointed expression'
                    yield stack.pop()
                    continue
                if polish_token.name == 'FUNC_R':
                    assert len(stack) > 0, f'line: {polish_token.line}, column: {polish_token.column}: Function missing argument'
                    stack.append(tree.BiTree(None, stack.pop(), polish_token))
                elif polish_token.name == 'FUNC_L':
                    assert len(stack) > 0, f'line: {polish_token.line}, column: {polish_token.column}: Function missing argument'
                    stack.append(tree.BiTree(stack.pop(), None, polish_token))
                elif polish_token.priority > 0:
                    assert len(stack) > 1, f'line: {polish_token.line}, column: {polish_token.column}: Operator missing arguments'
                    # NOTE: The flipped order (rhs first in stack, but second in constructor)
                    rhs, lhs = stack.pop(), stack.pop()
                    stack.append(tree.BiTree(lhs, rhs, polish_token))
                else:
                    stack.append(tree.BiTree(None, None, polish_token))

def evaluate(exp: tree.BiTree):
    return exp.value.handler.evaluate(exp)

def assign(exp: tree.BiTree, **parameters):
    return exp.value.handler.assign(exp, parameters)

if __name__ == "__main__":
    import logging
    import sys
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG,
        format="[%(levelname)s:%(funcName)s:%(lineno)s] %(message)s"
    )
    for exp in build_expression("sqrt 4 + sqrt 16 * 2]"):
        print(exp)
        print(evaluate(exp))