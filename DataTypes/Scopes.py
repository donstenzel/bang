from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Scope:
    parent: Scope | None
    members: dict

    def __contains__(self, item):
        match item in self.members.keys():
            case True: return True
            case False: return False if self.parent is None else self.parent.__contains__(item)

    def __getitem__(self, key):
        match key in self.members.keys():
            case True: return self.members[key]
            case False:
                if self.parent is None:
                    raise Exception(f"{key} does not exist in this scope.")
                return self.parent[key]

    def __setitem__(self, key, value):
        self.members[key] = value