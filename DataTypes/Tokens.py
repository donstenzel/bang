from dataclasses import dataclass
from enum import Enum
from typing import Any

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
    BIND              = 28 #  ->

    # Literals
    STRING            = 29 #  (' | ") + content + (' | ") <- quotes have to match.
    NUMBER            = 30 #  some number of numeric chars in a row, for now just ints. but simple to fix - just copy the float parser from jsonLexer
    COMMENT           = 31 #  //... until end of line
    IDENTIFIER        = 32 #  alphabetic chars + _ that dont match anything else

    # Keywords
    IF                = 33 #  if
    ELSE              = 34 #  else
    MATCH             = 35 #  match
    TRUE              = 36 #  true
    FALSE             = 37 #  false
    FOR               = 38 #  for
    IN                = 39 #  in
    WHILE             = 40 #  while
    RETURN            = 41 #  return
    VAR               = 42 #  var
    VAL               = 43 #  val
    THIS              = 44 #  this
    CLASS             = 45 #  class
    FUN               = 46 #  fun
    NULL              = 47 #  null
    BASE              = 48 #  base
    LET               = 49 #  let

@dataclass
class Token:
    token: TokenType
    lexeme: str
    literal: Any
