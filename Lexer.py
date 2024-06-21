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

    # Literals
    STRING            = 28 #  '"' + content + '"'
    NUMBER            = 29 #  some number of numeric chars in a row, for now just ints. but simple to fix - just copy the float parser from jsonparser
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
