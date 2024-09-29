from collections.abc import Callable
from typing import Any

try:
    from typing import override
except ImportError:

    def override(method: Callable[..., Any], /) -> Callable[..., Any]:
        try:
            method.__override__ = True

        except (AttributeError, TypeError):
            pass

        return method


__all__ = [
    "override",
]
