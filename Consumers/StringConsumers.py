from .GenericConsumers import predicate
from .Consumer import Consume
from Lib import reduce


def char(to_match: str) -> Consume[str]:
    return predicate(lambda c: c == to_match, f"¢ '{to_match}'")

def not_char(to_match: str) -> Consume[str]:
    return predicate(lambda c: c != to_match, f"¢ not '{to_match}'")

def chars(to_match: str) -> Consume[str]:
    return predicate(lambda c: c in to_match, f"¢ in '{to_match}'")

def not_chars(to_match: str) -> Consume[str]:
    return predicate(lambda c: c not in to_match, f"¢ not in '{to_match}'")

def string(to_match: str) -> Consume[str]:
    return reduce([char(c) for c in list(to_match)], Consume.__add__)