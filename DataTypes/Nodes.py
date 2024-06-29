from dataclasses import dataclass

from DataTypes.Tokens import Token


class Node: pass

@dataclass
class UnaryMinus(Node):
    value: Node

@dataclass
class UnaryBang(Node):
    value: Node

@dataclass
class BinaryPlus(Node):
    left: Node
    right: Node

@dataclass
class BinaryMinus(Node):
    left: Node
    right: Node

@dataclass
class BinaryStar(Node):
    left: Node
    right: Node

@dataclass
class BinarySlash(Node):
    left: Node
    right: Node

@dataclass
class BinaryLeftShift(Node):
    left: Node
    right: Node

@dataclass
class BinaryRightShift(Node):
    left: Node
    right: Node

@dataclass
class BinaryLessThan(Node):
    left: Node
    right: Node

@dataclass
class BinaryLessEquals(Node):
    left: Node
    right: Node

@dataclass
class BinaryGreaterThan(Node):
    left: Node
    right: Node

@dataclass
class BinaryGreaterEquals(Node):
    left: Node
    right: Node

@dataclass
class BinaryEquals(Node):
    left: Node
    right: Node

@dataclass
class BinaryNotEquals(Node):
    left: Node
    right: Node

# this is the base identifier when its not surrounded by other identifying shit like var/val/fun
@dataclass
class Reference(Node):
    name: Token

@dataclass
class Block(Node):
    stmts: list[Node]

@dataclass
class FunctionDeclaration(Node):
    name: Token # = Identifier
    args: list[Token] # = Identifiers
    body: Block

@dataclass
class AnonymousFunction(Node):
    args: list[Token]
    body: Block

@dataclass
class VariableDeclaration(Node):
    name: Token
    value: Node

@dataclass
class ValueDeclaration(Node):
    name: Token
    value: Node
@dataclass
class VariableAssignment(Node):
    name: Token
    value: Node

@dataclass
class While(Node):
    condition: Node | Token
    stmt: Node

@dataclass
class Else(Node):
    stmt: Node

@dataclass
class If(Node):
    cond: Node | Token
    stmt: Node
    otherwise: Else | None = None

@dataclass
class Return(Node):
    value: Node | None = None

@dataclass
class FunctionCall(Node):
    callee: Node
    args: list[Node]
