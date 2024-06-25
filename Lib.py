from enum import Enum
from typing import Iterable, Callable

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