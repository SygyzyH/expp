import re
import language.syntax.syntax as syntax
import language.syntax.syntax_error as syntax_error

def tokenize(string: str):
    token_specification = [(tkn.name, tkn.regex) for tkn in syntax.BASE_TOKENS]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    line_num = 1
    line_start = 0
    column = 0
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
            elif value[-2:] in syntax.KNOWN_MAGNITUDES:
                scalar = syntax.KNOWN_MAGNITUDES[value[-2:]]
                value = value[:-2]
            if 'j' in value:
                value = complex(value)
            else:
                value = float(value) if '.' in value else int(value)
            value *= scalar
        elif kind == 'EXP_HISTORY':
            value = int(value[1:])
        elif kind == 'RESULT_HISTORY':
            value = int(value[2:])
        elif kind == 'NEWLINE':
            line_start = mo.end()
            line_num += 1
            continue
        elif kind == 'COMMENT':
            line_num += value.count('\n')
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise syntax_error.ExppSyntaxError(line_num, column, f'Mismatched symbol "{value}"')
        source_token = syntax.default_token(kind)
        source_token.value = value
        source_token.line = line_num
        source_token.column = column
        last_token = source_token

        yield last_token
    if last_token is None or last_token.name != 'END_STATEMENT':
        terminator = syntax.default_token('END_STATEMENT')
        terminator.line = line_num
        terminator.column = column

        yield terminator
