import language.syntax.syntax as syntax
import utils.tree as tree


def sin_derivative(node: tree.BiTree, variable_name: str, **assigments):
    new_value = syntax.default_token('R_FUNC')
    new_value.value = 'cos'
    new_value.column = node.value.column
    new_value.line = node.value.line

    rhs = node.rhs.value.handler.derive(node.rhs, variable_name, **assigments)

    return tree.BiTree(None, rhs, new_value)

def cos_derivative(node: tree.BiTree, variable_name: str, **assigments):
    new_value = syntax.default_token('NUMBER')
    new_value.value = -1
    new_value.column = node.value.column
    new_value.line = node.value.line

    minus_one = tree.BiTree(None, None, new_value)

    new_value = syntax.default_token('R_FUNC')
    new_value.value = 'sin'
    new_value.column = node.value.column
    new_value.line = node.value.line

    cos = tree.BiTree(None, node.rhs, new_value)

    new_value = syntax.default_token('MUL')
    new_value.value = '*'
    new_value.column = node.value.column
    new_value.line = node.value.line

    return tree.BiTree(minus_one, cos, new_value)

def tan_derivative(node: tree.BiTree, variable_name: str, **assigments):
    new_value = syntax.default_token('R_FUNC')
    new_value.value = 'cos'
    new_value.column = node.value.column
    new_value.line = node.value.line

    cos = tree.BiTree(None, node.rhs, new_value)

    new_value = syntax.default_token('NUMBER')
    new_value.value = 2
    new_value.column = node.value.column
    new_value.line = node.value.line

    immediate = tree.BiTree(None, None, new_value)

    new_value = syntax.default_token('POW')
    new_value.value = '^'
    new_value.column = node.value.column
    new_value.line = node.value.line

    sec = tree.BiTree(cos, immediate, new_value)

    rhs = node.rhs.value.handler.derive(node.rhs, variable_name, **assigments)

    new_value = syntax.default_token('MUL')
    new_value.value = '*'
    new_value.column = node.value.column
    new_value.line = node.value.line

    return tree.BiTree(rhs, sec, new_value)

def ln_derivative(node: tree.BiTree, variable_name: str, **assigments):
    new_value = syntax.default_token('DIV')
    new_value.value = '/'
    new_value.column = node.value.column
    new_value.line = node.value.line

    return tree.BiTree(
        node.rhs.value.handler.derive(node.rhs, variable_name, **assigments),
        node.rhs,
        new_value
    )

def exp_derivative(node: tree.BiTree, variable_name: str, **assigments):
    new_value = syntax.default_token('CONST')
    new_value.value = '\\e'
    new_value.column = node.value.column
    new_value.line = node.value.line

    const_e = tree.BiTree(None, None, new_value)

    new_value = syntax.default_token('POW')
    new_value.value = '^'
    new_value.column = node.value.column
    new_value.line = node.value.line

    expanded_exp = tree.BiTree(
        const_e,
        node.rhs,
        new_value
    )

    return expanded_exp.value.handler.derive(expanded_exp, variable_name, **assigments)

def square_root_derivative(node: tree.BiTree, variable_name: str, **assigments):
    new_value = syntax.default_token('NUMBER')
    new_value.value = 0.5
    new_value.column = node.value.column
    new_value.line = node.value.line

    immediate = tree.BiTree(None, None, new_value)

    new_value = syntax.default_token('POW')
    new_value.value = '^'
    new_value.column = node.value.column
    new_value.line = node.value.line

    expanded_exp = tree.BiTree(
        node.rhs,
        immediate,
        new_value
    )

    return expanded_exp.value.handler.derive(expanded_exp, variable_name, **assigments)

KNOWN_FUNCTION_DERIVATIVES = {
    'sin': sin_derivative,
    'cos': cos_derivative,
    'tan': tan_derivative,
    'ln': ln_derivative,
    'exp': exp_derivative,
    'sqrt': square_root_derivative,
}

class RightFunctionHandler(syntax.TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree | object):
        func = syntax.KNOWN_FUNCTIONS[node.value.value]
        return func(node.rhs.value.handler.evaluate(node.rhs))
    
    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        func = syntax.KNOWN_FUNCTIONS[node.value.value]
        return func(node.rhs.value.handler.assign(node.rhs, **assigments))
    
    @staticmethod
    def simplify(node: tree.BiTree):
        # TODO
        node.rhs = node.rhs.value.handler.simplify(node.rhs)
        return node
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str, **_):
        func = KNOWN_FUNCTION_DERIVATIVES[node.value.value]
        return func(node, variable_name)

class RightFunction(syntax.Token):
    def __init__(self):
        self.name = 'R_FUNC'
        self.regex = r'|'.join(list(syntax.KNOWN_FUNCTIONS))
        self.handler = RightFunctionHandler
        self.priority = 5