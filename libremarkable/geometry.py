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
    """Point on a 2d plane"""

    x: float  #: x coordinate
    y: float  #: y coordinate

    def __iter__(self) -> Iterable[float]:
        """Iterate through the x and then y coordinate

        :returns: x and then y"""
        yield self.x
        yield self.y

    def __lt__(self, point: Point) -> bool:
        """Check to see if one point is less than another point

        :param point: point to compare against
        :return: if the tuple of this point is less than the tuple of the point to compare against
        """
        return tuple(self) < tuple(point)

    def toInt(self) -> Point:
        """Return a clone of this point after converting the x and y coordinates to integers"""
        return Point(int(self.x), int(self.y))


@dataclass(eq=True, frozen=False, unsafe_hash=True)
class Rect:
    """A rectangle on a 2d plane"""

    left: float  #: top left x coordinate
    top: float  #: top left y coordinate
    right: float  #: bottom right x coordinate
    bottom: float  #: bottom right y coordinate

    @property
    def width(self) -> float:
        """The width of the rectangle"""
        return self.right - self.left

    @property
    def height(self) -> float:
        """The height of the rectangle"""
        return self.bottom - self.top

    @property
    def topLeft(self) -> Point:
        """The top left point of the rectangle"""
        return Point(self.left, self.top)

    @property
    def topRight(self) -> Point:
        """The top right point of the rectangle"""
        return Point(self.right, self.top)

    @property
    def bottomLeft(self) -> Point:
        """The bottom left point of the rectangle"""
        return Point(self.left, self.bottom)

    @property
    def bottomRight(self) -> Point:
        """The bottom right point of the rectangle"""
        return Point(self.right, self.bottom)

    @property
    def center(self) -> Point:
        """The center point of the rectangle"""
        return Point(self.left + (self.width / 2), self.top + (self.height / 2))

    @property
    def area(self) -> float:
        """The area of the rectangle"""
        return self.width * self.height

    def __iter__(self) -> Iterable[float]:
        """Iterate through the left, top, right, and then bottom of the rectangle
        :return: left, top, right, then bottom of the rectangle"""
        yield self.left
        yield self.top
        yield self.right
        yield self.bottom

    def __bool__(self) -> bool:
        """If the rectangle is valid"""
        return self.area > 0

    def __lt__(self, point: Point) -> bool:
        """If a point is less than the rectangle
        :param point:"""
        return tuple(self) < tuple(point)

    @overload
    def __contains__(self, point: Point) -> bool:
        pass

    @overload
    def __contains__(self, rect: Rect) -> bool:
        pass

    def __contains__(self, item) -> bool:
        """If the rectangle contains a point or a rect

        :param Point|Rect item: Point or rectangle to check
        :return: If the point or rectangle is in this rectangle"""
        if isinstance(item, Point):
            return (
                self.left <= item.x <= self.right and self.top <= item.y <= self.bottom
            )

        if isinstance(item, Rect):
            return item.topLeft in self and item.bottomRight in self

        raise NotImplementedError()

    def __sub__(self, rect: Rect) -> Iterable[Rect]:
        """See :py:meth:`difference`"""
        return self.difference(rect)

    def __and__(self, rect: Rect) -> Rect | None:
        """See :py:meth:`intersect`"""
        return self.intersect(rect)

    def __xor__(self, rect: Rect) -> Region:
        """Returns the region without the :py:meth:`intersect` of rect

        :param rect:"""
        return Region(self, rect) - self.intersect(rect)

    def intersect(self, rect: Rect) -> Rect | None:
        """Returns the intersection of this rectangle and another rectangle

        :param rect: Rectangle to intersect
        :return: The intersection if there is any"""
        x1 = max(min(self.left, self.right), min(rect.left, rect.right))
        y1 = max(min(self.top, self.bottom), min(rect.top, rect.bottom))
        x2 = min(max(self.left, self.right), max(rect.left, rect.right))
        y2 = min(max(self.top, self.bottom), max(rect.top, rect.bottom))
        return Rect(x1, y1, x2, y2) if x1 < x2 and y1 < y2 else None

    def difference(self, rect: Rect) -> Iterable[Rect]:
        """Returns the difference of this rectangle and another rectangle

        :param rect: Rectangle to difference
        :return: Rectangles that make up the difference"""
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
        """Check if a rectangle intersects this rectangle

        :param rect: Rectangle to compare with
        :return: If they intersect"""
        return (
            rect.topLeft in self
            or rect.bottomRight in self
            or self.topLeft in rect
            or self.bottomRight in rect
        )

    def toInt(self) -> Rect:
        """Clone and return a rect where left, top, right, and bottom have been converted into integers
        :return: Cloned rectangle with integer coordinates"""
        return Rect(int(self.left), int(self.top), int(self.right), int(self.bottom))


class Region(MutableSet[Rect]):
    """A collection of rectangles"""

    def __init__(self, *rects: list[Rect]) -> Self:
        """Create a new instance

        :param rects: Rectangles that make up this region"""
        self.elements = set(rects)  #: Rectangles that make up the region

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
        """Checks if a point, rect, or region is contained in this region

        :param Point|Rect|Region item: Item to compare
        :return: If the item is contained in the region"""
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
        """Iterate through :py:data:`elements`"""
        return iter(self.elements)

    def __len__(self) -> int:
        """Number of :py:data:`elements` in the region"""
        return len(self.elements)

    @overload
    def __iadd__(self, rect: Rect) -> Self:
        pass

    @overload
    def __iadd__(self, rect: Iterable[Rect]) -> Self:
        pass

    @overload
    def __iadd__(self, region: Region) -> Self:
        pass

    def __iadd__(self, item) -> Self:
        """Add a rect or region to this region

        :param Rect|Iterable[Rect]|Region item: Item to add to the region"""
        if item is None:
            return self

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
        """Create a clone that adds one or more rect or a region to this region

        :param Rect|Iterable[Rect]|Region item: Item to add to the cloned region
        :return: clone merged with item"""
        region = Region(*self.elements)
        if item is None:
            return region

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
    def __isub__(self, rect: Iterable[Rect]) -> Self:
        pass

    @overload
    def __isub__(self, region: Region) -> Self:
        pass

    def __isub__(self, item) -> Self:
        """Remove a rect or region from this region

        :param Rect|Iterable[Rect]|Region item: Item(s) to remove"""
        if isinstance(item, Rect):
            self.discard(item)
            return self

        if isinstance(item, Region) or isinstance(item, Iterable):
            for rect in item:
                self.discard(rect)

            return self

        raise NotImplementedError()

    @overload
    def __sub__(self, rect: Rect) -> Region:
        pass

    @overload
    def __sub__(self, rect: Iterable[Rect]) -> Region:
        pass

    @overload
    def __sub__(self, region: Region) -> Region:
        pass

    def __sub__(self, item) -> Region:
        """Create a clone of the region and then remove the rect(s) from the clone

        :param Rect|Iterable[Rect]|Region item: Item(s) to remove
        :return: clone without the rect(s)"""
        region = Region(*self.elements)
        if isinstance(item, Rect):
            region.discard(item)
            return region

        if isinstance(item, Region) or isinstance(item, Iterable[Rect]):
            for rect in item:
                region.discard(rect)

            return region

        raise NotImplementedError()

    def add(self, rect: Rect) -> None:
        """Add a rect to the region

        :param rect: rect to add"""
        if not rect or rect in self:
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
        """Remove a rectangle from the region."""
        for r in list(self):
            self.elements.discard(r)
            self += list(r - rect)

    @property
    def toInt(self) -> Region:
        """Create a clone and convert all rects in the clone to integer coordinates"""
        return Region([x.toInt() for x in self])

    @property
    def boundingRect(self) -> Rect:
        """Get a rectangle that contains all the rectangles in the region"""
        if not self:
            return Rect(0, 0, 0, 0)

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
