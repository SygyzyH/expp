import language.syntax.syntax as syntax
import utils.tree as tree


class MultiplicationHandler(syntax.TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree | object):
        return node.lhs.value.handler.evaluate(node.lhs) * node.rhs.value.handler.evaluate(node.rhs)
    
    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        return node.lhs.value.handler.assign(node.lhs, **assigments) * node.rhs.value.handler.assign(node.rhs, **assigments)

    @staticmethod
    def simplify(node: tree.BiTree):
        node.lhs = node.lhs.value.handler.simplify(node.lhs)
        node.rhs = node.rhs.value.handler.simplify(node.rhs)
        if node.lhs.value.value == 0 or node.rhs.value.value == 0:
            new_value = syntax.default_token('NUMBER')
            new_value.value = 0
            new_value.column = node.value.column
            new_value.line = node.value.line
            return tree.BiTree(None, None, new_value)
        
        if node.rhs.value.value == 1:
            return node.lhs
        if node.lhs.value.value == 1:
            return node.rhs
        return node
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str, **assigments):
        lhs = tree.BiTree(
            node.lhs.value.handler.derive(node.lhs, variable_name, **assigments),
            node.rhs,
            node.value
        )
        rhs = tree.BiTree(
            node.rhs.value.handler.derive(node.rhs, variable_name, **assigments),
            node.lhs,
            node.value
        )

        new_value = syntax.default_token('ADD')
        new_value.value = '+'
        new_value.column = node.value.column
        new_value.line = node.value.line

        return tree.BiTree(
            lhs,
            rhs,
            new_value
        )

class Multiply(syntax.Token):
    def __init__(self):
        self.name = 'MUL'
        self.regex = r'\*|\.'
        self.handler = MultiplicationHandler
        self.priority = 3 