import sys

import Lexer
import Parser
from Consumers import GenericConsumers, StringConsumers
from Consumers.Consumer import ConsumeSuccess, ConsumeError


class Interpreter:
    def __init__(self, tokenizer, parser, linker, evaluator):
        self.tokenizer = tokenizer
        self.parser = parser
        self.linker = linker
        self.evaluator = evaluator
    def interpret(self, source: str):
        match self.tokenizer(source, 0):
            case ConsumeSuccess([], parsed, _):
                ast = self.parser(parsed, 0)
                cst = self.linker(ast)
                result = self.evaluator(cst)
                return result
            case ConsumeError(rest, desc, pos):
                return ConsumeError(rest, desc, pos)



def repl(interpreter):
    print("Welcome to the bang! repl. enter ~ to exit.")
    while (line := input('> ')) != '~':
        print(interpreter.interpret(list(line)))


def noop(a):
    return a

def main():
    interpreter = Interpreter(Lexer.TokenLexer, Parser.FileParser, noop, noop)
    match sys.argv:
        case [_]:
            repl(interpreter)
        case [_, source_or_file]:
            try:
                with open(source_or_file) as file:
                    source = file.read()
            except FileNotFoundError as _:
                source = source_or_file
            print(interpreter.interpret(list(source)))
        case [*_]: print("Use with a source file, direct source string or on its own.")


if __name__ == "__main__":
    main()
