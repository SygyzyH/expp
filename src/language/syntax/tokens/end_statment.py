import language.syntax.syntax as syntax


class EndStatement(syntax.Token):
    def __init__(self):
        self.name = 'END_STATEMENT'
        self.regex = r';'
        self.handler = syntax.NoHandler