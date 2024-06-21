from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable
from Lib import collapse, reduce

from Consumers.Consumer import Consume
from Consumers import GenericConsumers, StringConsumers



WhitespaceLexer = StringConsumers.chars(" \t\n").continuous()
# $ ~ # · †
class TokenType(Enum):
    # Grouping
    LEFTPARENTOKEN    =  0 #  (
    RIGHTPARENTOKEN   =  1 #  )
    LEFTBRAKETTOKEN   =  2 #  [
    RIGHTBRACKETTOKEN =  3 #  ]
    LEFTBRACETOKEN    =  4 #  {
    RIGHTBRACETOKEN   =  5 #  }

    # Single Character Operators
    PLUS              =  6 #  +
    MINUS             =  7 #  -
    STAR              =  8 #  *
    SLASH             =  9 #  /
    PERCENT           = 10 #  %
    AND               = 11 #  &
    OR                = 12 #  |
    LESS              = 13 #  <
    GREATER           = 14 #  >
    EQUALS            = 15 #  =
    BANG              = 16 #  !
    DOT               = 17 #  .
    QUESTIONMARK      = 18 #  ?
    COMMA             = 19 #  ,
    COLON             = 20 #  :

    # Double Character Operators
    DEQUALS           = 21 #  ==
    LESSEQUALS        = 22 #  <=
    GREATEREQUALS     = 23 #  >=
    NOTEQUALS         = 24 #  !=
    LEFTSHIFT         = 25 #  <<
    RIGHTSHIFT        = 26 #  >>
    PIPE              = 27 #  |>

    # Literals
    STRING            = 28 #  (' | ") + content + (' | ") <- quotes have to match.
    NUMBER            = 29 #  some number of numeric chars in a row, for now just ints. but simple to fix - just copy the float parser from jsonLexer
    COMMENT           = 30 #  //... until end of line
    IDENTIFIER        = 31 #  alphabetic chars + _ that dont match anything else

    # Keywords
    IF                = 32 #  if
    ELSE              = 33 #  else
    MATCH             = 34 #  match
    TRUE              = 35 #  true
    FALSE             = 36 #  false
    FOR               = 37 #  for
    IN                = 38 #  in
    WHILE             = 39 #  while
    RETURN            = 40 #  return
    VAR               = 41 #  var
    VAL               = 42 #  val
    THIS              = 43 #  this
    CLASS             = 44 #  class
    FUN               = 45 #  fun
    NULL              = 46 #  null
    BASE              = 47 #  base

@dataclass
class Token:
    token: TokenType
    lexeme: str
    literal: Any


TokenLexers = []
def SimpleTokenLexer(string, tokentype):
    c = GenericConsumers.sequence(string, f"{string} Token").penetrate(lambda cs: Token(tokentype, ''.join(cs), None))
    TokenLexers.append(c)
    return c

LeftParenLexer         = SimpleTokenLexer('(',      TokenType.LEFTPARENTOKEN )
RightParenLexer        = SimpleTokenLexer(')',      TokenType.RIGHTPARENTOKEN)
LeftBracketLexer       = SimpleTokenLexer('[',      TokenType.LEFTBRAKETTOKEN)
RightBracketLexer      = SimpleTokenLexer(']',      TokenType.RIGHTBRACKETTOKEN)
LeftBraceLexer         = SimpleTokenLexer('{',      TokenType.LEFTBRACETOKEN)
RightBraceLexer        = SimpleTokenLexer('}',      TokenType.RIGHTBRACETOKEN)

PlusLexer              = SimpleTokenLexer('+',      TokenType.PLUS)
MinusLexer             = SimpleTokenLexer('-',      TokenType.MINUS)
StarLexer              = SimpleTokenLexer('*',      TokenType.STAR)
SlashLexer             = SimpleTokenLexer('/',      TokenType.SLASH)
PercentLexer           = SimpleTokenLexer('%',      TokenType.PERCENT)
AndLexer               = SimpleTokenLexer('&',      TokenType.AND)
OrLexer                = SimpleTokenLexer('|',      TokenType.OR)
LessThanLexer          = SimpleTokenLexer('<',      TokenType.LESS)
GreaterThanLexer       = SimpleTokenLexer('>',      TokenType.GREATER)
EqualsLexer            = SimpleTokenLexer('=',      TokenType.EQUALS)
BangLexer              = SimpleTokenLexer('!',      TokenType.BANG)
DotLexer               = SimpleTokenLexer('.',      TokenType.DOT)
QuestionmarkLexer      = SimpleTokenLexer('?',      TokenType.QUESTIONMARK)
CommaLexer             = SimpleTokenLexer(',',      TokenType.COMMA)
ColonLexer             = SimpleTokenLexer(':',      TokenType.COLON)

DoubleEqualsLexer      = SimpleTokenLexer('==',     TokenType.DEQUALS)
LessEqualsLexer        = SimpleTokenLexer('<=',     TokenType.LESSEQUALS)
GreaterEqualsLexer     = SimpleTokenLexer('>=',     TokenType.GREATEREQUALS)
NotEqualsLexer         = SimpleTokenLexer('!=',     TokenType.NOTEQUALS)
LeftShiftLexer         = SimpleTokenLexer('<<',     TokenType.LEFTSHIFT)
RightShiftLexer        = SimpleTokenLexer('>>',     TokenType.RIGHTSHIFT)
PipeLexer              = SimpleTokenLexer('|>',     TokenType.PIPE)


Keywords = {
    "if"     :   TokenType.IF,
    "else"   :   TokenType.ELSE,
    "match"  :   TokenType.MATCH,
    "true"   :   TokenType.TRUE,
    "false"  :   TokenType.FALSE,
    "for"    :   TokenType.FOR,
    "in"     :   TokenType.IN,
    "while"  :   TokenType.WHILE,
    "return" :   TokenType.RETURN,
    "var"    :   TokenType.VAR,
    "val"    :   TokenType.VAL,
    "this"   :   TokenType.THIS,
    "class"  :   TokenType.CLASS,
    "fun"    :   TokenType.FUN,
    "null"   :   TokenType.NULL,
    "base"   :   TokenType.BASE
}

def ident_or_keyword(string):
    string = ''.join(string)
    if string in Keywords.keys():
        return Token(Keywords[string], string, None)
    else: return Token(TokenType.IDENTIFIER, string, string)

IdentifierKeywordLexer = GenericConsumers\
                        .predicate(lambda e: e.isalnum() or e == '_', "Identifier")\
                        .continuous()\
                        .penetrate(ident_or_keyword)

# Possible new thing, interesting if we want more string like syntax pieces
SingleQuoteLexer = StringConsumers.char("'")
SingleQuoteStringLexer = StringConsumers.not_chars("'") \
    .continuous() \
    .optional() \
    .bracketed(SingleQuoteLexer, SingleQuoteLexer) \
    .penetrate(collapse) \
    .penetrate(lambda string: Token(TokenType.STRING, "'" + string + "'", string))

DoubleQuoteLexer = StringConsumers.char('"')
DoubleQuoteStringLexer = StringConsumers.not_chars('"') \
    .continuous() \
    .optional() \
    .bracketed(DoubleQuoteLexer, DoubleQuoteLexer) \
    .penetrate(collapse) \
    .penetrate(lambda string: Token(TokenType.STRING, '"' + string + '"', string))

UnderscoreLexer = StringConsumers.char('_')
DigitLexer: Consume[str] = GenericConsumers.predicate(str.isdigit, "Digit")
NumberLexer = DigitLexer.delimited(UnderscoreLexer).penetrate(collapse).penetrate(
    lambda num: Token(TokenType.NUMBER, num, int(num))
)

CommentLexer = (
        StringConsumers.string('//')
        >> StringConsumers.not_chars('\n').continuous()
        << StringConsumers.char('\n')
).penetrate(collapse) \
 .penetrate(lambda comment: Token(TokenType.COMMENT, '//' + comment + '\n', comment))

# BlockCommentLexer = (
#         StringConsumers.string('/*')
#         >> (StringConsumers.not_chars('*') | StringConsumers.char('*').lookahead(StringConsumers.char('/'))).iterated()
#         << StringConsumers.string('*/')
# ).penetrate(collapse) \
#     .penetrate(lambda string: Token(TokenType.COMMENT, '/*' + string + '*/', string))

TokenLexers.extend([NumberLexer, IdentifierKeywordLexer, DoubleQuoteStringLexer, SingleQuoteStringLexer, CommentLexer])

TokenLexer = reduce(TokenLexers[::-1], Consume.__or__).delimited_optional(WhitespaceLexer)
"""Converts a string into a list of tokens if possible."""
