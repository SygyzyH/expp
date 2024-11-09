import language.syntax.syntax as syntax
import utils.tree as tree


class MagnitudeCastHandler(syntax.TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree | object):
        magnitude = node.value.value[len('as '):]
        return node.lhs.value.handler.evaluate(node.lhs) / syntax.KNOWN_MAGNITUDES[magnitude]
    
    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        magnitude = node.value.value[len('as '):]
        return node.lhs.value.handler.assign(node.lhs, **assigments) / syntax.KNOWN_MAGNITUDES[magnitude]
    
    @staticmethod
    def simplify(node: tree.BiTree):
        magnitude = node.value.value[len('as '):]
        node.lhs = node.lhs.value.handler.simplify(node.lhs)
        if node.lhs.value.value == 0:
            new_value = syntax.default_token('NUMBER')
            new_value.value = 0
            new_value.column = node.value.column
            new_value.line = node.value.line
            return tree.BiTree(None, None, new_value)
        if isinstance(node.lhs.value.value, (int, float, complex)):
            new_value = syntax.default_token('NUMBER')
            new_value.value = node.lhs.value.value / syntax.KNOWN_MAGNITUDES[magnitude]
            new_value.column = node.value.column
            new_value.line = node.value.line
            return tree.BiTree(None, None, new_value)
        return node
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str, **assigments):
        magnitude = node.value.value[len('as '):]
        
        new_value = syntax.default_token('NUMBER')
        new_value.value = syntax.KNOWN_MAGNITUDES[magnitude]
        new_value.column = node.value.column
        new_value.line = node.value.line

        immidiate = tree.BiTree(None, None, new_value)

        new_value = syntax.default_token('MUL')
        new_value.value = '*'
        new_value.column = node.value.column
        new_value.line = node.value.line

        return tree.BiTree(
            immidiate,
            node.lhs.value.handler.derive(node.lhs, variable_name, **assigments),
            new_value
        )

class LeftFunction(syntax.Token):
    def __init__(self):
        self.name = 'L_FUNC'
        self.regex = r'as (' + '|'.join(list(syntax.KNOWN_MAGNITUDES.keys())) + r')'
        self.handler = MagnitudeCastHandler