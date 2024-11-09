import language.syntax.syntax as syntax


class ResultHistory(syntax.Token):
    def __init__(self):
        self.name = 'RESULT_HISTORY'
        self.regex = r'\$\$[0-9]+'
        self.handler = syntax.NoHandler