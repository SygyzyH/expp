import tokenizer
import tokens

class PolishConstructor:
    def __init__(self) -> None:
        self._stack: list[tokens.Token] = []

    def consume_token(self, token: tokens.Token):
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
            self._stack.insert(max(0, len(self._stack) - 1), tokens.Token('O_PAREN', '(', token.line, token.column, None))
        if token.name == 'C_PAREN' or token.name == 'PAREN_BACK':
            while self._stack[-1].name != 'O_PAREN':
                yield self._stack.pop()
                assert len(self._stack) > 0, f'line: {token.line}, column: {token.column}: Missing opening parenthesis'
            self._stack.pop()
            if len(self._stack) > 0 and 'FUNC' in self._stack[-1].name:
                yield self._stack.pop()
        # TODO: FUNC_R doesn't prioritze just the next token with low priority
        elif token.name == 'O_PAREN' or token.name == 'FUNC_R':
            self._stack.append(token)
        elif token.name == 'EQUAL':
            self._stack.insert(0, token)
        elif token.name == 'FUNC_L':
            yield token
        elif token.priority > 0:
            if len(self._stack) == 0 or token.priority > self._stack[-1].priority:
                self._stack.append(token)
            else:
                while len(self._stack) != 0 and token.priority < self._stack[-1].priority:
                    yield self._stack.pop()
                self._stack.append(token)
        else:
            yield token
    