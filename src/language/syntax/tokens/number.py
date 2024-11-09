import language.syntax.syntax as syntax
import utils.tree as tree

import copy


class NumberHandler(syntax.TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree):
        return node.value.value

    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        return node.value.value
    
    @staticmethod
    def simplify(node: tree.BiTree):
        return node
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str, **_):
        new_node_value = copy.copy(node.value)
        new_node_value.value = 0
        return tree.BiTree(None, None, new_node_value)

class Number(syntax.Token):
    def __init__(self):
        self.name = 'NUMBER'
        self.regex =  r'-?\d+(\.\d+)?j?(' + '|'.join(list(syntax.KNOWN_MAGNITUDES.keys())) + r')?'
        self.handler = NumberHandler