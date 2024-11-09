class ExppSyntaxError(Exception):
    def __init__(self, line, col, message) -> None:
        super().__init__(f"line: {line}, column: {col}: {message}")
        self.line = line
        self.col = col