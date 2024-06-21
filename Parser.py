from __future__ import annotations
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