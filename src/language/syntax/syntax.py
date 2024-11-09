from dataclasses import dataclass
from abc import ABC, abstractmethod
import math
import copy

import language.base as base
import utils.tree as tree

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
    "Tb": 1e9 * 2**10,
    "Gb": 1e6 * 2**10,
    "Mb": 1e3 * 2**10,
    "kb": 2**10,
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
        return f"{self.__class__.__name__}(value={self.value.__repr__()}, ({self.line}, {self.column}), priority={self.priority})"

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

import language.syntax.tokens.end_statment as end_statment
import language.syntax.tokens.directive as directive
import language.syntax.tokens.expression_history as expression_history
import language.syntax.tokens.result_history as result_history
import language.syntax.tokens.number as number
import language.syntax.tokens.equal as equal
import language.syntax.tokens.add as add
import language.syntax.tokens.subtract as subtract
import language.syntax.tokens.multiply as multiply
import language.syntax.tokens.divide as divide
import language.syntax.tokens.power as power
import language.syntax.tokens.open_parenthesis as open_parenthesis
import language.syntax.tokens.close_parenthesis as close_parenthesis
import language.syntax.tokens.back_parenthesis as back_parenthesis
import language.syntax.tokens.left_function as left_function
import language.syntax.tokens.right_function as right_function
import language.syntax.tokens.constant as constant
import language.syntax.tokens.name as name
import language.syntax.tokens.comment as comment
import language.syntax.tokens.newline as newline
import language.syntax.tokens.skip as skip
import language.syntax.tokens.mismatch as mismatch

BASE_TOKENS = [
    end_statment.EndStatement(),
    directive.Directive(),
    expression_history.ExpressionHistory(),
    result_history.ResultHistory(),
    number.Number(),
    equal.Equal(),
    add.Add(),
    subtract.Subtract(),
    power.Power(),
    multiply.Multiply(),
    divide.Divide(),
    open_parenthesis.OpenParenthesis(),
    close_parenthesis.CloseParenthesis(),
    back_parenthesis.BackParenthesis(),
    left_function.LeftFunction(),
    right_function.RightFunction(),
    constant.Constant(),
    name.Name(),
    comment.Comment(),
    newline.Newline(),
    skip.Skip(),
    mismatch.Mismatch(),
]

def default_token(name: str):
    return copy.copy(next(_ for _ in BASE_TOKENS if _ == name))