import language.syntax.syntax as syntax
import language.syntax.syntax_error as syntax_error
import utils.tree as tree
import language.base as base


class NamedVariableHandler(syntax.TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree):
        # TODO: Describe why this failed, "attempting to evaluate variable"
        raise AttributeError()

    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        assert node.value.value in assigments.keys(), syntax_error.ExppSyntaxError(node.value.line, node.value.column, f'No value assigned for {node.value.value}')
        return base.assign(assigments[node.value.value], **assigments)
    
    @staticmethod
    def simplify(node: tree.BiTree):
        return node
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str, **assigments):
        new_number = 0
        if node.value.value in assigments:
            #raise EncodingWarning
            return assigments[node.value.value].value.handler.derive(assigments[node.value.value], variable_name, **assigments)
        elif node.value.value == variable_name:
            new_number = 1
        new_value = syntax.default_token('NUMBER')
        new_value.value = new_number
        new_value.column = node.value.column
        new_value.line = node.value.line

        return tree.BiTree(None, None, new_value)

class Name(syntax.Token):
    def __init__(self):
        self.name = 'NAME'
        self.regex = r'[a-zA-Z_]+[0-9]*'
        self.handler = NamedVariableHandler