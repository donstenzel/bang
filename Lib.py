def cons(a, b):
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