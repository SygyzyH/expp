from dataclasses import dataclass
from abc import ABC, abstractmethod
import math
import copy

import base
import tree

KNOWN_DIRECTIVES = {
    'eval': base.evaluate,
    'assign': base.assign,
    'derive': base.derive,
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
    'log': math.log10,
    'exp': math.exp,
    'sqrt': math.sqrt,
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
    def derive(node: tree.BiTree, variable_name: str):
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

class NumberHandler(TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree):
        return node.value.value

    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        return node.value.value
    
    @staticmethod
    def simplify(node: tree.BiTree):
        return node.value.value
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str):
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
        return KNOWN_CONSTANTS['\\' + node.value.value]
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str):
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
        return base.assign(assigments[node.value.value], **assigments)
    
    @staticmethod
    def simplify(node: tree.BiTree):
        return node
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str):
        new_number = 0
        if node.value.value == variable_name:
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
        raise NotImplementedError
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str):
        return tree.BiTree(
            node.lhs.value.handler.derive(node.lhs, variable_name),
            node.rhs.value.handler.derive(node.rhs, variable_name),
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
        raise NotImplementedError
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str):
        return tree.BiTree(
            node.lhs.value.handler.derive(node.lhs, variable_name),
            node.rhs.value.handler.derive(node.rhs, variable_name),
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
        raise NotImplementedError
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str):
        lhs = tree.BiTree(
            node.lhs.value.handler.derive(node.lhs, variable_name),
            node.rhs,
            node.value
        )
        rhs = tree.BiTree(
            node.rhs.value.handler.derive(node.rhs, variable_name),
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
        raise NotImplementedError
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str):
        new_value = default_token('MUL')
        new_value.value = '*'
        new_value.column = node.value.column
        new_value.line = node.value.line

        lhs = tree.BiTree(
            node.lhs.value.handler.derive(node.lhs, variable_name),
            node.rhs,
            new_value
        )

        rhs = tree.BiTree(
            node.lhs,
            node.rhs.value.handler.derive(node.rhs, variable_name),
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
        new_value.value = 2
        new_value.column = node.value.column
        new_value.line = node.value.line

        divisor = tree.BiTree(node.lhs, immediat, new_value)

        return tree.BiTree(
            divisor,
            divident,
            node.value
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
        raise NotImplementedError
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str):
        lhs = node.lhs.value.handler.derive(node.lhs, variable_name)
        rhs = node.rhs.value.handler.derive(node.rhs, variable_name)

        new_value = default_token('FUNC_R')
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
        raise NotImplementedError
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str):
        raise NotImplementedError

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
        raise NotImplementedError
    
    @staticmethod
    def derive(node: tree.BiTree, variable_name: str):
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
            node.lhs.value.handler.derive(node.lhs, variable_name),
            new_value
        )

BASE_TOKENS = [
    Token('END_STATEMENT', r';', None),
    Token('DIRECTIVE', r'\$' + r'|\$'.join(list(KNOWN_DIRECTIVES.keys())), None),
    Token('HISTORY', r'\$[0-9]+', None),
    Token('RESULT_HISTORY', r'\$\$[0-9]+', None),
    Token('NUMBER', r'-?\d+(\.\d+)?j?[' + ''.join(list(KNOWN_MAGNITUDES.keys())) + r']?', NumberHandler),
    Token('EQUAL', r'=', None, priority=1), # NOTE: Priority requires to be treated as an operand by polish
    Token('ADD', r'\+', AdditionHandler, priority=2),
    Token('SUB', r'-', SubtractionHandler, priority=2),
    Token('POW', r'\^|\*\*', ExponantiationHandler, priority=4),
    Token('MUL', r'\*|\.', MultiplicationHandler, priority=3),
    Token('DIV', r'/', DivisionHandler, priority=3),
    Token('O_PAREN', r'\(', None),
    Token('C_PAREN', r'\)', None),
    Token('PAREN_BACK', r'\]', None),
    Token('FUNC_L', r'as [' + ''.join(list(KNOWN_MAGNITUDES.keys())) + r']', MagnitudeCastHandler),
    Token('FUNC_R', r'|'.join(list(KNOWN_FUNCTIONS)), RightFunctionHandler, priority=5),
    Token('CONST', r'|'.join(list(KNOWN_CONSTANTS)), ConstHandler),
    Token('NAME', r'[a-zA-Z_]+', NamedVariableHandler),
    Token('NEWLINE', r'\n', None),
    Token('SKIP', r'[ \t]+', None),
    Token('MISMATCH', r'.', None),
]

def default_token(name: str):
    return copy.copy(next(_ for _ in BASE_TOKENS if _ == name))