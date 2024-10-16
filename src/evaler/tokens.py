from dataclasses import dataclass
from abc import ABC, abstractmethod
import math

import tree

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
    'sin',
    'cos',
    'tan',
    'acos',
    'asin',
    'atan',
    'ln',
    'log2',
    'log',
    'exp',
    'sqrt',
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
    
class NamedVariableHandler(TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree):
        # TODO: Describe why this failed, "attempting to evaluate variable"
        raise

    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        return assigments[node.value.value]
    
    @staticmethod
    def simplify(node: tree.BiTree):
        return node
    
class AdditionHandler(TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree | object):
        return node.lhs.value.handler.evaluate(node.lhs) + node.rhs.value.handler.evaluate(node.rhs)
    
    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        return node.lhs.value.handler.assign(node.lhs, **assigments) + node.rhs.value.handler.assign(node.rhs, **assigments)

    @staticmethod
    def simplify(node: tree.BiTree):
        ...

class SubtractionHandler(TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree | object):
        return node.lhs.value.handler.evaluate(node.lhs) - node.rhs.value.handler.evaluate(node.rhs)
    
    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        return node.lhs.value.handler.assign(node.lhs, **assigments) - node.rhs.value.handler.assign(node.rhs, **assigments)

    @staticmethod
    def simplify(node: tree.BiTree):
        ...

class MultiplicationHandler(TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree | object):
        return node.lhs.value.handler.evaluate(node.lhs) * node.rhs.value.handler.evaluate(node.rhs)
    
    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        return node.lhs.value.handler.assign(node.lhs, **assigments) * node.rhs.value.handler.assign(node.rhs, **assigments)

    @staticmethod
    def simplify(node: tree.BiTree):
        ...

class DivisionHandler(TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree | object):
        return node.lhs.value.handler.evaluate(node.lhs) / node.rhs.value.handler.evaluate(node.rhs)
    
    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        return node.lhs.value.handler.assign(node.lhs, **assigments) / node.rhs.value.handler.assign(node.rhs, **assigments)

    @staticmethod
    def simplify(node: tree.BiTree):
        ...

class ExponantiationHandler(TokenHandler):
    @staticmethod
    def evaluate(node: tree.BiTree | object):
        return node.lhs.value.handler.evaluate(node.lhs) ** node.rhs.value.handler.evaluate(node.rhs)
    
    @staticmethod
    def assign(node: tree.BiTree, **assigments):
        return node.lhs.value.handler.assign(node.lhs, **assigments) ** node.rhs.value.handler.assign(node.rhs, **assigments)

    @staticmethod
    def simplify(node: tree.BiTree):
        ...

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
        ...

TOKENS = [
    Token('NUMBER', r'-?\d+(\.\d*)?j?[' + ''.join(list(KNOWN_MAGNITUDES.keys())) + r']?', NumberHandler),
    Token('EQUAL', r'=', None, priority=1),
    Token('ADD', r'\+', AdditionHandler, priority=2),
    Token('SUB', r'-', SubtractionHandler, priority=2),
    Token('POW', r'\^|\*\*', ExponantiationHandler, priority=4),
    Token('MUL', r'\*|\.', MultiplicationHandler, priority=3),
    Token('DIV', r'/', DivisionHandler, priority=3),
    Token('O_PAREN', r'\(', None),
    Token('C_PAREN', r'\)', None),
    Token('PAREN_BACK', r'\]', None),
    Token('FUNC_L', r'as [' + ''.join(list(KNOWN_MAGNITUDES.keys())) + r']', MagnitudeCastHandler),
    Token('FUNC_R', r'|'.join(list(KNOWN_FUNCTIONS)), None),
    Token('CONST', r'|'.join(list(KNOWN_CONSTANTS)), ConstHandler),
    Token('NAME', r'[a-zA-Z_]+', NamedVariableHandler),
    Token('NEWLINE', r'\n', None),
    Token('SKIP', r'[ \t]+', None),
    Token('MISMATCH', r'.', None),
]

