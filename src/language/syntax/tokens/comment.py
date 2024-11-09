import language.syntax.syntax as syntax

class Comment(syntax.Token):
    def __init__(self):
        self.name = 'COMMENT'
        self.regex = r'#.*#'
        self.handler = syntax.NoHandler