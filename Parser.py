from types import NoneType
from typing import Iterable, Self

from Consumers import GenericConsumers
from Consumers.TokenConsumers import token
from Consumers.Consumer import Consume, ConsumeError, ConsumeSuccess, ConsumeResult
from DataTypes.Nodes import *
from DataTypes.Tokens import TokenType
from Lib import reduce

ExpressionParser = Consume(lambda: None) # forward declaration.
StatementParser = Consume(lambda: None) # same here.
DeclarationParser = Consume(lambda: None) # and here.

PrimaryParser = token(TokenType.IDENTIFIER).penetrate(Reference) \
              | token(TokenType.NUMBER).penetrate(lambda v: Literal(v, int)) \
              | token(TokenType.STRING).penetrate(lambda v: Literal(v, str)) \
              | token(TokenType.NULL).penetrate(lambda v: Literal(v, NoneType)) \
              | token(TokenType.TRUE).penetrate(lambda v: Literal(v, bool)) \
              | token(TokenType.FALSE).penetrate(lambda v: Literal(v, bool)) \
              | (token(TokenType.LEFTPARENTOKEN) >> ExpressionParser << token(TokenType.RIGHTPARENTOKEN))

CommaDelExprsParser = token(TokenType.LEFTPARENTOKEN) >> ExpressionParser.delimited(token(TokenType.COMMA)).optional() << token(TokenType.RIGHTPARENTOKEN)

def parse_function_call(collection, pos):
    match PrimaryParser(collection, pos):
        case ConsumeError(rest, desc, pos): return ConsumeError(rest, desc, pos)
        case ConsumeSuccess(rest, parsed, pos):
            curr = ConsumeSuccess(rest, parsed, pos)
            while True:
                match CommaDelExprsParser(rest, pos):
                    case ConsumeError(_, _, _): break
                    case ConsumeSuccess(rest, parsed, pos):
                        curr = ConsumeSuccess(rest, FunctionCall(curr.parsed, parsed), pos)
            return curr

FunctionCallParser = Consume(parse_function_call)

unaries = lambda tokens: reduce([unary_parser(tkn, node) for tkn, node in tokens], Consume.__or__)

unary_parser = lambda to_match, node: (token(to_match) >> FunctionCallParser).penetrate(node)

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
UnaryParser = unaries(UnaryTokens) | FunctionCallParser

FactorTokens = [(TokenType.STAR, BinaryStar),
                (TokenType.SLASH, BinarySlash)]
FactorParser = binaries(UnaryParser, FactorTokens)

TermTokens = [(TokenType.PLUS, BinaryPlus),
              (TokenType.MINUS, BinaryMinus)]
TermParser = binaries(FactorParser, TermTokens)

ShiftTokens = [(TokenType.LEFTSHIFT, BinaryLeftShift),
               (TokenType.RIGHTSHIFT, BinaryRightShift)]
ShiftParser = binaries(TermParser, ShiftTokens)

ComparisonTokens = [(TokenType.LESS, BinaryLessThan),
                    (TokenType.LESSEQUALS, BinaryLessEquals),
                    (TokenType.GREATER, BinaryGreaterThan),
                    (TokenType.GREATEREQUALS, BinaryGreaterEquals)]
ComparisonParser = binaries(ShiftParser, ComparisonTokens)

EqualityTokens = [(TokenType.DEQUALS, BinaryEquals),
                  (TokenType.NOTEQUALS, BinaryNotEquals)]
EqualityParser = binaries(ComparisonParser, EqualityTokens)

ArgsParser = token(TokenType.LEFTPARENTOKEN) >> token(TokenType.IDENTIFIER).delimited(token(TokenType.COMMA)).optional() << token(TokenType.RIGHTPARENTOKEN)

AnonFunctionParser = ((ArgsParser << token(TokenType.BIND)) + StatementParser).penetrate(lambda l: AnonymousFunction(*l))

ReturnParser = (token(TokenType.RETURN) >> ExpressionParser.optional()).penetrate(Return)

VariableAssParser = ((token(TokenType.IDENTIFIER) << token(TokenType.EQUALS)) + ExpressionParser).penetrate(lambda l: VariableAssignment(*l))

BlockParser = (token(TokenType.LEFTBRACETOKEN) >> DeclarationParser.continuous().optional() << token(TokenType.RIGHTBRACETOKEN)).penetrate(Block)

ElseParser = (token(TokenType.ELSE) >> StatementParser).penetrate(Else)

IfParser = ((token(TokenType.IF) >> ExpressionParser) + StatementParser + ElseParser.optional()).penetrate(lambda l: If(*l))

WhileParser = ((token(TokenType.WHILE) >> ExpressionParser) + StatementParser).penetrate(lambda l: While(*l))

VariableDeclParser = ((token(TokenType.VAR) >> token(TokenType.IDENTIFIER) << token(TokenType.EQUALS)) + ExpressionParser).penetrate(lambda l: VariableDeclaration(*l))

ValueDeclParser = ((token(TokenType.VAL) >> token(TokenType.IDENTIFIER) << token(TokenType.EQUALS)) + ExpressionParser).penetrate(lambda l: ValueDeclaration(*l))

def funcdecl(l):
    name, *args, stmt = l
    return FunctionDeclaration(name, args, stmt)

FunctionDeclParser = ((token(TokenType.FUN) >> token(TokenType.IDENTIFIER))
                     +(ArgsParser << token(TokenType.BIND))
                     + StatementParser).penetrate(funcdecl)

ClassDeclParser = ...



# here we override the instance method and not the entire instance.
# this overrides the referenced function and supplies the actual definition,
# which allows us to create infinitely nested non left or right recursive (primitive?) parsers.
ExpressionParser.consume = (AnonFunctionParser | EqualityParser).consume
StatementParser.consume = (IfParser | WhileParser | ReturnParser | VariableAssParser | BlockParser | ExpressionParser).consume
DeclarationParser.consume = (FunctionDeclParser | ValueDeclParser | VariableDeclParser | StatementParser).consume


FileParser = DeclarationParser.continuous().penetrate(File)

# Expressions
# function call: expr ( exprs )
# operators ✔
# anonymous function: (a) -> {b} ✔
# if: {a} if (b) else {c} ✔
# identifier: a ✔
# literals: 123, "a" ✔ maybe more
# block: {stmts +expr} maybe
# match: match a { (b -> {c})+ } maybe

# Declarations
# variable: var a = b where b is expr ✔
# value: val a = b ✔
# function def: fun a (b) -> {c} ✔

# Statements
# if: if (a) {b} else [ifstmt]
# while loop: while cond -> {a} ✔
# block: {stmts} ✔
# return: return a
# for loop: for a in b {c}
# match: match a { (b -> {c})+ }