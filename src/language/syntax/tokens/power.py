import language.syntax.syntax as syntax
import utils.tree as tree


class ExponantiationHandler(syntax.TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree | object):
        return node.lhs.value.handler.evaluate(node.lhs) ** node.rhs.value.handler.evaluate(node.rhs)
    
    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        return node.lhs.value.handler.assign(node.lhs, **assigments) ** node.rhs.value.handler.assign(node.rhs, **assigments)

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
        if node.rhs.value.value == 0:
            new_value = syntax.default_token('NUMBER')
            new_value.value = 1
            new_value.column = node.value.column
            new_value.line = node.value.line
            return tree.BiTree(None, None, new_value)
        if node.rhs.value.value == 1:
            return node.lhs
        return node
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str, **assigments):
        lhs = node.lhs.value.handler.derive(node.lhs, variable_name, **assigments)
        rhs = node.rhs.value.handler.derive(node.rhs, variable_name, **assigments)

        new_value = syntax.default_token('R_FUNC')
        new_value.value = 'ln'
        new_value.column = node.value.column
        new_value.line = node.value.line

        ln = tree.BiTree(
            None,
            node.lhs,
            new_value
        )

        new_value = syntax.default_token('MUL')
        new_value.value = '*'
        new_value.column = node.value.column
        new_value.line = node.value.line

        inside_lhs = tree.BiTree(
            rhs,
            ln,
            new_value
        )

        inside_rhs_mul = tree.BiTree(
            lhs,
            node.rhs,
            new_value
        )

        new_value = syntax.default_token('DIV')
        new_value.value = '/'
        new_value.column = node.value.column
        new_value.line = node.value.line

        inside_rhs = tree.BiTree(
            inside_rhs_mul,
            node.lhs,
            new_value
        )

        new_value = syntax.default_token('ADD')
        new_value.value = '+'
        new_value.column = node.value.column
        new_value.line = node.value.line

        inside_sum = tree.BiTree(
            inside_lhs,
            inside_rhs,
            new_value
        )

        new_value = syntax.default_token('MUL')
        new_value.value = '*'
        new_value.column = node.value.column
        new_value.line = node.value.line

        return tree.BiTree(
            node,
            inside_sum,
            new_value
        )

class Power(syntax.Token):
    def __init__(self):
        self.name = 'POW'
        self.regex = r'\^|\*\*'
        self.handler = syntax.NoHandler
        self.priority = 4