from __future__ import annotations

import os

from typing import Self
from typing import Any
from collections.abc import Callable

from ._typing import override

from ._safe_property import safe_property

from ._framebuffer import FrameBuffer
from ._framebuffer import WaveformMode
from ._framebuffer import DEFAULT_FONT_SIZE

from .geometry import Rect
from .geometry import Region

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from weakref import ref
from typing import Iterable


class Scene:
    """Scene with widgets"""

    def __init__(
        self,
        fb: FrameBuffer,
        children: list[Widget] = [],
        background: str | tuple = "white",
    ):
        """Create a new scene

        :param fb: framebuffer instance to draw the scene to
        :param children: widgets to add to the scene
        :param background: Background colour"""
        self.fb = fb  #: Framebuffer instance
        self.children = children  #: Child widgets
        for widget in self.children:
            widget.parent = ref(self)

        self.buffer = Image.new(
            "RGBA",
            (self.fb.width(), self.fb.height()),
            background,
        )  #: Buffer for scene

    @property
    def screenRect(self) -> Rect:
        """Screen geometry for widgets to use when doing layout"""
        # TODO handle landscape
        return Rect(0, 0, self.fb.width(), self.fb.height())

    @property
    def changed(self) -> Iterable[Widget]:
        """Widgets that have changed and need to be re-painted"""
        for widget in self.children:
            if widget.dirty or list(widget.changed):
                yield widget

    def update(self, fullUpdate: bool = False):
        """Perform a screen update. This first performs layout on all the widgets, re-paints any changes
        to the buffer, and then updates the screen from the buffer

        :param fullUpdate: If the entire screen should be redrawn instead of just the changes
        """
        screenRect = self.screenRect
        # TODO handle landscape
        for widget in self.children:
            widget.layout(screenRect)

        region = Region()
        if fullUpdate:
            region += screenRect

        needsRepaint = Region()
        for widget in self.changed:
            if (
                widget.screenRect is None
                or widget.parent() is None
                or not widget.screenRect
            ):
                continue

            region += widget.paint(self.buffer)
            needsRepaint += widget.oldScreenRect - widget.screenRect
            widget.dirty = False

        # TODO sort out how to paint less
        d = ImageDraw.Draw(self.buffer)
        for rect in needsRepaint:
            d.rectangle((tuple(rect.topLeft), tuple(rect.bottomRight)), "white")

        for widget in self.children:
            if widget.rect in needsRepaint:
                widget.paint(self.buffer)

        region += needsRepaint
        markers = []
        for rect in region:
            left, top, right, bottom = rect
            cropped = self.buffer.crop((left, top, right, bottom))
            self.fb.draw_image(left, top, cropped)
            markers.append(
                self.fb.update(
                    left,
                    top,
                    rect.width,
                    rect.height,
                    waveform=WaveformMode.HighQualityGrayscale,
                )
            )

        for marker in markers:
            self.fb.wait(marker)


def widgetProperty(func: Callable[Self, Any] | str, T: type | None = None):
    """Decorator"""
    if isinstance(func, str):

        def noop(x):
            pass

        name = func
        func = noop

    else:
        name = func.__name__
        T = next(iter(func.__annotations__))

    def setter(self, value: T):
        func(value)
        self._data[name] = value
        self.dirty = True

    def getter(self) -> T:
        return self._data[name]

    return property(getter, setter)


class Widget:
    def __init__(self, left: float, top: float, right: float, bottom: float):
        assert 0 <= left <= 1
        assert 0 <= top <= 1
        assert 0 <= right <= 1
        assert 0 <= bottom <= 1
        self.rect = Rect(left, top, right, bottom)
        self.oldRect = Rect(0, 0, 0, 0)
        self.parent: ref[Widget | Scene] = None  #: Parent widget or scene
        self._children: list[Widget] = []
        self.dirty: bool = True
        self.screenRect: Rect = Rect(0, 0, 0, 0)
        self.oldScreenRect: Rect = Rect(0, 0, 0, 0)

    @property
    def children(self) -> list[Widget]:
        return self._children

    @property
    def left(self):
        return self.rect.left

    @left.setter
    def left(self, left: float):
        assert 0 <= left <= 1
        self.rect.left = left
        self.dirty = True

    @property
    def top(self):
        return self.rect.top

    @top.setter
    def top(self, top: float):
        assert 0 <= top <= 1
        self.rect.top = top
        self.dirty = True

    @property
    def right(self):
        return self.rect.right

    @right.setter
    def right(self, right: float):
        assert 0 <= right <= 1
        self.rect.right = right
        self.dirty = True

    @property
    def bottom(self):
        return self.rect.bottom

    @bottom.setter
    def bottom(self, bottom: float):
        assert 0 <= bottom <= 1
        self.rect.bottom = bottom
        self.dirty = True

    @property
    def width(self):
        return self.rect.width

    @width.setter
    def width(self, width: float):
        assert 0 <= width <= 1
        self.resize(width, self.height)
        self.dirty = True

    @property
    def height(self):
        return self.rect.height

    @height.setter
    def height(self, height: float):
        assert 0 <= height <= 1
        self.resize(self.width, height)
        self.dirty = True

    @property
    def changed(self) -> Iterable[Widget]:
        for widget in self.children:
            if widget.dirty or list(widget.changed):
                yield widget

    @property
    def scene(self) -> Scene | None:
        parent = self.parent()
        while not isinstance(parent, Scene):
            if parent is None:
                return None

            parent = parent.parent()

        return parent

    @property
    def image(self) -> Image | None:
        assert self.screenRect is not None
        if not self.screenRect:
            return None

        assert self.screenRect.width > 0
        assert self.screenRect.height > 0
        return Image.new(
            "RGBA",
            (self.screenRect.width, self.screenRect.height),
            (0, 0, 0, 0),
        )

    @property
    def drawRect(self) -> Rect:
        left, top, right, bottom = self.screenRect
        parent = self.parent()
        if not isinstance(parent, Scene):
            rect = parent.screenRect
            left = int(left - rect.left)
            top = int(top - rect.top)
            right = int(right - rect.left)
            bottom = int(bottom - rect.top)

        return Rect(left, top, right, bottom)

    def translate(self, x: float, y: float):
        assert -1 <= x <= 1
        assert -1 <= y <= 1
        w, h = self.width, self.height
        self.left += x
        self.top += y
        self.resize(w, h)

    def resize(self, width: float, height: float):
        assert -1 <= width <= 1
        assert -1 <= height <= 1
        self.right = self.left + width
        self.bottom = self.top + height

    def layout(self, screenRect: Rect):
        self.oldScreenRect = self.screenRect
        self.screenRect = Rect(
            screenRect.left + (self.left * screenRect.width),
            screenRect.top + (self.top * screenRect.height),
            screenRect.left + (self.right * screenRect.width),
            screenRect.top + (self.bottom * screenRect.height),
        ).toInt()
        if self.oldScreenRect != self.screenRect:
            self.dirty = True

        for widget in self.children:
            if widget.parent is None:
                widget.parent = ref(self)

            widget.layout(self.screenRect)

    def paint_children(self, image: Image, region: Region) -> Region:
        needsRepaint = Region()
        for widget in self.changed:
            if widget.screenRect is None or not widget.screenRect:
                continue

            region += widget.paint(image)
            needsRepaint += widget.oldScreenRect - widget.screenRect
            widget.dirty = False

        # TODO sort out how to paint less
        d = ImageDraw.Draw(image)
        for rect in needsRepaint:
            d.rectangle((tuple(rect.topLeft), tuple(rect.bottomRight)), (0, 0, 0, 0))

        for widget in self.children:
            if widget.rect in needsRepaint:
                widget.paint(image)

        return needsRepaint

    def paint(self, image: Image) -> Region:
        region = Region(self.screenRect) if self.dirty else Region()
        widgetImage = self.image
        if widgetImage is None:
            return Region()

        assert widgetImage.width == self.screenRect.width
        assert widgetImage.height == self.screenRect.height
        region += self.paint_children(widgetImage, region)
        left, top, right, bottom = self.drawRect
        image.paste(widgetImage, (left, top), widgetImage)
        return region


class IChildlessWidget:
    """Mixin to disable children on a widget"""

    @override
    @safe_property
    def children(self) -> list[Widget]:
        return []

    @override
    def paint_children(self, image: Image, region: Region) -> Region:
        return Region()


class IImagelessWidget:
    """Mixin to disable the image property on a widget, rendering is instead handled by a custom paint() method"""

    @override
    @property
    def image(self) -> Image:
        raise NotImplementedError()

    @override
    def paint(self, image: Image) -> Region:
        raise NotImplementedError()


class IAlwaysRenderWidget:
    """Mixin to make a widget always render"""

    @override
    @property
    def dirty(self) -> bool:
        return True

    @dirty.setter
    def dirty(self, dirty: bool):
        pass


class Text(IChildlessWidget, IImagelessWidget, Widget):
    """Text widget"""

    def __init__(
        self,
        left: float,
        top: float,
        right: float,
        bottom: float,
        text: str = "",
        color: str = "black",
        fontSize: int = DEFAULT_FONT_SIZE,
    ):
        super().__init__(left, top, right, bottom)
        self._data = {
            "text": text,
            "color": color,
            "fontSize": fontSize,
        }

    text = widgetProperty("text", str)
    color = widgetProperty("color", str)
    fontSize = widgetProperty("fontSize", int)

    @override
    def paint(self, image: Image) -> Region:
        if self.screenRect is None or self.parent() is None or not self.screenRect:
            return Region()

        left, top, right, bottom = self.drawRect
        d = ImageDraw.Draw(image)
        d.fontmode = "L"
        d.multiline_text(
            (left, top),
            self.text,
            self.color,
            font=ImageFont.load_default(size=self.fontSize),
        )
        return Region(self.screenRect) if self.dirty else Region()


class Rectangle(IImagelessWidget, Widget):
    """Rectangle widget"""

    def __init__(
        self,
        left: float,
        top: float,
        right: float,
        bottom: float,
        background: str = "white",
        color: str | None = None,
        lineWidth: int = 1,
    ):
        super().__init__(left, top, right, bottom)
        self._data = {
            "background": background,
            "color": color,
            "lineWidth": lineWidth,
        }

    background = widgetProperty("background", str | None)
    color = widgetProperty("color", str | None)

    @widgetProperty
    def lineWidth(lineWidth: int):
        assert lineWidth > 0

    @override
    def paint(self, image: Image) -> Region:
        left, top, right, bottom = self.drawRect
        d = ImageDraw.Draw(image)
        d.rectangle(
            ((left, top), (right - self.lineWidth, bottom - self.lineWidth)),
            self.background,
            self.color,
            self.lineWidth,
        )
        region = Region(self.screenRect) if self.dirty else Region()
        if self.children:
            widgetImage = image.crop((left, top, right, bottom))
            region += self.paint_children(widgetImage, region)
            image.paste(widgetImage, (left, top), widgetImage)

        return region


class Picture(IChildlessWidget, IImagelessWidget, Widget):
    """Image widget"""

    def __init__(
        self,
        left: float,
        top: float,
        right: float,
        bottom: float,
        path: str,
        background: str = "white",
    ):
        super().__init__(left, top, right, bottom)
        assert os.path.exists(path)
        self._data = {
            "path": path,
            "background": background,
        }

    background = widgetProperty("background", str)

    @widgetProperty
    def path(path: str):
        assert os.path.exists(path)

    @override
    def paint(self, image: Image) -> Region:
        left, top, right, bottom = self.drawRect
        d = ImageDraw.Draw(image)
        d.rectangle(((left, top), (right, bottom)), self.background)
        thumbnail = Image.open(self.path)
        thumbnail.thumbnail((self.screenRect.width, self.screenRect.height))
        image.paste(thumbnail, (left, top), thumbnail)
        region = Region(self.screenRect) if self.dirty else Region()
        return region
