from dataclasses import dataclass

from DataTypes.Tokens import Token


class Node: pass

@dataclass
class UnaryMinus(Node):
    value: Node | Token

@dataclass
class UnaryBang(Node):
    value: Node | Token

@dataclass
class BinaryPlus(Node):
    left: Node | Token
    right: Node | Token

@dataclass
class BinaryMinus(Node):
    left: Node | Token
    right: Node | Token

@dataclass
class BinaryStar(Node):
    left: Node | Token
    right: Node | Token

@dataclass
class BinarySlash(Node):
    left: Node | Token
    right: Node | Token

@dataclass
class BinaryLeftShift(Node):
    left: Node | Token
    right: Node | Token

@dataclass
class BinaryRightShift(Node):
    left: Node | Token
    right: Node | Token

@dataclass
class BinaryLessThan(Node):
    left: Node | Token
    right: Node | Token

@dataclass
class BinaryLessEquals(Node):
    left: Node | Token
    right: Node | Token

@dataclass
class BinaryGreaterThan(Node):
    left: Node | Token
    right: Node | Token

@dataclass
class BinaryGreaterEquals(Node):
    left: Node | Token
    right: Node | Token

@dataclass
class BinaryEquals(Node):
    left: Node | Token
    right: Node | Token

@dataclass
class BinaryNotEquals(Node):
    left: Node | Token
    right: Node | Token
