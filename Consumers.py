from typing import Iterable, Callable

from Consumer import Consume, ConsumeError, ConsumeSuccess
from Lib import reduce


def predicate[T](func: Callable[[T], bool], name: str) -> Consume[T]:
    def parse(collection, pos):
        match collection:
            case head, *tail: return ConsumeSuccess(tail, head, pos +1) if func(head) else ConsumeError(collection, f"{name} @ {pos} $> {head} did not match predicate.", pos)
            case []: return ConsumeError(collection, f"{name} @ {pos} $> Input is empty.", pos)
            case _: return ConsumeError(collection, f"{name} @ {pos} $> Input has wrong format.", pos)
    return Consume(parse)

def item[T](to_match: T, name: str) -> Consume[T]:
    return predicate(lambda matcher: matcher == to_match, name)

def sequence[T](seq: Iterable[T], name: str) -> Consume[T]:
    ps = []
    for elem in seq:
        ps.append(item(elem, name))
    return reduce(ps, Consume.__add__)