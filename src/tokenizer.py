import re
import syntax

def tokenize(string: str):
    token_specification = [(tkn.name, tkn.regex) for tkn in syntax.BASE_TOKENS]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    line_num = 1
    line_start = 0
    last_token = None
    for mo in re.finditer(tok_regex, string):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if kind == 'NUMBER':
            scalar = 1
            if value[-1] in syntax.KNOWN_MAGNITUDES:
                scalar = syntax.KNOWN_MAGNITUDES[value[-1]]
                value = value[:-1]
            if 'j' in value:
                value = complex(value)
            else:
                value = float(value) if '.' in value else int(value)
            value *= scalar
        elif kind == 'HISTORY':
            value = int(value[1:])
        elif kind == 'RESULT_HISTORY':
            value = int(value[2:])
        elif kind == 'NEWLINE':
            line_start = mo.end()
            line_num += 1
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise SyntaxError(f'line: {line_num}, column: {column}: Mismatched symbol "{value}"')
        source_token = next(_ for _ in syntax.BASE_TOKENS if _ == kind)
        last_token = syntax.Token(
            source_token.name,
            source_token.regex,
            source_token.handler,
            source_token.priority,
            value,
            line_num,
            column,
        )

        yield last_token
    if last_token is None or last_token.name != 'END_STATEMENT':
        yield syntax.BASE_TOKENS[0]
