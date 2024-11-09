import language.syntax.syntax as syntax
import utils.tree as tree


class SubtractionHandler(syntax.TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree | object):
        return node.lhs.value.handler.evaluate(node.lhs) - node.rhs.value.handler.evaluate(node.rhs)
    
    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        return node.lhs.value.handler.assign(node.lhs, **assigments) - node.rhs.value.handler.assign(node.rhs, **assigments)

    @staticmethod
    def simplify(node: tree.BiTree):
        node.lhs = node.lhs.value.handler.simplify(node.lhs)        
        node.rhs = node.rhs.value.handler.simplify(node.rhs)
        if node.rhs.value.value == 0:
            return node.lhs
        return node
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str, **assigments):
        return tree.BiTree(
            node.lhs.value.handler.derive(node.lhs, variable_name, **assigments),
            node.rhs.value.handler.derive(node.rhs, variable_name, **assigments),
            node.value
        )

class Subtract(syntax.Token):
    def __init__(self):
        self.name = 'SUB'
        self.regex = r'-'
        self.handler = syntax.NoHandler
        self.priority = 2 