from enum import Enum
from typing import Iterable, Callable

Colors = [
    "\033[38;5;196m",
    "\033[38;5;202m",
    "\033[38;5;208m",
    "\033[38;5;214m",
    "\033[38;5;220m",
    "\033[38;5;226m",
    "\033[38;5;190m",
    "\033[38;5;154m",
    "\033[38;5;118m",
    "\033[38;5;082m",
    "\033[38;5;046m",
    "\033[38;5;047m",
    "\033[38;5;048m",
    "\033[38;5;049m",
    "\033[38;5;050m",
    "\033[38;5;051m",
    "\033[38;5;045m",
    "\033[38;5;039m",
    "\033[38;5;033m",
    "\033[38;5;027m",
    "\033[38;5;021m",
    "\033[38;5;057m",
    "\033[38;5;093m",
    "\033[38;5;129m",
    "\033[38;5;165m",
    "\033[38;5;201m",
    "\033[38;5;200m",
    "\033[38;5;199m",
    "\033[38;5;198m",
    "\033[38;5;197m",
]

ColorOff = "\033[0m"

NAME = ('\n' +
       Colors[0] + " ▄▄▄▄    ▄▄▄       ███▄    █   ▄████  ▐██▌ " + '\n' +
       Colors[1] + "▓█████▄ ▒████▄     ██ ▀█   █  ██▒ ▀█▒ ▐██▌ " + '\n' +
       Colors[2] + "▒██▒ ▄██▒██  ▀█▄  ▓██  ▀█ ██▒▒██░▄▄▄░ ▐██▌ " + '\n' +
       Colors[3] + "▒██░█▀  ░██▄▄▄▄██ ▓██▒  ▐▌██▒░▓█  ██▓ ▓██▒ " + '\n' +
       Colors[4] + "░▓█  ▀█▓ ▓█   ▓██▒▒██░   ▓██░░▒▓███▀▒ ▒▄▄  " + '\n' +
       Colors[4] + "░▒▓███▀▒ ▒▒   ▓▒█░░ ▒░   ▒ ▒  ░▒   ▒  ░▀▀▒ " + '\n' +
       Colors[3] + "▒░▒   ░   ▒   ▒▒ ░░ ░░   ░ ▒░  ░   ░  ░  ░ " + '\n' +
       Colors[2] + " ░    ░   ░   ▒      ░   ░ ░ ░ ░   ░     ░ " + '\n' +
       Colors[1] + " ░            ░  ░         ░       ░  ░    " + '\n' +
       Colors[0] + "      ░                                    " + ColorOff
       + '\n')


#NAME = f"{Colors[0]}b{Colors[-2]}a{Colors[-4]}n{Colors[-6]}g{Colors[-8]}!{ColorOff}"

def cons(a, b):
    """what + should be when lists are involved..."""
    match a, b:
        case [  ], [  ] : return [      ]  # Empty Empty
        case [*l], [  ] : return [*l    ]  # List  Empty
        case [  ], [*r] : return [    *r]  # Empty List
        case [ l], [  ] : return [ l    ]  # Item  Empty
        case [  ], [ r] : return [     r]  # Empty Item
        case [*l], [*r] : return [*l, *r]  # List  List
        case [*l],   r  : return [*l,  r]  # List  Item
        case   l,  [*r] : return [ l, *r]  # Item  List
        case   l,    r  : return [ l,  r]  # Item  Item

def reduce_with_base[T](items: Iterable[T], agg: Callable[[T, T], T], start: T) -> T:
    out = start
    for item in items:
        out = agg(out, item)
    return out

def reduce[T](items: Iterable[T], aggr: Callable[[T, T], T]):
    out, *rest = items
    for item in rest:
        out = aggr(out, item)
    return out

def collapse(chars: Iterable[str]) -> str:
    return ''.join(chars)

class Ordering(Enum):
    LESS = 0
    EQUAL = 1
    GREATER = 2

def compare(a, b):
    if a < b:
        return Ordering.LESS
    if a > b:
        return Ordering.GREATER
    else:
        return Ordering.EQUAL



def planet(l, string):
    """call this with list and a string consisting of '·' and 'o' representing which items to keep."""
    if len(string) > len(l): raise Exception(f"'{string}' is longer than list.")
    return [l[i] for i, c in enumerate(string) if c == 'o'] + l[len(string)]