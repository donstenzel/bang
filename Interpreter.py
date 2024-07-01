import sys

import Evaluator
import Lexer
import Lib
import Parser
import Linker
from Consumers.Consumer import ConsumeSuccess, ConsumeError


class Interpreter:
    def __init__(self, tokenizer, parser, linker, evaluator):
        self.tokenizer = tokenizer
        self.parser = parser
        self.linker = linker
        self.evaluator = evaluator
        self.linker_scope = Linker.Scope(None, {})
        self.eval_scope = Linker.Scope(None, {})
    def interpret(self, source: str):
        match self.tokenizer(source, 0):
            case ConsumeSuccess([], tokenized, _):
                match self.parser(tokenized, 0):
                    case ConsumeSuccess([], parsed, _):
                        linked = self.linker(self.linker_scope, parsed)
                        result = self.evaluator(self.eval_scope, linked)
                        return result

                    case ConsumeError(rest, desc, pos):
                        return ConsumeError(rest, desc, pos)

            case ConsumeError(rest, desc, pos):
                return ConsumeError(rest, desc, pos)


def repl(interpreter):
    line_start = Lib.Colors[7] + '> '# + Lib.ColorOff
    print(f"{Lib.NAME}{Lib.Colors[17]}Welcome to the interactive environment. enter ~ to exit.{Lib.ColorOff}")
    while (line := input(line_start)) != '~':
        try:
            res = interpreter.interpret(list(line))
            print(res)
            print(interpreter.eval_scope)
        except Exception as e:
            print(e)
    print(Lib.Colors[17] + "👋 keep banging!" + Lib.ColorOff)


def noop(a):
    return a

def main():
    interpreter = Interpreter(Lexer.TokenLexer, Parser.FileParser, Linker.resolve, Evaluator.evaluate)
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
