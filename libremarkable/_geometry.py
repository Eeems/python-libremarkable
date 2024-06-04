from typing import Self
from typing import Iterable

from collections.abc import MutableSet

from dataclasses import dataclass


@dataclass(eq=True, frozen=False, unsafe_hash=True)
class Point:
    x: float
    y: float

    def toInt(self) -> Self:
        return Point(int(self.x), int(self.y))


@dataclass(eq=True, frozen=False, unsafe_hash=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    def toInt(self) -> Self:
        return Rect(int(self.x), int(self.y), int(self.width), int(self.height))

    @property
    def topLeft(self) -> Point:
        return Point(self.x, self.y)

    @property
    def topRight(self) -> Point:
        return Point(self.x + self.width, self.y)

    @property
    def bottomLeft(self) -> Point:
        return Point(self.x, self.y + self.height)

    @property
    def bottomRight(self) -> Point:
        return Point(self.x + self.width, self.y + self.height)

    @property
    def center(self) -> Point:
        return Point(self.x + (self.width / 2), self.y + (self.height / 2))


class Region(MutableSet[Rect]):
    def __init__(self, *rects: list[Rect]) -> Self:
        self.elements = set(rects)

    def __contains__(self, rect: Rect) -> bool:
        return rect in self.elements

    def __iter__(self) -> Iterable[Rect]:
        return iter(self.elements)

    def __len__(self) -> int:
        return len(self.elements)

    def add(self, rect: Rect):
        # TODO - Merge overlapping rects
        #        ref: https://stackoverflow.com/a/36101971
        self.elements.add(rect)

    def discard(self, rect: Rect):
        # TODO - Subtract from overlapping rects
        self.elements.discard(rect)

    @property
    def toInt(self) -> Self:
        return Region([x.toInt() for x in self])
