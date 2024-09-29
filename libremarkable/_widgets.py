from __future__ import annotations

from ._framebuffer import FrameBuffer
from ._framebuffer import WaveformMode
from ._framebuffer import DEFAULT_FONT_SIZE

from ._device import Orientation
from ._device import orientation

from .geometry import Rect
from .geometry import Region

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from weakref import ref
from typing import Iterable


class Scene:
    """Scene with widgets"""

    def __init__(self, fb: FrameBuffer, children: list[Widget] = []):
        self.fb = fb  #: Framebuffer instance
        self.children = children  #: Child widgets
        for widget in self.children:
            widget.parent = ref(self)

        self.buffer = Image.new(
            "RGBA", (self.fb.width(), self.fb.height()), "white"
        )  #: Buffer for scene

    @property
    def screenRect(self) -> Rect:
        if orientation() != Orientation.LANDSCAPE:
            return Rect(0, 0, self.fb.width(), self.fb.height())

        return Rect(0, 0, self.fb.height(), self.fb.width())

    @property
    def changed(self) -> Iterable[Widget]:
        for widget in self.children:
            if widget.dirty or list(widget.changed):
                yield widget

    def update(self):
        screenRect = self.screenRect
        for widget in self.children:
            widget.layout(screenRect)

        region = Region()
        needsRepaint = Region()
        for widget in self.changed:
            paintedRegion = widget.paint(self.buffer)
            needsRepaint += widget.oldScreenRect - widget.screenRect
            region += paintedRegion

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


class Widget:
    def __init__(self, left: float, top: float, right: float, bottom: float):
        assert 0 <= left <= 1
        assert 0 <= top <= 1
        assert 0 <= right <= 1
        assert 0 <= bottom <= 1
        self.rect = Rect(left, top, right, bottom)
        self.oldRect = Rect(0, 0, 0, 0)
        self.parent: Widget | Scene = None  #: Parent widget or scene
        self.children: list[Widget] = []
        self.dirty: bool = True
        self.screenRect: Rect = Rect(0, 0, 0, 0)
        self.oldScreenRect: Rect = Rect(0, 0, 0, 0)

    @property
    def left(self):
        return self.rect.left

    @left.setter
    def left(self, left: int):
        assert 0 <= left <= 1
        self.rect.left = left

    @property
    def top(self):
        return self.rect.top

    @top.setter
    def top(self, top: int):
        assert 0 <= top <= 1
        self.rect.top = top

    @property
    def right(self):
        return self.rect.right

    @right.setter
    def right(self, right: int):
        assert 0 <= right <= 1
        self.rect.right = right

    @property
    def bottom(self):
        return self.rect.bottom

    @bottom.setter
    def bottom(self, bottom: int):
        assert 0 <= bottom <= 1
        self.rect.bottom = bottom

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

    @property
    def changed(self) -> Iterable[Widget]:
        if self.dirty:
            yield self
            return

        for widget in self.children:
            for widget2 in widget.changed:
                yield widget2

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

    def paint(self, image: Image) -> Region:
        if self.screenRect is None or self.parent() is None or not self.screenRect:
            return Rect(0, 0, 0, 0)

        region = Region()
        if self.dirty:
            region.add(self.screenRect)
            self.dirty = False

        widgetImage = self.image
        if widgetImage is None:
            return Rect(0, 0, 0, 0)

        assert widgetImage.width == self.screenRect.width
        assert widgetImage.height == self.screenRect.height
        needsRepaint = Region()
        for widget in self.children:
            paintedRegion = widget.paint(widgetImage)
            needsRepaint += widget.oldScreenRect - widget.screenRect
            region += paintedRegion

        # TODO sort out how to paint less
        for widget in self.children:
            if widget.rect in needsRepaint:
                widget.paint(widgetImage)

        region += needsRepaint
        left, top, right, bottom = self.screenRect
        parent = self.parent()
        if not isinstance(parent, Scene):
            rect = parent.screenRect
            left = int(left - rect.left)
            top = int(top - rect.top)
            right = int(right - rect.left)
            bottom = int(bottom - rect.top)

        background = image.crop((left, top, right, bottom))
        composite = Image.alpha_composite(background, widgetImage)
        image.paste(composite, (left, top), composite)
        return region


class Text(Widget):
    text: str = ""
    color: str = "black"
    fontSize: int = DEFAULT_FONT_SIZE

    @property
    def image(self) -> Image:
        image = super().image
        d = ImageDraw.Draw(image)
        d.fontmode = "L"
        d.text(
            (0, 0),
            self.text,
            self.color,
            font=ImageFont.load_default(size=self.fontSize),
        )
        return image


class Rectangle(Widget):
    color: str = "white"

    @property
    def image(self) -> Image:
        return Image.new(
            "RGBA",
            (self.screenRect.width, self.screenRect.height),
            self.color,
        )
