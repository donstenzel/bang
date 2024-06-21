import sys

import Lexer
from Consumers import GenericConsumers, StringConsumers


class Interpreter:
    def __init__(self, tokenizer, parser, linker, evaluator):
        self.tokenizer = tokenizer
        self.parser = parser
        self.linker = linker
        self.evaluator = evaluator
    def interpret(self, source: str):
        tokens = self.tokenizer(source, 0)
        ast = self.parser(tokens)
        cst = self.linker(ast)
        result = self.evaluator(cst)
        return result

def repl(interpreter):
    print("Welcome to the bang! repl. enter ~ to exit.")
    while (line := input('> ')) != '~':
        print(interpreter.interpret(list(line)))


def noop(a):
    return a

def main():
    interpreter = Interpreter(Lexer.TokenLexer, noop, noop, noop)
    match sys.argv:
        case [_]:
            repl(interpreter)
        case [_, source_or_file]:
            try:
                with open(source_or_file) as file:
                    source = file.read()
            except FileNotFoundError as _:
                source = source_or_file
            print(interpreter.interpret(source))
        case [*_]: print("Use with a source file, direct source string or on its own.")


if __name__ == "__main__":
    main()
