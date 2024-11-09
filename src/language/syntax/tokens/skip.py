import language.syntax.syntax as syntax


class Skip(syntax.Token):
    def __init__(self):
        self.name = 'SKIP'
        self.regex = r'[ \t]+'
        self.handler = syntax.NoHandler