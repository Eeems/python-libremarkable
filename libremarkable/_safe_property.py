def _immutable(self, *args, **kws):
    raise TypeError("cannot change object - object is immutable")


class FrozenList(list):
    """Immutable list"""

    pop = _immutable
    remove = _immutable
    append = _immutable
    clear = _immutable
    extend = _immutable
    insert = _immutable
    reverse = _immutable


class FrozenDict(dict):
    """Immutable dictionary"""

    __setitem__ = _immutable
    __delitem__ = _immutable
    pop = _immutable
    popitem = _immutable
    clear = _immutable
    update = _immutable
    setdefault = _immutable


class safe_property(property):
    """Make a list/dict/set property immutable

    https://stackoverflow.com/a/54639748"""

    def __get__(self, obj, objtype=None):
        candidate = super().__get__(obj, objtype)
        if isinstance(candidate, dict):
            return FrozenDict(candidate)

        if isinstance(candidate, list):
            return FrozenList(candidate)

        if isinstance(candidate, set):
            return frozenset(candidate)

        return candidate


__all__ = ["safe_property"]
