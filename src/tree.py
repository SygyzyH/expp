from dataclasses import dataclass

@dataclass
class BiTree:
    lhs: "BiTree"
    rhs: "BiTree"
    value: object
