import language.syntax.syntax as syntax


class OpenParenthesis(syntax.Token):
    def __init__(self):
        self.name = 'O_PAREN'
        self.regex = r'\('
        self.handler = syntax.NoHandler