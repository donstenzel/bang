from Consumer import Consume, ConsumeError, ConsumeSuccess

def predicate(func, name):
    def parse(collection, pos):
        match collection:
            case head, *tail: return ConsumeSuccess(tail, head, pos +1) if func(head) else ConsumeError(collection, f"{name} @ {pos} $> {head} did not match predicate.", pos)
            case []: return ConsumeError(collection, f"{name} @ {pos} $> Input is empty.", pos)
            case _: return ConsumeError(collection, f"{name} @ {pos} $> Input has wrong format.", pos)
    return Consume(parse)

