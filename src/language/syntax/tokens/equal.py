import language.syntax.syntax as syntax


class Equal(syntax.Token):
    def __init__(self):
        self.name = 'EQUAL'
        self.regex = r'='
        self.handler = syntax.NoHandler
        # NOTE: Priority requires to be treated as an operand by polish
        self.priority = 1 