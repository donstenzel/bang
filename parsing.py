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

def repl():
    print("Welcome to the ___ repl. enter ~ to exit.")
    while (line := input('')) != '~':
        print(tokenize(line))


def tokenize(source): ...


def main():
    match sys.argv:
        case [_]:
            repl()
        case [_, source_or_file]:
            try:
                with open(source_or_file) as file:
                    source = file.read()
            except FileNotFoundError as _:
                source = source_or_file
            print(tokenize(source))
        case [*_]: print("Use with a source file, direct source string or on its own.")


if __name__ == "__main__":
    main()
