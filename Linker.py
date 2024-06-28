# resolve function: takes a node and a scope
# adds decls to scope, maybe creates new own scope, recurses when necessary
# tries resolving references from scope, errors if referencing something that doesnt exist

from __future__ import annotations
from dataclasses import dataclass

from DataTypes.Nodes import *


@dataclass
class Scope:
    parent: Scope | None
    members: dict

    def __contains__(self, item):
        match item in self.members.keys():
            case True: return True
            case False: return False if self.parent is None else self.parent.__contains__(item)

    def __getitem__(self, key):
        return self.members[key]

    def __setitem__(self, key, value):
        self.members[key] = value

@dataclass
class FunctionCallable:
    slots: list[str] # identifiers
    body: Block

class ValueSlot: pass

def resolve(scope, tree: Node):
    match tree:
        case Reference(name): # ✔
            if name in scope:
                return scope.members[name]
            else:
                raise Exception(f"{name} not found in current scope.")

        case UnaryMinus(arg): # ✔
            return UnaryMinus(resolve(scope, arg))

        case BinaryPlus(left, right): # ✔
            return BinaryPlus(resolve(scope, left), resolve(scope, right))

        case VariableDeclaration(name, value): # ✔
            scope[name] = value

        case FunctionDeclaration(name, args, body):
            func_scope = Scope(scope, {})
            for arg in args:
                func_scope[arg] = ValueSlot()

            scope[name] = FunctionCallable(args, resolve(func_scope, body))

        case Block(stmts):
            block_scope = Scope(scope, {})
            return Block([resolve(block_scope, stmt) for stmt in stmts])

    return tree

@dataclass
class Value(Node):
    val: int

if __name__ == "__main__":
    scope = Scope(None, {})

    var = VariableDeclaration("Test", Value(20)) # var Test = 20

    resolve(scope, var)

    node = BinaryPlus(Reference("Test"), Reference("Test")) #  Test + Test

    out = resolve(scope, node)
    print(out)
    print(out.left is out.right)