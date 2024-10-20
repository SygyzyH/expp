import syntax
import syntax_error

class PolishConstructor:
    def __init__(self) -> None:
        self._stack: list[syntax.Token] = []

    def consume_token(self, token: syntax.Token):
        assert token.name != 'DIRECTIVE', f'line: {token.line}, column: {token.column}: Directive in mathematical expression'
        if token.name == 'END_STATEMENT':
            while len(self._stack) > 0:
                yield self._stack.pop()
            yield token
            return
        if token.name == 'PAREN_BACK':
            # TODO Think if this feature is any good.
            # The idea is, while writing your expression you may realize you forgot a parenthesis.
            # You can then "PAREN_BACK" to where its missing, and add it there.
            # The problem is that the stack doesn't remmember the operators and operands after an operation
            # is concluded
            self._stack.insert(max(0, len(self._stack) - 1), syntax.Token('O_PAREN', '(', token.line, token.column, None))
        if token.name == 'C_PAREN' or token.name == 'PAREN_BACK':
            assert 'O_PAREN' in self._stack, syntax_error.SyntaxError(token.line, token.column, 'Missing opening parenthesis')
            while self._stack[-1].name != 'O_PAREN':
                yield self._stack.pop()
            self._stack.pop()
            if len(self._stack) > 0 and 'FUNC' in self._stack[-1].name:
                yield self._stack.pop()
        # TODO: R_FUNC doesn't prioritze just the next token with low priority
        elif token.name == 'O_PAREN' or token.name == 'R_FUNC':
            self._stack.append(token)
        elif token.name == 'EQUAL':
            while len(self._stack) != 0:
                yield self._stack.pop()
            self._stack.insert(0, token)
        elif token.name == 'L_FUNC':
            yield token
        elif token.priority > 0:
            if len(self._stack) == 0 or token.priority > self._stack[-1].priority:
                self._stack.append(token)
            else:
                while len(self._stack) != 0 and token.priority <= self._stack[-1].priority:
                    yield self._stack.pop()
                self._stack.append(token)
        else:
            yield token
    