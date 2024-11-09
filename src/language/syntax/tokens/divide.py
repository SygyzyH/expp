import language.syntax.syntax as syntax
import utils.tree as tree


class DivisionHandler(syntax.TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree | object):
        return node.lhs.value.handler.evaluate(node.lhs) / node.rhs.value.handler.evaluate(node.rhs)
    
    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        return node.lhs.value.handler.assign(node.lhs, **assigments) / node.rhs.value.handler.assign(node.rhs, **assigments)

    @staticmethod
    def simplify(node: tree.BiTree):
        node.lhs = node.lhs.value.handler.simplify(node.lhs)
        if node.lhs.value.value == 0:
            new_value = syntax.default_token('NUMBER')
            new_value.value = 0
            new_value.column = node.value.column
            new_value.line = node.value.line
            return tree.BiTree(None, None, new_value)
        
        node.rhs = node.rhs.value.handler.simplify(node.rhs)
        if node.rhs.value.value == 1:
            return node.lhs
        return node
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str, **assigments):
        new_value = syntax.default_token('MUL')
        new_value.value = '*'
        new_value.column = node.value.column
        new_value.line = node.value.line

        lhs = tree.BiTree(
            node.lhs.value.handler.derive(node.lhs, variable_name, **assigments),
            node.rhs,
            new_value
        )

        rhs = tree.BiTree(
            node.lhs,
            node.rhs.value.handler.derive(node.rhs, variable_name, **assigments),
            new_value
        )

        new_value = syntax.default_token('SUB')
        new_value.value = '-'
        new_value.column = node.value.column
        new_value.line = node.value.line

        divident = tree.BiTree(lhs, rhs, new_value)

        new_value = syntax.default_token('NUMBER')
        new_value.value = 2
        new_value.column = node.value.column
        new_value.line = node.value.line

        immediat = tree.BiTree(None, None, new_value)

        new_value = syntax.default_token('POW')
        new_value.value = '^'
        new_value.column = node.value.column
        new_value.line = node.value.line

        divisor = tree.BiTree(node.rhs, immediat, new_value)

        new_value = syntax.default_token('DIV')
        new_value.value = '/'
        new_value.column = node.value.column
        new_value.line = node.value.line

        return tree.BiTree(
            divident,
            divisor,
            new_value
        )
    
class Divide(syntax.Token):
    def __init__(self):
        self.name = 'DIV'
        self.regex = r'/'
        self.handler = syntax.NoHandler
        self.priority = 3 