import json
from enum import (
    Enum,
    auto,
)


class UserRole(Enum):
    guest = auto()
    normal = auto()
    admin = auto()


class DmEncoder(json.JSONEncoder):
    prefix = "__enum__"

    def default(self, o):
        if isinstance(o, UserRole):
            return {self.prefix: o.name}
        else:
            return super().default(self, o)


def dm_decode(d):
    if DmEncoder.prefix in d:
        name = d[DmEncoder.prefix]
        return UserRole[name]
    else:
        return d
