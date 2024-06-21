from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Callable, Any
from Lib import cons

type ConsumeResult[T] = ConsumeSuccess[T] | ConsumeError[T]
type ConsumeFunction[T] = Callable[[Iterable[T], int], ConsumeResult[T]]

@dataclass
class ConsumeSuccess[T]:
    __match_args__ = ('rest', 'parsed', 'progress')
    rest: Iterable[T]
    parsed: T
    progress: int

@dataclass
class ConsumeError[T]:
    __match_args__ = ('rest', 'description', 'progress')
    rest: Iterable[T]
    description: str
    progress: int

class Consume[T]:
    def __init__(self, func: ConsumeFunction[T]):
        self.func = func

    def __add__(self, other: Consume[T]) -> Consume[T]:
        def consume(collection: Iterable[T], pos: int) -> ConsumeResult[T]:
            match self(collection, pos):
                case ConsumeSuccess(rest1, parsed1, pos1):
                    match other(rest1, pos1):
                        case ConsumeSuccess(rest2, parsed2, pos2):
                            return ConsumeSuccess(rest2, cons(parsed1, parsed2), pos2)
                        case ConsumeError(rest2, desc2, pos2):
                            return ConsumeError(rest2, desc2, pos2)
                case ConsumeError(rest1, desc1, pos1):
                    return ConsumeError(rest1, desc1, pos1)
        return Consume(consume)

    def __or__(self, other: Consume[T]) -> Consume[T]:
        def consume(collection: Iterable[T], pos: int) -> ConsumeResult[T]:
            match self(collection, pos):
                case ConsumeSuccess(rest1, parsed1, pos1):
                    return ConsumeSuccess(rest1, parsed1, pos1)
                case ConsumeError(rest1, error1, pos1):
                    match other(collection, pos):
                        case ConsumeSuccess(rest2, parsed2, pos2):
                            return ConsumeSuccess(rest2, parsed2, pos2)
                        case ConsumeError(rest2, error2, pos2):
                            if pos2 > pos1:
                                return ConsumeError(rest2, error2, pos2)
                            elif pos1 > pos2:
                                return ConsumeError(rest1, error1, pos1)
                            else:
                                return ConsumeError(rest1, f"{error1} | {error2}", pos1)
        return Consume(consume)

    def __rshift__(self, other: Consume[T]) -> Consume[T]:
        def consume(collection: Iterable[T], pos: int) -> ConsumeResult[T]:
            match self(collection, pos):
                case ConsumeSuccess(rest1, _, pos1):
                    match other(rest1, pos1):
                        case ConsumeSuccess(rest2, parsed, pos2):
                            return ConsumeSuccess(rest2, parsed, pos2)
                        case ConsumeError(rest2, desc2, pos2):
                            return ConsumeError(rest2, desc2, pos2)
                case ConsumeError(rest1, desc1, pos1):
                    return ConsumeError(rest1, desc1, pos1)

        return Consume(consume)

    def __lshift__(self, other: Consume[T]) -> Consume[T]:
        def consume(collection: Iterable[T], pos: int) -> ConsumeResult[T]:
            match self(collection, pos):
                case ConsumeSuccess(rest1, parsed, pos1):
                    match other(rest1, pos1):
                        case ConsumeSuccess(rest2, _, pos2):
                            return ConsumeSuccess(rest2, parsed, pos2)
                        case ConsumeError(rest2, desc2, pos2):
                            return ConsumeError(rest2, desc2, pos2)
                case ConsumeError(rest1, desc1, pos1):
                    return ConsumeError(rest1, desc1, pos1)
        return Consume(consume)


    def continuous(self) -> Consume[T]:
        def consume(collection: Iterable[T], progress: int) -> ConsumeResult[T]:
            match self(collection, progress):
                case ConsumeError(rest, desc, pos): return ConsumeError(rest, desc, pos)
                case ConsumeSuccess(rest1, parsed1, pos1):
                    curr = ConsumeSuccess(rest1, parsed1, pos1)
                    while True:
                        match self(curr.rest, curr.progress):
                            case ConsumeError(_, _, _): break
                            case ConsumeSuccess(rest2, parsed2, pos2):
                                curr = ConsumeSuccess(rest2, cons(curr.parsed, parsed2), pos2)
                    return curr
        return Consume(consume)


    def delimited(self, other: Consume[T]) -> Consume[T]:
        delimelem = other >> self

        def consume(collection: Iterable[T], pos: int) -> ConsumeResult[T]:
            match self(collection, pos):
                case ConsumeError(rest, desc, pos): return ConsumeError(rest, desc, pos)
                case ConsumeSuccess(rest, parsed, pos):
                    curr = ConsumeSuccess(rest, parsed, pos)
                    while True:
                        match other(rest, pos):
                            case ConsumeError(_, _, _): break
                            case ConsumeSuccess(rest, _, pos):
                                match self(rest, pos):
                                    case ConsumeError(rest, desc, pos): return ConsumeError(rest, desc, pos)
                                    case ConsumeSuccess(rest, parsed, pos):
                                        curr = ConsumeSuccess(rest, cons(curr.parsed, parsed), pos)
                    return curr
        return Consume(consume)

    def penetrate(self, func: Callable[[T], Any]) -> Consume[T]:
        def consume(collection: Iterable[T], pos: int) -> ConsumeResult[T]:
            match self(collection, pos):
                case ConsumeSuccess(rest, parsed, pos): return ConsumeSuccess(rest, func(parsed), pos)
                case err: return err
        return Consume(consume)

    def description(self, func: Callable[[str], str]) -> Consume[T]:
        def consume(collection: Iterable[T], pos: int) -> ConsumeResult[T]:
            match self(collection, pos):
                case ConsumeError(rest, desc, pos): return ConsumeError(rest, func(desc), pos)
                case succ: return succ
        return Consume(consume)

    def __call__(self, collection: Iterable[T], pos: int) -> ConsumeResult[T]:
        return self.func(collection, pos)