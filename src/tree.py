from dataclasses import dataclass
from functools import cache

@dataclass
class BiTree:
    lhs: "BiTree"
    rhs: "BiTree"
    value: object

    def __repr__(self, depth=1) -> str:
        tabs = '\t' * depth
        external_tabs = '\t' * (depth - 1)
        string = f"{external_tabs}BiTree(\n{tabs}{self.value}\n"
        if self.lhs is not None:
            string += f"{tabs}l:\n{self.lhs.__repr__(depth + 1)}\n"
        if self.rhs is not None:
            string += f"{tabs}r:\n{self.rhs.__repr__(depth + 1)}\n"
        return string + external_tabs + ")"
    
    @property
    @cache
    def depth(self):
        depth = 0
        
        if self.lhs is not None:
            depth += self.lhs.depth + 1
        if self.rhs is not None:
            depth += self.rhs.depth + 1

        return depth
