import language.syntax.syntax as syntax

class BackParenthesis(syntax.Token):
    def __init__(self):
        self.name = 'PAREN_BACK'
        self.regex = r'\]'
        self.handler = syntax.NoHandler