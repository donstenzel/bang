import sys
import Consumers
def repl(interpreter):
    print("Welcome to the ___ repl. enter ~ to exit.")
    while (line := input('> ')) != '~':
        print(interpreter(list(line), 0))



def main():
    AP = Consumers.predicate(lambda c: c == "A", "A")#.continuous()
    BP = Consumers.predicate(lambda c: c == "B", "B")
    Interpreter = AP.delimited(BP)
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
