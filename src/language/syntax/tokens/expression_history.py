import language.syntax.syntax as syntax


class ExpressionHistory(syntax.Token):
    def __init__(self):
        self.name = 'EXP_HISTORY'
        self.regex = r'\$[0-9]+'
        self.handler = syntax.NoHandler