# resolve function: takes a node and a scope
# adds decls to scope, maybe creates new own scope, recurses when necessary
# tries resolving references from scope, errors if referencing something that doesnt exist

from __future__ import annotations
from dataclasses import dataclass

import Lib
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
        match key in self.members.keys():
            case True: return self.members[key]
            case False:
                if self.parent is None:
                    raise Exception(f"{key} does not exist in this scope.")
                return self.parent[key]

    def __setitem__(self, key, value):
        self.members[key] = value

@dataclass
class FunctionCallable:
    slots: list[str] # identifiers
    body: Block

class ValueSlot: pass

def resolve(scope, tree: Node):
    match tree:

        case None: return None

        case Reference(name): # ✔
            if name.lexeme in scope:
                return scope[name.lexeme]
            else:
                raise Exception(f"Cannot reference '{name.lexeme}' because it does not exist in current scope.")

        case UnaryMinus(arg): # ✔
            return UnaryMinus(resolve(scope, arg))

        case UnaryBang(arg): # ✔
            return UnaryBang(resolve(scope, arg))

        case BinaryPlus(left, right): # ✔
            return BinaryPlus(resolve(scope, left), resolve(scope, right))

        case BinaryMinus(left, right):
            return BinaryMinus(resolve(scope, left), resolve(scope, right))

        case BinaryStar(left, right): # ✔
            return BinaryStar(resolve(scope, left), resolve(scope, right))

        case BinarySlash(left, right):
            return BinarySlash(resolve(scope, left), resolve(scope, right))

        case BinaryLeftShift(left, right):
            return BinaryLeftShift(resolve(scope, left), resolve(scope, right))

        case BinaryRightShift(left, right):
            return BinaryRightShift(resolve(scope, left), resolve(scope, right))

        case BinaryLessThan(left, right):
            return BinaryLessThan(resolve(scope, left), resolve(scope, right))

        case BinaryLessEquals(left, right):
            return BinaryLessEquals(resolve(scope, left), resolve(scope, right))

        case BinaryGreaterThan(left, right):
            return BinaryGreaterThan(resolve(scope, left), resolve(scope, right))

        case BinaryGreaterEquals(left, right):
            return BinaryGreaterEquals(resolve(scope, left), resolve(scope, right))

        case BinaryEquals(left, right):
            return BinaryEquals(resolve(scope, left), resolve(scope, right))

        case BinaryNotEquals(left, right):
            return BinaryNotEquals(resolve(scope, left), resolve(scope, right))

        case VariableDeclaration(name, value): # ✔
            scope[name.lexeme] = VariableDeclaration(name, resolve(scope, value))
            return scope[name.lexeme]

        case ValueDeclaration(name, value):
            scope[name.lexeme] = ValueDeclaration(name, resolve(scope, value))
            return scope[name.lexeme]

        case VariableAssignment(name, value):
            if name.lexeme in scope:
                match scope[name.lexeme]:
                    case VariableDeclaration(_, _):
                        return VariableAssignment(name, resolve(scope, value))
                    case ValueDeclaration(_, _):
                        raise Exception(f"Cannot assign value to '{name.lexeme}' because it is immutable.")
            raise Exception(f"Cannot assign value to '{name.lexeme}' because it does not exist in current scope.")

        case AnonymousFunction(args, body):
            return FunctionCallable(args, resolve(Scope(scope, { arg: ValueSlot() for arg in args }), body))

        case FunctionDeclaration(name, args, body):
            scope[name.lexeme] = FunctionCallable(args, None) # forward declaration for recursion 🥶
            scope[name.lexeme].body =  resolve(Scope(scope, { arg.lexeme: ValueSlot() for arg in args }), body)
            return scope[name.lexeme]

        case Block(stmts):
            block_scope = Scope(scope, {})
            return Block([resolve(block_scope, stmt) for stmt in stmts])

        case FunctionCall(callee, args):
            # we can only do analysis when we know that the callee is a callable.
            res = resolve(scope, callee)
            match res:
                case FunctionCallable(slots, _):
                    ls = len(slots)
                    la = len(args)
                    match Lib.compare(ls, la):
                        case Lib.Ordering.GREATER: raise Exception(f"Not enough arguments: expected {ls}, found {la}.")
                        case Lib.Ordering.EQUAL: return FunctionCall(res, [resolve(scope, arg) for arg in args])
                        case Lib.Ordering.LESS: raise Exception(f"Too many arguments: expected {ls}, found {la}.")
                case _:
                    return FunctionCall(res, [resolve(scope, arg) for arg in args])

        case Return(expr):
            return Return(resolve(scope, expr))

        case File(stmts):
            return File([resolve(scope, stmt) for stmt in stmts])

    return tree

@dataclass
class Value(Node):
    val: int

if __name__ == "__main__":
    s = Scope(None, {})

    import Lexer, Parser
    with open("sample.bang") as f:
        nodeeee = Parser.FileParser(Lexer.TokenLexer(f.read(), 0), 0)

    r_curr = resolve(s, nodeeee)
    print(r_curr)
    print(s)