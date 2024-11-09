import language.syntax.syntax as syntax

class CloseParenthesis(syntax.Token):
    def __init__(self):
        self.name = 'C_PAREN'
        self.regex = r'\)'
        self.handler = syntax.NoHandler