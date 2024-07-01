
from DataTypes.Scopes import *
from DataTypes.Nodes import *
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