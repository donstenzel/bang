from __future__ import annotations
import sys
from typing import Iterable, Callable

type ParserSuccess[T] = tuple[Iterable[T], T, int]
type ParserError[T] = tuple[Iterable[T], str, int]
type ParserResult[T] = ParserSuccess[T] | ParserError[T]
type ParserFunction[T] = Callable[[Iterable[T], int], ParserResult[T]]

# Parser Combinator


def collapse(string):
    return ''.join(string)


def reduce[T](items: Iterable[T], agg: Callable[[T, T], T], start: T) -> T:
    out = start
    for item in items:
        out = agg(out, item)
    return out


def flatten(*items):
    out = []
    for item in items:
        match item:
            case [*a]:
                out.extend(a)
            case None:
                pass
            case a:
                out.append(a)
    return out


# no errors for now.
type ParseSuccess[T] = tuple[Iterable[T], T]
type ParseResult[T] = ParseSuccess[T] | None
type ParserFunction[T] = Callable[[Iterable[T]], ParseResult[T]]


class Parser[T]:
    """A Parser that tries consuming a T from an Iterable[T], and returns (Rest, T) upon success."""

    def __init__(self, parse: ParserFunction[T]) -> None:
        self.parse = parse

    def __add__(self, other: Parser[T]) -> Parser[T]:
        """Parses 2 parsers in sequence and combines their results"""

        def parse(collection: Iterable[T]) -> ParseResult[T]:
            match self.parse(collection):
                case [rest1, parsed1]:
                    match other.parse(rest1):
                        case [rest2, parsed2]:
                            return (rest2, flatten(parsed1, parsed2))
                        case None:
                            return None
                case None:
                    return None
            raise Exception("__add__: Parser returned faulty result.")

        return Parser(parse)

    def __lshift__(self, other: Parser[T]) -> Parser[T]:
        """Parses 2 parsers in sequence and discards the right> result."""

        def parse(collection: Iterable[T]) -> ParseResult[T]:
            match self.parse(collection):
                case [rest1, parsed]:
                    match other.parse(rest1):
                        case [rest2, _]:
                            return (rest2, parsed)
                        case None:
                            return None
                case None:
                    return None
            raise Exception("__lshift__: Parser returned faulty result.")

        return Parser(parse)

    def __rshift__(self, other: Parser[T]) -> Parser[T]:
        """Parses 2 parsers in sequence and discards the <left result."""

        def parse(collection: Iterable[T]) -> ParseResult[T]:
            match debug1 := self.parse(collection):
                case [rest1, _]:
                    match debug2 := other.parse(rest1):
                        case [rest2, parsed]:
                            return (rest2, parsed)
                        case None:
                            return None
                case None:
                    return None
            raise Exception('__rshift__: Parser returned faulty result.')

        return Parser(parse)

    def __or__(self, other: Parser[T]) -> Parser[T]:
        """Parses left parser, returns result if it succeeds. If not, parses right parser and returns its result"""

        def parse(collection: Iterable[T]) -> ParseResult[T]:
            match self(collection):
                case None:
                    return other(collection)
                case val:
                    return val

        return Parser(parse)

    def __xor__(self, other: Parser[T]) -> Parser[T]:
        def parse(collection: Iterable[T]) -> ParseResult[T]:
            match (self.parse(collection), other.parse(collection)):
                case (result, None) | (None, result):
                    return result
                case (None, None):
                    return None
                case (_, _):
                    raise Exception("__xor__: Both parsers returned results -> Ambiguous match.")

        return Parser(parse)

    def iterated(self) -> Parser[T]:
        """Parser that consumes its subject as often as possible, returns none if 0 results."""

        def parse(collection: Iterable[T]) -> ParseResult[T]:
            rest = collection
            parsedL = []
            while (result := self.parse(rest)) != None:
                rest, parsed = result
                parsedL.append(parsed)
            if parsedL == []: return None
            return (rest, parsedL)

        return Parser(parse)

    def seperated(self, sep: Parser[T]) -> Parser[T]:
        """Parses like .iterated(), but with a seperator."""
        return (self << (padding + sep.optional() + padding)).iterated()

    def bracket(self, left: Parser[T], right: Parser[T]) -> Parser[T]:
        """Parses left delimiter, main and right delimiter, then returns only main."""
        return (left + padding) >> self << (padding + right)

    def bracket_no_padding(self, left: Parser[T], right: Parser[T]) -> Parser[T]:
        """Parses left delimiter, main and right delimiter, then returns only main."""
        return left >> self << right

    def collection(self, sep: Parser[T], left: Parser[T], right: Parser[T]) -> Parser[T]:
        """Parser that combines .seperated() and .bracket()"""
        return self.seperated(sep).bracket(left, right)

    def key(self, sep: Parser[T], key: Parser[T]) -> Parser[T]:
        """Parses a key value pair, returning key and value. Call this on the *value* parser."""
        return (key << (padding + sep + padding)) + self

    def value(self, sep: Parser[T], value: Parser[T]) -> Parser[T]:
        """Parses a key value pair, returning key and value. Call this on the *key* parser."""
        return (self << (padding + sep + padding)) + value

    def penetrate(self, func: Callable[[T], Any]) -> Parser[T]:
        """Injects a function to be applied to the parsed object before returning it with the rest."""

        def parse(collection: Iterable[T]) -> ParseResult[T]:
            match self.parse(collection):
                case [rest, parsed]:
                    match func(parsed):
                        case None:
                            return None
                        case converted:
                            return (rest, converted)
                case None:
                    return None

        return Parser(parse)

    def conversion(self) -> Parser[T]:
        def parse(string):
            match self(string):
                case [head, *tail]:
                    return [head] + tail
                case None:
                    return None

        return Parser(parse)

    def padded(self) -> Parser[T]:
        return padding >> self << padding

    def optional(self):
        """Makes the parser optional by always succeeding."""

        def parse(collection: Iterable[T]) -> ParseResult[T]:
            match self.parse(collection):
                case [rest, parsed]:
                    return (rest, parsed)
                case None:
                    return (collection, [])

        return Parser(parse)

    def lookahead(self, other: Parser[T]) -> Parser[T]:
        """matches p1 then peeks if p2 works. if it does None is returned. if only p1 matches it parses regularly, and if it doesnt it returns None aswell."""

        def parse(collection: Iterable[T]) -> ParseResult[T]:
            match self(collection):
                case [rest, parsed]:
                    match other(rest):
                        case None:
                            return (rest, parsed)
                        case _:
                            return None
                case None:
                    return None

        return Parser(parse)

    def __call__(self, *args, **kwds):
        """Class wraps its own parse method."""
        return self.parse(*args, *kwds)


class Parsers:

    def empty() -> Parser[str]:
        """a parser that consumes nothing and always succeeds."""

        def parse(string: str):
            return (string, '')

        return Parser(parse)

    def predicate(p: Callable[[Any], bool]) -> Parser[Any]:
        """a parser that consumes a single item if p(item) is true."""

        def parse(collection: Iterable[Any]) -> ParseResult[Any]:
            # match collection:
            #     case None: return None
            #     case head, *tail: return (tail, head) if p(head) else None
            #     case single if not isinstance(single, list): return ([], single) if p(single) else None
            if not collection: return None
            head, *tail = collection
            return (tail, head) if p(head) else None

        return Parser(parse)

    def char(char_to_parse: str) -> Parser[str]:
        """a parser that consumes a single character if it is equal to char_to_parse"""
        return Parsers.predicate(lambda c: c == char_to_parse)

    def chars(chars_to_parse: str) -> Parser[str]:
        """a parser that consumes a single character if it is equal to any of chars_to_parse"""
        return Parsers.predicate(lambda c: c in chars_to_parse)

    def not_chars(chars_to_not_parse: str) -> Parser[str]:
        """a parser that consumes a single character if it is not equal to any of chars_to_not_parse"""
        return Parsers.predicate(lambda c: c not in chars_to_not_parse)

    def string(string_to_parse: str) -> Parser[str]:
        """a parser that consumes string_to_parse if possible"""
        head, *tail = [Parsers.char(c) for c in string_to_parse]
        return reduce(tail, Parser.__add__, head)

    def whitespace() -> Parser[str]:
        """a parser for whitespace"""
        return (Parsers.char(' ') | Parsers.char('\n')).iterated()

    def padding() -> Parser[str]:
        """a parser that matches 0 or more tabs, spaces & newlines"""
        padding_chars = ' \t\n'
        return Parsers.chars(padding_chars).iterated().optional()

    def unconditional():
        def parse(collection):
            match collection:
                case [head, *tail]:
                    return (tail, head)
                case []:
                    return None

        return Parser(parse)


padding = Parsers.padding()

if __name__ == "__main__":

    LAngleBracketParser = Parsers.char('<')
    RAngleBracketParser = Parsers.char('>')
    SlashParser = Parsers.char('/')

    XmlNameParser = Parsers \
        .predicate(lambda c: c not in ['>', '<']) \
        .iterated() \
        .penetrate(lambda cs: ''.join(cs))


    def interpretXmlKvp(kvp):
        match kvp:
            case [key1, value, key2] if key1 == key2:
                return {key1: value}
            case [key1, value, key2]:
                return None
            case _:
                raise Exception("should never be reached!")


    XmlKeyValueParser = (
            XmlNameParser.bracket(LAngleBracketParser, RAngleBracketParser)
            + XmlNameParser
            + XmlNameParser.bracket(LAngleBracketParser + SlashParser, RAngleBracketParser)
    ).penetrate(interpretXmlKvp)

# !/usr/bin/python3

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import sys
from typing import Any
from parzerker import Parser, Parsers, collapse, padding, reduce


# Tokens: Literals, Keywords, Operators, Grouping
# Grouping: '(' ')' '{' '}' '[' ']'
# Operators: + - * / % & | < > = == <= >= ! != << >> |> . : (maybe $ ~ # · † ) [+]
# Literals: String, Number, Identifier, Comment [+]

@dataclass
class Token:
    token: TokenType
    lexeme: str
    literal: Any


class TokenType(Enum):
    # Grouping
    LEFTPARENTOKEN = 0  # (
    RIGHTPARENTOKEN = 1  # )
    LEFTBRAKETTOKEN = 2  # [
    RIGHTBRACKETTOKEN = 3  # ]
    LEFTBRACETOKEN = 4  # {
    RIGHTBRACETOKEN = 5  # }

    # Single Character Operators
    PLUS = 6  # +
    MINUS = 7  # -
    STAR = 8  # *
    SLASH = 9  # /
    PERCENT = 10  # %
    AND = 11  # &
    OR = 12  # |
    LESS = 13  # <
    GREATER = 14  # >
    EQUALS = 15  # =
    BANG = 16  # !
    DOT = 17  # .
    QUESTIONMARK = 18  # ?
    COMMA = 19  # ,
    COLON = 20  # :

    # Double Character Operators
    DEQUALS = 21  # ==
    LESSEQUALS = 22  # <=
    GREATEREQUALS = 23  # >=
    NOTEQUALS = 24  # !=
    LEFTSHIFT = 25  # <<
    RIGHTSHIFT = 26  # >>
    PIPE = 27  # |>

    # Literals
    STRING = 28  # '"' + content + '"'
    NUMBER = 29  # some number of numeric chars in a row, for now just ints. but simple to fix - just copy the float parser from jsonparser
    COMMENT = 30  # //... until end of line
    IDENTIFIER = 31  # alphabetic chars + _ that dont match anything else

    # Keywords
    IF = 32  # if
    ELSE = 33  # else
    MATCH = 34  # match
    TRUE = 35  # true
    FALSE = 36  # false
    FOR = 37  # for
    IN = 38  # in
    WHILE = 39  # while
    RETURN = 40  # return
    VAR = 41  # var
    VAL = 42  # val
    THIS = 43  # this
    CLASS = 44  # class
    FUN = 45  # fun
    NULL = 46  # null
    BASE = 47  # base


Keywords = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "match": TokenType.MATCH,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "while": TokenType.WHILE,
    "return": TokenType.RETURN,
    "var": TokenType.VAR,
    "val": TokenType.VAL,
    "this": TokenType.THIS,
    "class": TokenType.CLASS,
    "fun": TokenType.FUN,
    "null": TokenType.NULL,
    "base": TokenType.BASE
}

Unaries = [TokenType.BANG, TokenType.MINUS, TokenType.PLUS]

TokenParsers = []


class Scanner:
    global TokenParsers, Keywords

    def ConstantTokenParser(string, token):
        parser = Parsers.string(string).penetrate(lambda cs: Token(token, collapse(cs), None))
        TokenParsers.append(parser)
        return parser

    LeftParenParser = ConstantTokenParser('(', TokenType.LEFTPARENTOKEN)
    RightParenParser = ConstantTokenParser(')', TokenType.RIGHTPARENTOKEN)
    LeftBracketParser = ConstantTokenParser('[', TokenType.LEFTBRAKETTOKEN)
    RightBracketParser = ConstantTokenParser(']', TokenType.RIGHTBRACKETTOKEN)
    LeftBraceParser = ConstantTokenParser('{', TokenType.LEFTBRACETOKEN)
    RightBraceParser = ConstantTokenParser('}', TokenType.RIGHTBRACETOKEN)

    PlusParser = ConstantTokenParser('+', TokenType.PLUS)
    MinusParser = ConstantTokenParser('-', TokenType.MINUS)
    StarParser = ConstantTokenParser('*', TokenType.STAR)
    SlashParser = ConstantTokenParser('/', TokenType.SLASH)
    PercentParser = ConstantTokenParser('%', TokenType.PERCENT)
    AndParser = ConstantTokenParser('&', TokenType.AND)
    OrParser = ConstantTokenParser('|', TokenType.OR)
    LessThanParser = ConstantTokenParser('<', TokenType.LESS)
    GreaterThanParser = ConstantTokenParser('>', TokenType.GREATER)
    EqualsParser = ConstantTokenParser('=', TokenType.EQUALS)
    BangParser = ConstantTokenParser('!', TokenType.BANG)
    DotParser = ConstantTokenParser('.', TokenType.DOT)
    QuestionmarkParser = ConstantTokenParser('?', TokenType.QUESTIONMARK)
    CommaParser = ConstantTokenParser(',', TokenType.COMMA)
    ColonParer = ConstantTokenParser(':', TokenType.COLON)

    DoubleEqualsParser = ConstantTokenParser('==', TokenType.DEQUALS)
    LessEqualsParser = ConstantTokenParser('<=', TokenType.LESSEQUALS)
    GreaterEqualsParser = ConstantTokenParser('>=', TokenType.GREATEREQUALS)
    NotEqualsParser = ConstantTokenParser('!=', TokenType.NOTEQUALS)
    LeftShiftParser = ConstantTokenParser('<<', TokenType.LEFTSHIFT)
    RightShiftParser = ConstantTokenParser('>>', TokenType.RIGHTSHIFT)
    PipeParser = ConstantTokenParser('|>', TokenType.PIPE)

    # Possible new thing, interesting if we want more string like syntax pieces
    SingleQuoteParser = Parsers.char("'")
    SingleQuoteStringParser = Parsers.not_chars("'") \
        .iterated() \
        .optional() \
        .bracket_no_padding(SingleQuoteParser, SingleQuoteParser) \
        .penetrate(collapse) \
        .penetrate(lambda string: Token(TokenType.STRING, "'" + string + "'", string))

    DoubleQuoteParser = Parsers.char('"')
    DoubleQuoteStringParser = Parsers.not_chars('"') \
        .iterated() \
        .optional() \
        .bracket_no_padding(DoubleQuoteParser, DoubleQuoteParser) \
        .penetrate(collapse) \
        .penetrate(lambda string: Token(TokenType.STRING, '"' + string + '"', string))

    UnderscoreParser = Parsers.char('_')
    DigitParser = Parsers.predicate(str.isdigit)
    NumberParser = DigitParser.seperated(UnderscoreParser).penetrate(collapse).penetrate(
        lambda num: Token(TokenType.NUMBER, num, int(num)))

    CommentParser = (
            Parsers.string('//')
            >> Parsers.not_chars('\n').iterated()
            << Parsers.char('\n')
    ).penetrate(collapse) \
        .penetrate(lambda comment: Token(TokenType.COMMENT, '//' + comment + '\n', comment))

    BlockCommentParser = (
            Parsers.string('/*')
            >> (Parsers.not_chars('*') | Parsers.char('*').lookahead(Parsers.char('/'))).iterated()
            << Parsers.string('*/')
    ).penetrate(collapse) \
        .penetrate(lambda string: Token(TokenType.COMMENT, '/*' + string + '*/', string))

    def ident(string):
        if string in Keywords.keys():
            return Token(Keywords[string], string, None)
        return Token(TokenType.IDENTIFIER, string, string)

    IdentifierKeywordParser = (
            Parsers.predicate(lambda char: char.isalpha() or char == '_')
            + Parsers.predicate(lambda char: char.isalnum() or char == '_').iterated().optional()
    ).penetrate(collapse) \
        .penetrate(ident)

    TokenParsers.extend(
        [NumberParser, IdentifierKeywordParser, DoubleQuoteStringParser, SingleQuoteStringParser, CommentParser,
         BlockCommentParser])
    head, *tail = TokenParsers[::-1]
    TokenParser = (
        reduce(tail, Parser.__or__, head)
    ).seperated(padding)


def token(token_to_parse: TokenType) -> Parser[Token]:
    return Parsers.predicate(lambda t: t.token == token_to_parse)


def binaryOpTrain(element, operator):
    return element + (operator + element).iterated().optional()


def binaryTree(operator, element):
    opelem = operator + element

    def parse(tokens):
        match element(tokens):
            case None:
                return None
            case [rest, curr]:
                while (res := opelem(rest)) != None:
                    rest, [op, elem] = res
                    curr = BinaryOperation(curr, op, elem)
                return (rest, curr)

    return Parser(parse)


def cons(a, b):
    match a, b:
        case oneA, oneB:
            return [oneA, oneB]
        case oneA, [*multB]:
            return [oneA, *multB]
        case [*multA], oneB:
            return [*multA, oneB]
        case [*multA], [*multB]:
            return [*multA, *multB]


def delimited(element, delimiter):
    delimelem = delimiter >> element

    def parse(tokens):
        match element(tokens):
            case None:
                return None
            case [rest, curr]:
                while (res := delimelem(rest)) != None:
                    rest, elem = res
                    curr = cons(curr, elem)
                return (rest, curr)

    return Parser(parse)


class Node: pass


@dataclass
class PrimaryNode(Node):
    value: Token


@dataclass
class UnaryOperation(Node):
    operator: Token
    value: Token


@dataclass
class BinaryOperation(Node):
    left: Token
    operator: Token
    right: Token


@dataclass
class FunctionDefinitionNode(Node):
    name: Token
    args: list[Token]
    body: Token

    def __init__(self, args):
        head, *mid, tail = args
        self.name = head
        self.args = mid
        self.body = tail


Variables = {}


@dataclass
class VariableNode(Node):
    name: str
    value: Token
    global Variables

    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value

    def __new__(cls, name, value):
        instance = super().__new__(cls)
        Variables[name] = instance
        return instance


class AbstractSyntaxTreeParser:
    # expression     → equality ;
    # equality       → comparison ( ( "!=" | "==" ) comparison )* ;
    # comparison     → shift ( ( ">" | ">=" | "<" | "<=" ) shift )* ;
    # shift          → term ( ( ">>" | "<<" ) term )* ;
    # term           → factor ( ( "-" | "+" ) factor )* ;
    # factor         → unary ( ( "/" | "*" ) unary )* ;
    # unary          → ( "!" | "-" ) unary
    #                | primary ;
    # primary        → NUMBER | STRING | "true" | "false" | "null"
    #                | "(" expression ")" ;

    Expression = Parser(lambda: None)

    Statement = Parser(lambda: None)

    def assign(pair):
        ident, value = pair
        return VariableNode(ident.literal, value)

    Assignment = ((token(TokenType.IDENTIFIER) << token(TokenType.EQUALS)) + Expression).penetrate(assign)

    # keyword fun -> identifier name -> parenthesized comma seperated list of identifiers arguments -> braced list of expressions and statements
    # returns: name -> list of arg names -> body
    FunctionDefinition = (token(TokenType.FUN) \
                          >> token(TokenType.IDENTIFIER) \
                          + (
                                  token(TokenType.LEFTPARENTOKEN)
                                  >> delimited(token(TokenType.IDENTIFIER), token(TokenType.COMMA))
                                  << token(TokenType.RIGHTPARENTOKEN)
                          ) + (
                                  token(TokenType.LEFTBRACETOKEN)
                                  >> (Statement | Expression).iterated()
                                  << token(TokenType.RIGHTBRACETOKEN)
                          )).penetrate(FunctionDefinitionNode)

    LiteralKeyword = token(TokenType.TRUE) | token(TokenType.FALSE) | token(TokenType.NULL)

    Primary = (token(TokenType.IDENTIFIER) | token(TokenType.NUMBER) | token(TokenType.STRING) | LiteralKeyword | (
                token(TokenType.LEFTPARENTOKEN) >> Expression << token(TokenType.RIGHTPARENTOKEN)))  # .penetrate(PrimaryNode)

    # no nested unaries like !!a only !(!a) works
    UnaryOp = token(TokenType.BANG) | token(TokenType.MINUS) | token(TokenType.PLUS)
    Unary = (UnaryOp + Primary).penetrate(lambda tkns: UnaryOperation(*tkns)) | Primary

    FactorOp = token(TokenType.STAR) | token(TokenType.SLASH)
    Factor = binaryTree(FactorOp, Unary)

    TermOp = token(TokenType.PLUS) | token(TokenType.MINUS)
    Term = binaryTree(TermOp, Factor)

    ShiftOp = token(TokenType.LEFTSHIFT) | token(TokenType.RIGHTSHIFT)
    Shift = binaryTree(ShiftOp, Term)

    ComparisonOp = token(TokenType.LESS) | token(TokenType.LESSEQUALS) | token(TokenType.GREATER) | token(
        TokenType.GREATEREQUALS)
    Comparison = binaryTree(ComparisonOp, Shift)

    EqualityOp = token(TokenType.DEQUALS) | token(TokenType.NOTEQUALS)
    Equality = binaryTree(EqualityOp, Comparison)

    Expression.parse = Equality.parse

    Statement.parse = (FunctionDefinition | Assignment).parse

    File = Statement | Expression

    ...


def interpret(src):
    match Scanner.TokenParser(src):
        case None:
            print("Invalid tokens.")
        case [rest, parsed1]:
            print("Tokens:")
            print(*parsed1, sep='\n')
            match AbstractSyntaxTreeParser.FunctionDefinition(parsed1):
                case None:
                    print("Invalid syntax.")
                case [rest, parsed2]:
                    print("Rest:", rest, "Nodes:", parsed2, sep='\n')


def repl():
    print("Welcome to the ___ REPL. Enter valid syntax to see its lexed representation.\nEnter ~ to quit.\n")
    while True:
        line = input('> ')
        if line == "~": break
        interpret(line)


def main():
    match sys.argv:
        case [_]:
            repl()
        case [_, path_or_literal]:
            try:
                with open(path_or_literal) as src:
                    script = src.read()
                interpret(script)
            except:
                interpret(path_or_literal)
        case [*_]:
            print("Usage: interpreter.py [script or source]")


if __name__ == "__main__":
    main()