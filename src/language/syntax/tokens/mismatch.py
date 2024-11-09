import language.syntax.syntax as syntax


class Mismatch(syntax.Token):
    def __init__(self):
        self.name = 'MISMATCH'
        self.regex = r'.'
        self.handler = syntax.NoHandler