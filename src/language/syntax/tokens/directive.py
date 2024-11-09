import language.syntax.syntax as syntax


class Directive(syntax.Token):
    def __init__(self):
        self.name = 'DIRECTIVE'
        self.regex = r'\$' + r'|\$'.join(list(syntax.KNOWN_DIRECTIVES.keys()))
        self.handler = syntax.NoHandler