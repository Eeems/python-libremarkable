from __future__ import annotations

from typing import Self
from typing import Iterable
from typing import overload

from collections.abc import MutableSet

from itertools import product
from itertools import pairwise

from dataclasses import dataclass


@dataclass(eq=True, frozen=False, unsafe_hash=True)
class Point:
    x: float
    y: float

    def __iter__(self) -> Iterable[float]:
        yield self.x
        yield self.y

    def __lt__(self, point: Point) -> bool:
        return tuple(self) < tuple(point)

    def toInt(self) -> Point:
        return Point(int(self.x), int(self.y))


@dataclass(eq=True, frozen=False, unsafe_hash=True)
class Rect:
    left: float
    top: float
    right: float
    bottom: float

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top

    @property
    def topLeft(self) -> Point:
        return Point(self.left, self.top)

    @property
    def topRight(self) -> Point:
        return Point(self.right, self.top)

    @property
    def bottomLeft(self) -> Point:
        return Point(self.left, self.bottom)

    @property
    def bottomRight(self) -> Point:
        return Point(self.right, self.bottom)

    @property
    def center(self) -> Point:
        return Point(self.left + (self.width / 2), self.top + (self.height / 2))

    @property
    def area(self) -> float:
        return self.width * self.height

    def __iter__(self) -> Iterable[float]:
        yield self.left
        yield self.top
        yield self.right
        yield self.bottom

    def __bool__(self) -> bool:
        return self.area > 0

    def __lt__(self, point: Point) -> bool:
        return tuple(self) < tuple(point)

    @overload
    def __contains__(self, point: Point) -> bool:
        pass

    @overload
    def __contains__(self, rect: Rect) -> bool:
        pass

    def __contains__(self, item) -> bool:
        if isinstance(item, Point):
            return (
                self.left <= item.x <= self.right and self.top <= item.y <= self.bottom
            )

        if isinstance(item, Rect):
            return item.topLeft in self and item.bottomRight in self

        raise NotImplementedError()

    def __sub__(self, rect: Rect) -> Iterable[Rect]:
        return self.difference(rect)

    def __and__(self, rect: Rect) -> Rect | None:
        return self.intersect(rect)

    def __xor__(self, rect: Rect) -> Region:
        return Region(self, rect) - self.intersect(rect)

    def intersect(self, rect: Rect) -> Rect | None:
        x1 = max(min(self.left, self.right), min(rect.left, rect.right))
        y1 = max(min(self.top, self.bottom), min(rect.top, rect.bottom))
        x2 = min(max(self.left, self.right), max(rect.left, rect.right))
        y2 = min(max(self.top, self.bottom), max(rect.top, rect.bottom))
        return Rect(x1, y1, x2, y2) if x1 < x2 and y1 < y2 else None

    def difference(self, rect: Rect) -> Iterable[Rect]:
        if not self.intersects(rect):
            yield self
            return

        intersection = self.intersect(rect)
        xs = {self.left, self.right}
        ys = {self.top, self.bottom}

        if self.left < rect.left < self.right:
            xs.add(rect.left)

        if self.left < rect.right < self.right:
            xs.add(rect.right)

        if self.top < rect.top < self.bottom:
            ys.add(rect.top)

        if self.top < rect.bottom < self.bottom:
            ys.add(rect.bottom)

        for (left, right), (top, bottom) in product(
            pairwise(sorted(xs)), pairwise(sorted(ys))
        ):
            rect = Rect(left, top, right, bottom)
            if rect != intersection:
                yield rect

    def intersects(self, rect: Rect) -> bool:
        return (
            rect.topLeft in self
            or rect.bottomRight in self
            or self.topLeft in rect
            or self.bottomRight in rect
        )

    def toInt(self) -> Rect:
        return Rect(int(self.left), int(self.top), int(self.right), int(self.bottom))


class Region(MutableSet[Rect]):
    def __init__(self, *rects: list[Rect]) -> Self:
        self.elements = set(rects)

    def __repr__(self) -> str:
        return f"Region(rects={len(self)})"

    @overload
    def __contains__(self, point: Point) -> bool:
        pass

    @overload
    def __contains__(self, rect: Rect) -> bool:
        pass

    @overload
    def __contains__(self, region: Region) -> bool:
        pass

    def __contains__(self, item) -> bool:
        if isinstance(item, Point) or isinstance(item, Rect):
            for rect in self:
                if item in rect:
                    return True

            return False

        if isinstance(item, Region):
            for rect in item:
                if rect not in self:
                    return False

            return True

        raise NotImplementedError()

    def __iter__(self) -> Iterable[Rect]:
        return iter(self.elements)

    def __len__(self) -> int:
        return len(self.elements)

    @overload
    def __iadd__(self, rect: Rect) -> Self:
        pass

    @overload
    def __iadd__(self, region: Region) -> Self:
        pass

    def __iadd__(self, item) -> Self:
        if isinstance(item, Rect):
            self.add(item)
            return self

        if isinstance(item, Region) or isinstance(item, Iterable):
            for r in item:
                self += r

            return self

        raise NotImplementedError()

    @overload
    def __add__(self, rect: Rect) -> Region:
        pass

    @overload
    def __add__(self, rects: Iterable[Rect]) -> Region:
        pass

    @overload
    def __add__(self, region: Region) -> Region:
        pass

    def __add__(self, item) -> Region:
        region = Region(*self.elements)
        if isinstance(item, Rect):
            region.add(item)
            return region

        if isinstance(item, Region) or isinstance(item, Iterable):
            for r in item:
                region += r

            return region

        raise NotImplementedError()

    @overload
    def __isub__(self, rect: Rect) -> Self:
        pass

    @overload
    def __isub__(self, region: Region) -> Self:
        pass

    def __isub__(self, item) -> Self:
        if isinstance(item, Rect):
            self.discard(item)
            return self

        if isinstance(item, Region):
            for rect in item:
                self.discard(rect)

            return self

        raise NotImplementedError()

    @overload
    def __sub__(self, rect: Rect) -> Region:
        pass

    @overload
    def __sub__(self, region: Region) -> Region:
        pass

    def __sub__(self, item) -> Region:
        region = Region(*self.elements)
        if isinstance(item, Rect):
            region.discard(item)
            return region

        if isinstance(item, Region):
            for rect in item:
                region.discard(rect)

            return region

        raise NotImplementedError()

    def add(self, rect: Rect) -> None:
        if rect in self:
            return

        intersected = [x for x in self if x.intersects(rect)]
        if not intersected:
            self.elements.add(rect)
            return

        rects = [rect]
        for r in intersected:
            for rect in rects:
                if not r.intersects(rect):
                    continue

                while rect in rects:
                    rects.remove(rect)

                for diffRect in rect.difference(r):
                    rects.append(diffRect)

        for rect in rects:
            self.elements.add(rect)

        # TODO - merge rectangles that can be merged

    def discard(self, rect: Rect) -> None:
        for r in list(self):
            self.elements.discard(r)
            self += list(r - rect)

    @property
    def toInt(self) -> Region:
        return Region([x.toInt() for x in self])

    @property
    def boundingRect(self) -> Rect:
        return Rect(
            min([x.left for x in self]),
            min([x.top for x in self]),
            max([x.right for x in self]),
            max([x.bottom for x in self]),
        )


__all__ = [
    "Point",
    "Rect",
    "Region",
]
