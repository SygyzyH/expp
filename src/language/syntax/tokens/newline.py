import language.syntax.syntax as syntax


class Newline(syntax.Token):
    def __init__(self):
        self.name = 'NEWLINE'
        self.regex = r'\n'
        self.handler = syntax.NoHandler