import language.syntax.syntax as syntax
import utils.tree as tree

import copy


class ConstHandler(syntax.TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree):
        return syntax.KNOWN_CONSTANTS['\\' + node.value.value]

    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        return syntax.KNOWN_CONSTANTS['\\' + node.value.value]
    
    @staticmethod
    def simplify(node: tree.BiTree):
        return node
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str, **_):
        new_node_value = copy.copy(node.value)
        new_node_value.value = 0
        return tree.BiTree(None, None, new_node_value)
 

class Constant(syntax.Token):
    def __init__(self):
        self.name = 'CONST'
        self.regex = r'|'.join(list(syntax.KNOWN_CONSTANTS))
        self.handler = syntax.NoHandler