# Bang!
#### A small 'language' built in python

You can try out the interpreter by running `Interpreter.py`. Providing a `.bang` file currently lexes, parses and links it.
Running without any arguments starts the REPL.

`sample.bang` is a small sample containing a couple of different statements and expressions.

`Consumers` contains the lexing / parsing class, since both have the same foundation.
It's essentially a parser combinator type library.

`DataTypes` holds the representations that are used throughout the interpretation / compilation.

