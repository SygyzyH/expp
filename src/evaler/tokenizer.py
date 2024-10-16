import re
import tokens

def tokenize(string: str):
    token_specification = [(tkn.name, tkn.regex) for tkn in tokens.TOKENS]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    line_num = 1
    line_start = 0
    for mo in re.finditer(tok_regex, string):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if kind == 'NUMBER':
            scalar = 1
            if value[-1] in tokens.KNOWN_MAGNITUDES:
                scalar = tokens.KNOWN_MAGNITUDES[value[-1]]
                value = value[:-1]
            value = float(value) if '.' in value else int(value)
            value *= scalar
        elif kind == 'NEWLINE':
            line_start = mo.end()
            line_num += 1
            continue
        elif kind == 'SKIP':
            continue
        source_token = next(_ for _ in tokens.TOKENS if _ == kind)
        
        yield tokens.Token(
            source_token.name,
            source_token.regex,
            source_token.handler,
            source_token.priority,
            value,
            line_num,
            column,
        )
