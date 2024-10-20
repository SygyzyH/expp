from dataclasses import dataclass
from abc import ABC, abstractmethod
import math
import copy

import base
import tree
import syntax_error

KNOWN_DIRECTIVES = {
    'eval': base.evaluate,
    'neval': base.nevaluate,
    'assign': base.assign,
    'derive': base.derive,
    'simplify': base.simplify,
    'solve': base.solve,
    'set': base.set,
    'get': base.get,
}

KNOWN_MAGNITUDES = {
    "T": 1e12,
    "G": 1e9,
    "M": 1e6,
    "k": 1e3,
    "o": 1e0,
    "m": 1e-3,
    "u": 1e-6,
    "n": 1e-9,
}

KNOWN_CONSTANTS = {
    r"\\pi": math.pi,
    r"\\e": math.e,
}

KNOWN_FUNCTIONS = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'acos': math.acos,
    'asin': math.asin,
    'atan': math.atan,
    'ln': math.log,
    'log2': math.log2,
    'log10': math.log10,
    'exp': math.exp,
    'sqrt': math.sqrt,
}
def sin_derivative(node: tree.BiTree, variable_name: str, **assigments):
    new_value = default_token('R_FUNC')
    new_value.value = 'cos'
    new_value.column = node.value.column
    new_value.line = node.value.line

    rhs = node.rhs.value.handler.derive(node.rhs, variable_name, **assigments)

    return tree.BiTree(None, rhs, new_value)

def cos_derivative(node: tree.BiTree, variable_name: str, **assigments):
    new_value = default_token('NUMBER')
    new_value.value = -1
    new_value.column = node.value.column
    new_value.line = node.value.line

    minus_one = tree.BiTree(None, None, new_value)

    new_value = default_token('R_FUNC')
    new_value.value = 'sin'
    new_value.column = node.value.column
    new_value.line = node.value.line

    cos = tree.BiTree(None, node.rhs, new_value)

    new_value = default_token('MUL')
    new_value.value = '*'
    new_value.column = node.value.column
    new_value.line = node.value.line

    return tree.BiTree(minus_one, cos, new_value)

def tan_derivative(node: tree.BiTree, variable_name: str, **assigments):
    new_value = default_token('R_FUNC')
    new_value.value = 'cos'
    new_value.column = node.value.column
    new_value.line = node.value.line

    cos = tree.BiTree(None, node.rhs, new_value)

    new_value = default_token('NUMBER')
    new_value.value = 2
    new_value.column = node.value.column
    new_value.line = node.value.line

    immediate = tree.BiTree(None, None, new_value)

    new_value = default_token('POW')
    new_value.value = '^'
    new_value.column = node.value.column
    new_value.line = node.value.line

    sec = tree.BiTree(cos, immediate, new_value)

    rhs = node.rhs.value.handler.derive(node.rhs, variable_name, **assigments)

    new_value = default_token('MUL')
    new_value.value = '*'
    new_value.column = node.value.column
    new_value.line = node.value.line

    return tree.BiTree(rhs, sec, new_value)

def ln_derivative(node: tree.BiTree, variable_name: str, **assigments):
    new_value = default_token('DIV')
    new_value.value = '/'
    new_value.column = node.value.column
    new_value.line = node.value.line

    return tree.BiTree(
        node.rhs.value.handler.derive(node.rhs, variable_name, **assigments),
        node.rhs,
        new_value
    )

def exp_derivative(node: tree.BiTree, variable_name: str, **assigments):
    new_value = default_token('CONST')
    new_value.value = '\\e'
    new_value.column = node.value.column
    new_value.line = node.value.line

    const_e = tree.BiTree(None, None, new_value)

    new_value = default_token('POW')
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
    new_value = default_token('NUMBER')
    new_value.value = 0.5
    new_value.column = node.value.column
    new_value.line = node.value.line

    immediate = tree.BiTree(None, None, new_value)

    new_value = default_token('POW')
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

class TokenHandler(ABC):
    @staticmethod
    @abstractmethod
    def evaluate(node: tree.BiTree):
        pass

    @staticmethod
    @abstractmethod
    def assign(node: tree.BiTree, **assigments):
        pass

    @staticmethod
    @abstractmethod
    def simplify(node: tree.BiTree):
        pass

    @staticmethod
    @abstractmethod
    def derive(node: tree.BiTree, variable_name: str, **assigments):
        pass

@dataclass
class Token:
    name: str
    regex: str
    handler: TokenHandler
    priority: int = 0
    value: str = None
    line: int = None
    column: int = None

    def __eq__(self, value: object) -> bool:
        return self.name == value or (hasattr(value, "name") and value.name == self.name)

    def __hash__(self) -> int:
        return hash(self.name)
    
    def __repr__(self) -> str:
        return f"{self.name}(value={self.value.__repr__()}, ({self.line}, {self.column}), priority={self.priority})"

class NoHandler(TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree):
        raise NotImplementedError

    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        raise NotImplementedError
    
    @staticmethod
    def simplify(node: tree.BiTree):
        raise NotImplementedError
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str, **_):
        raise NotImplementedError

class NumberHandler(TokenHandler):
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
    
class ConstHandler(TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree):
        return KNOWN_CONSTANTS['\\' + node.value.value]

    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        return KNOWN_CONSTANTS['\\' + node.value.value]
    
    @staticmethod
    def simplify(node: tree.BiTree):
        return node
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str, **_):
        new_node_value = copy.copy(node.value)
        new_node_value.value = 0
        return tree.BiTree(None, None, new_node_value)
    
class NamedVariableHandler(TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree):
        # TODO: Describe why this failed, "attempting to evaluate variable"
        raise

    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        assert node.value.value in assigments.keys(), syntax_error.SyntaxError(node.value.line, node.value.column, f'No value assigned for {node.value.value}')
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
        new_value = default_token('NUMBER')
        new_value.value = new_number
        new_value.column = node.value.column
        new_value.line = node.value.line

        return tree.BiTree(None, None, new_value)
class AdditionHandler(TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree | object):
        return node.lhs.value.handler.evaluate(node.lhs) + node.rhs.value.handler.evaluate(node.rhs)
    
    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        return node.lhs.value.handler.assign(node.lhs, **assigments) + node.rhs.value.handler.assign(node.rhs, **assigments)

    @staticmethod
    def simplify(node: tree.BiTree):
        node.lhs = node.lhs.value.handler.simplify(node.lhs)        
        node.rhs = node.rhs.value.handler.simplify(node.rhs)
        if node.lhs.value.value == 0:
            return node.rhs
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

class SubtractionHandler(TokenHandler):
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

class MultiplicationHandler(TokenHandler):
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
            new_value = default_token('NUMBER')
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

        new_value = default_token('ADD')
        new_value.value = '+'
        new_value.column = node.value.column
        new_value.line = node.value.line

        return tree.BiTree(
            lhs,
            rhs,
            new_value
        )

class DivisionHandler(TokenHandler):
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
            new_value = default_token('NUMBER')
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
        new_value = default_token('MUL')
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

        new_value = default_token('SUB')
        new_value.value = '-'
        new_value.column = node.value.column
        new_value.line = node.value.line

        divident = tree.BiTree(lhs, rhs, new_value)

        new_value = default_token('NUMBER')
        new_value.value = 2
        new_value.column = node.value.column
        new_value.line = node.value.line

        immediat = tree.BiTree(None, None, new_value)

        new_value = default_token('POW')
        new_value.value = '^'
        new_value.column = node.value.column
        new_value.line = node.value.line

        divisor = tree.BiTree(node.rhs, immediat, new_value)

        new_value = default_token('DIV')
        new_value.value = '/'
        new_value.column = node.value.column
        new_value.line = node.value.line

        return tree.BiTree(
            divident,
            divisor,
            new_value
        )

class ExponantiationHandler(TokenHandler):
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
            new_value = default_token('NUMBER')
            new_value.value = 0
            new_value.column = node.value.column
            new_value.line = node.value.line
            return tree.BiTree(None, None, new_value)
        
        node.rhs = node.rhs.value.handler.simplify(node.rhs)
        if node.rhs.value.value == 0:
            new_value = default_token('NUMBER')
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

        new_value = default_token('R_FUNC')
        new_value.value = 'ln'
        new_value.column = node.value.column
        new_value.line = node.value.line

        ln = tree.BiTree(
            None,
            node.lhs,
            new_value
        )

        new_value = default_token('MUL')
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

        new_value = default_token('DIV')
        new_value.value = '/'
        new_value.column = node.value.column
        new_value.line = node.value.line

        inside_rhs = tree.BiTree(
            inside_rhs_mul,
            node.lhs,
            new_value
        )

        new_value = default_token('ADD')
        new_value.value = '+'
        new_value.column = node.value.column
        new_value.line = node.value.line

        inside_sum = tree.BiTree(
            inside_lhs,
            inside_rhs,
            new_value
        )

        new_value = default_token('MUL')
        new_value.value = '*'
        new_value.column = node.value.column
        new_value.line = node.value.line

        return tree.BiTree(
            node,
            inside_sum,
            new_value
        )

class RightFunctionHandler(TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree | object):
        func = KNOWN_FUNCTIONS[node.value.value]
        return func(node.rhs.value.handler.evaluate(node.rhs))
    
    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        func = KNOWN_FUNCTIONS[node.value.value]
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

class MagnitudeCastHandler(TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree | object):
        magnitude = node.value.value[-1]
        return node.lhs.value.handler.evaluate(node.lhs) / KNOWN_MAGNITUDES[magnitude]
    
    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        magnitude = node.value.value[-1]
        return node.lhs.value.handler.assign(node.lhs, **assigments) / KNOWN_MAGNITUDES[magnitude]
    
    @staticmethod
    def simplify(node: tree.BiTree):
        magnitude = node.value.value[-1]
        node.lhs = node.lhs.value.handler.simplify(node.lhs)
        if node.lhs.value.value == 0:
            new_value = default_token('NUMBER')
            new_value.value = 0
            new_value.column = node.value.column
            new_value.line = node.value.line
            return tree.BiTree(None, None, new_value)
        if isinstance(node.lhs.value.value, (int, float, complex)):
            new_value = default_token('NUMBER')
            new_value.value = node.lhs.value.value / KNOWN_MAGNITUDES[magnitude]
            new_value.column = node.value.column
            new_value.line = node.value.line
            return tree.BiTree(None, None, new_value)
        return node
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str, **assigments):
        magnitude = node.value.value[-1]
        
        new_value = default_token('NUMBER')
        new_value.value = KNOWN_MAGNITUDES[magnitude]
        new_value.column = node.value.column
        new_value.line = node.value.line

        immidiate = tree.BiTree(None, None, new_value)

        new_value = default_token('MUL')
        new_value.value = '*'
        new_value.column = node.value.column
        new_value.line = node.value.line

        return tree.BiTree(
            immidiate,
            node.lhs.value.handler.derive(node.lhs, variable_name, **assigments),
            new_value
        )

BASE_TOKENS = [
    Token('END_STATEMENT', r';', NoHandler),
    Token('DIRECTIVE', r'\$' + r'|\$'.join(list(KNOWN_DIRECTIVES.keys())), NoHandler),
    Token('EXP_HISTORY', r'\$[0-9]+', NoHandler),
    Token('RESULT_HISTORY', r'\$\$[0-9]+', NoHandler),
    Token('NUMBER', r'-?\d+(\.\d+)?j?[' + ''.join(list(KNOWN_MAGNITUDES.keys())) + r']?', NumberHandler),
    Token('EQUAL', r'=', NoHandler, priority=1), # NOTE: Priority requires to be treated as an operand by polish
    Token('ADD', r'\+', AdditionHandler, priority=2),
    Token('SUB', r'-', SubtractionHandler, priority=2),
    Token('POW', r'\^|\*\*', ExponantiationHandler, priority=4),
    Token('MUL', r'\*|\.', MultiplicationHandler, priority=3),
    Token('DIV', r'/', DivisionHandler, priority=3),
    Token('O_PAREN', r'\(', NoHandler),
    Token('C_PAREN', r'\)', NoHandler),
    Token('PAREN_BACK', r'\]', NoHandler),
    Token('L_FUNC', r'as [' + ''.join(list(KNOWN_MAGNITUDES.keys())) + r']', MagnitudeCastHandler),
    Token('R_FUNC', r'|'.join(list(KNOWN_FUNCTIONS)), RightFunctionHandler, priority=5),
    Token('CONST', r'|'.join(list(KNOWN_CONSTANTS)), ConstHandler),
    Token('NAME', r'[a-zA-Z_]+[0-9]*', NamedVariableHandler),
    Token('COMMENT', r'#.*#', NoHandler),
    Token('NEWLINE', r'\n', NoHandler),
    Token('SKIP', r'[ \t]+', NoHandler),
    Token('MISMATCH', r'.', NoHandler),
]

def default_token(name: str):
    return copy.copy(next(_ for _ in BASE_TOKENS if _ == name))