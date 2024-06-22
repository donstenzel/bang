from .GenericConsumers import predicate

def token(to_match):
    return predicate(lambda t: t.token == to_match, f"{to_match}")

def not_token(to_match):
    return predicate(lambda t: t.token != to_match, f"!{to_match}")