from typing import Iterable

from Consumers import GenericConsumers
from Consumers.TokenConsumers import token
from Consumers.Consumer import Consume, ConsumeError, ConsumeSuccess, ConsumeResult
from DataTypes.Nodes import *
from DataTypes.Tokens import TokenType
from Lib import reduce

ExpressionParser = Consume(lambda: None) # forward declaration.

PrimaryParser = token(TokenType.IDENTIFIER) \
              | token(TokenType.NUMBER) \
              | token(TokenType.STRING) \
              | token(TokenType.NULL) \
              | token(TokenType.TRUE) \
              | token(TokenType.FALSE) \
              | (token(TokenType.LEFTPARENTOKEN) >> ExpressionParser << token(TokenType.RIGHTPARENTOKEN))

unaries = lambda tokens: reduce([unary_parser(tkn, node) for tkn, node in tokens], Consume.__or__)

unary_parser= lambda to_match, node: (token(to_match) >> PrimaryParser).penetrate(node)

def binary(element, to_match: TokenType, node) -> Consume[Token]:
    operator = token(to_match)
    def consume(collection: Iterable[Token], pos: int) -> ConsumeResult[Token]:
        match element(collection, pos):
            case ConsumeError(rest, desc, pos):
                return ConsumeError(rest, desc, pos)
            case ConsumeSuccess(rest, parsed, pos):
                curr = ConsumeSuccess(rest, parsed, pos)
                while True:
                    match operator(rest, pos):
                        case ConsumeError(_, _, _):
                            break
                        case ConsumeSuccess(rest, _, pos):
                            match element(rest, pos):
                                case ConsumeError(rest, desc, pos):
                                    return ConsumeError(rest, desc, pos)
                                case ConsumeSuccess(rest, parsed, pos):
                                    curr = ConsumeSuccess(rest, node(curr.parsed, parsed), pos)
                return curr
    return Consume(consume)

binaries = lambda element, operators: reduce([binary(element, op, node) for op, node in operators], Consume.__or__)

UnaryTokens = [(TokenType.BANG, UnaryBang),
               (TokenType.MINUS, UnaryMinus)]
UnaryParser = unaries(UnaryTokens) | PrimaryParser

FactorTokens = [(TokenType.STAR, BinaryStar),
                (TokenType.SLASH, BinarySlash)]
FactorParser = binaries(UnaryParser, FactorTokens) | UnaryParser

TermTokens = [(TokenType.PLUS, BinaryPlus),
              (TokenType.MINUS, BinaryMinus)]
TermParser = binaries(FactorParser, TermTokens) | FactorParser

ShiftTokens = [(TokenType.LEFTSHIFT, BinaryLeftShift),
               (TokenType.RIGHTSHIFT, BinaryRightShift)]
ShiftParser = binaries(TermParser, ShiftTokens) | TermParser

ComparisonTokens = [(TokenType.LESS, BinaryLessThan),
                    (TokenType.LESSEQUALS, BinaryLessEquals),
                    (TokenType.GREATER, BinaryGreaterThan),
                    (TokenType.GREATEREQUALS, BinaryGreaterEquals)]
ComparisonParser = binaries(ShiftParser, ComparisonTokens) | ShiftParser # redundant since binary allows single element?

# here we override the instance method and not the entire instance.
# this overrides the referenced function and supplies the actual definition.
# this allows us to create infinitely nested non left or right recursive (primitive?) parsers.
ExpressionParser.consume = (ComparisonParser).consume