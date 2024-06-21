import sys
from Consumers import GenericConsumers, StringConsumers
#import Lexer

def repl(interpreter):
    print("Welcome to the bang! repl. enter ~ to exit.")
    while (line := input('> ')) != '~':
        print(interpreter(list(line), 0))



def main():
    Interpreter = StringConsumers.string("Hello").optional()
    match sys.argv:
        case [_]:
            repl(Interpreter)
        case [_, source_or_file]:
            try:
                with open(source_or_file) as file:
                    source = file.read()
            except FileNotFoundError as _:
                source = source_or_file
            print(Interpreter(source, 0))
        case [*_]: print("Use with a source file, direct source string or on its own.")


if __name__ == "__main__":
    main()
