import Lib
from DataTypes.Scopes import *
from DataTypes.Nodes import *
from Linker import FunctionCallable

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


# technically eval and exec
def evaluate(scope, tree):

    match tree:
        case Literal(value, t):
            return value.literal

        case UnaryMinus(value):
            return -evaluate(scope, value)

        case UnaryBang(value):
            return not evaluate(scope, value)

        case BinaryPlus(left, right):
            return evaluate(scope, left) + evaluate(scope, right)

        case BinaryMinus(left, right):
            return evaluate(scope, left) - evaluate(scope, right)

        case BinaryStar(left, right): # ✔
            return evaluate(scope, left) * evaluate(scope, right)

        case BinarySlash(left, right):
            return evaluate(scope, left) / evaluate(scope, right)

        case BinaryLeftShift(left, right):
            return evaluate(scope, left) << evaluate(scope, right)

        case BinaryRightShift(left, right):
            return evaluate(scope, left) >> evaluate(scope, right)

        case BinaryLessThan(left, right):
            return evaluate(scope, left) < evaluate(scope, right)

        case BinaryLessEquals(left, right):
            return evaluate(scope, left) <= evaluate(scope, right)

        case BinaryGreaterThan(left, right):
            return evaluate(scope, left) > evaluate(scope, right)

        case BinaryGreaterEquals(left, right):
            return evaluate(scope, left) >= evaluate(scope, right)

        case BinaryEquals(left, right):
            return evaluate(scope, left) == evaluate(scope, right)

        case BinaryNotEquals(left, right):
            return evaluate(scope, left) != evaluate(scope, right)

        case If(cond, stmt, otherwise):
            if evaluate(scope, cond):
                evaluate(scope, stmt)
            else:
                evaluate(scope, otherwise)

        case Else(stmt):
            evaluate(scope, stmt)

        case While(cond, stmt):
            while evaluate(scope, cond):
                evaluate(scope, stmt)

        case Block(stmts):
            block_scope = Scope(scope, {})
            for stmt in stmts:
                evaluate(block_scope, stmt)

        case Return(expr):
            raise ReturnException(value= evaluate(scope, expr))

        case ValueDeclaration(name, value):
            scope[name.lexeme] = evaluate(scope, value)

        case VariableDeclaration(name, value):
            scope[name.lexeme] = evaluate(scope, value)

        case VariableAssignment(name, value):
            # this is always safe since the linker takes care of illegal assignments
            scope[name.lexeme] = evaluate(scope, value)

        case Reference(name):
            # similar to assignment, linker nags you about illegal references
            return scope[name.lexeme]

        case FunctionDeclaration(name, args, body):
            scope[name.lexeme] = FunctionCallable(args, body)

        case AnonymousFunction(args, body):
            return FunctionCallable(args, body)

        case File(stmts):
            match stmts:
                case [single]:
                    return evaluate(scope, single)
                case [*multiple]:
                    for stmt in multiple:
                        evaluate(scope, stmt)

        case FunctionCall(callee, args):
            match evaluate(scope, callee):
                case FunctionCallable(slots, body):
                    la = len(args)
                    ls = len(slots)
                    match Lib.compare(la, ls):
                        case Lib.Ordering.LESS: raise Exception(f"Not enough arguments given, expected {ls}, got {la}")
                        case Lib.Ordering.GREATER: raise Exception(f"Too many arguments given, expected {ls}, got {la}")
                        case Lib.Ordering.EQUAL:
                            temp_scope = Scope(scope, { slot.lexeme: evaluate(scope, args[i]) for i, slot in enumerate(slots) })
                            try:
                                evaluate(temp_scope, body)
                            except ReturnException as re:
                                return re.value
                case _:
                    raise Exception(f"Illegal callee: {callee}")