import os

from collections.abc import Iterable

from bresenham import bresenham

from mmap import mmap
from mmap import MAP_SHARED
from mmap import MAP_POPULATE
from mmap import PROT_READ
from mmap import PROT_WRITE
from mmap import ACCESS_DEFAULT

from ctypes import sizeof

from contextlib import contextmanager

from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont

from . import _mxcfb
from . import _rm2fb

from ._color import c_t
from ._color import getrgb

from ._device import DeviceType
from ._device import current

from ._mxcfb import WaveformMode
from ._mxcfb import UPDATE_MODE_PARTIAL
from ._mxcfb import UPDATE_MODE_FULL
from ._mxcfb import mxcfb_update_data

# from ._mxcfb import TEMP_USE_REMARKABLE_DRAW

IMAGE_MODE = "I;16"

_fb = None
_marker = 0


def implementation():
    # As these may change at runtime, they are methods instead of stored at startup
    if current == DeviceType.RM1:
        return _mxcfb

    if current == DeviceType.RM2:
        assert os.path.exists(_rm2fb.path())
        return _rm2fb

    if os.path.exists(_rm2fb.path()):
        return _rm2fb

    return _mxcfb


def _set_line_to_data(x: int, y: int, data) -> None:
    _ensure_fb()["data"][
        FrameBuffer.get_offset(x, y) : FrameBuffer.get_offset(x + len(data), y)
    ] = data


def _ensure_fb():
    global _fb
    if _fb is None:
        FrameBuffer.mmap().__enter__()

    return _fb


class FrameBuffer:
    @staticmethod
    def path():
        return implementation().path()

    @classmethod
    def open(cls):
        return open(cls.path(), "r+b")

    @staticmethod
    def size():
        size = implementation().getsize()
        assert size, "Framebuffer size is invalid"
        return size

    @staticmethod
    def width() -> int:
        return implementation().width()

    @staticmethod
    def height() -> int:
        return implementation().height()

    @staticmethod
    def pixel_size() -> int:
        return implementation().pixel_size()

    @staticmethod
    def virtual_width() -> int:
        return implementation().virtual_width()

    @staticmethod
    def virtual_height() -> int:
        return implementation().virtual_height()

    @staticmethod
    def x_offset() -> int:
        return implementation().x_offset()

    @staticmethod
    def y_offset() -> int:
        return implementation().y_offset()

    @classmethod
    @contextmanager
    def mmap(cls):
        global _fb
        if _fb is None:
            f = cls.open()
            size = cls.size()
            mm = mmap(
                f.fileno(),
                size,
                flags=MAP_SHARED | MAP_POPULATE,
                prot=PROT_READ | PROT_WRITE,
                access=ACCESS_DEFAULT,
            )
            offset = cls.get_offset(0, 0)
            _fb = {
                "f": f,
                "mm": mm,
                "data": (c_t * int(size / sizeof(c_t))).from_buffer(mm),
                "offset": offset,
                "image": Image.frombuffer(
                    IMAGE_MODE,
                    (cls.virtual_width(), cls.virtual_height()),
                    mm,
                ),
            }

        yield _fb["data"]

    @staticmethod
    def release():
        global _fb
        if _fb is not None:
            _fb["image"].close()
            del _fb["data"]
            _fb["data"] = None
            _fb["mm"].close()
            _fb["f"].close()
            _fb = None

    @classmethod
    def update(
        cls,
        x: int,
        y: int,
        width: int,
        height: int,
        waveform: WaveformMode,
        marker: int = None,
        partial=True,
        sync=False,
    ) -> int:
        if marker is None:
            global _marker
            marker = _marker = _marker + 1

        data = mxcfb_update_data()
        data.update_region.left = x
        data.update_region.top = y
        data.update_region.width = width
        data.update_region.height = height
        data.waveform_mode = waveform
        data.update_mode = UPDATE_MODE_PARTIAL if partial else UPDATE_MODE_FULL
        # data.temp = TEMP_USE_REMARKABLE_DRAW
        data.update_marker = marker
        implementation().update(data)
        if sync:
            cls.wait(data.update_marker)

        return data.update_marker

    @classmethod
    def update_full(cls, waveform: WaveformMode, marker: int = None, sync=False):
        cls.update(
            0,
            0,
            cls.width(),
            cls.height(),
            waveform,
            marker,
            partial=False,
            sync=sync,
        )

    @staticmethod
    def wait(marker: int) -> None:
        implementation().wait(marker)

    @classmethod
    def get_row_offset(cls, y: int) -> int:
        assert 0 <= y <= cls.height()
        return (y + cls.y_offset()) * cls.virtual_width()

    @classmethod
    def get_offset(cls, x: int, y: int) -> int:
        assert 0 <= x <= cls.width(), f"{x} not within bounds"
        assert 0 <= y <= cls.height(), f"{y} not within bounds"
        return cls.get_row_offset(y) + x + cls.x_offset()

    @classmethod
    def set_pixel(cls, x: int, y: int, color: c_t | str) -> None:
        if isinstance(color, str):
            color = cls.getcolor(color)

        _ensure_fb()["data"][cls.get_offset(x, y)] = color

    @classmethod
    def get_pixel(cls, x: int, y: int) -> int:
        return _ensure_fb()["data"][cls.get_offset(x, y)]

    @classmethod
    def set_row(cls, x: int, y: int, width: int, color: c_t | str) -> None:
        assert width > 0
        assert x + width <= cls.width()
        if isinstance(color, str):
            color = cls.getcolor(color)

        data = (c_t * width).from_buffer(bytearray(color) * width)
        _set_line_to_data(x, y, data)

    @classmethod
    def get_row(cls, x: int, y: int, width: int) -> tuple[int]:
        return _ensure_fb()["data"][cls.get_offset(x, y) : cls.get_offset(x + width, y)]

    @classmethod
    def set_col(cls, x: int, y: int, height: int, color: c_t | str) -> None:
        assert height
        assert x + height <= height()
        if isinstance(color, str):
            color = cls.getcolor(color)

        for i in range(y, y + height):
            cls.set_pixel(x, i, color)

    @classmethod
    def set_rect(
        cls,
        left: int,
        top: int,
        width: int,
        height: int,
        color: c_t | str,
    ) -> None:
        assert 0 <= left < cls.width(), f"left of {left} is invalid"
        assert 0 <= top < cls.height(), f"top of {top} is invalid"
        assert 0 < width <= cls.width() - left, f"width of {width} is invalid"
        assert 0 < height <= cls.height() - top, f"height of {height} is invalid"
        if isinstance(color, str):
            color = cls.getcolor(color)

        data = (c_t * width).from_buffer(bytearray(color) * width)
        for y in range(top, top + height):
            _set_line_to_data(left, y, data)

    @classmethod
    def set_color(cls, color: c_t | str) -> None:
        if isinstance(color, str):
            color = cls.getcolor(color)

        cls.set_rect(0, 0, cls.width(), cls.height(), color)

    @classmethod
    def draw_rect(
        cls,
        left: int,
        top: int,
        right: int,
        bottom: int,
        color: c_t | str,
        lineSize: int = 1,
    ) -> None:
        if isinstance(color, str):
            color = cls.getcolor(color)

        cls.set_rect(left, top, right - left, lineSize, color)  # Top line
        cls.set_rect(
            left, bottom - lineSize, right - left, lineSize, color
        )  # Bottom line
        cls.set_rect(left, top, lineSize, bottom - top, color)  # Left line
        cls.set_rect(right - lineSize, top, lineSize, bottom - top, color)  # Right line

    @classmethod
    def draw_image(cls, left: int, top: int, image: Image) -> None:
        width = image.width
        height = image.height

        assert 0 <= left < cls.width(), f"left of {left} is invalid"
        assert 0 <= top < cls.height(), f"top of {top} is invalid"
        assert 0 < width <= cls.width() - left, f"width of {width} is invalid"
        assert 0 < height <= cls.height() - top, f"height of {height} is invalid"

        if image.mode != IMAGE_MODE:
            image = image.convert(IMAGE_MODE)

        data = (c_t * (image.width * image.height)).from_buffer_copy(image.tobytes())
        for y in range(0, image.height):
            _set_line_to_data(left, top + y, data[y * width : y * width + width])

    @classmethod
    def draw_text(
        cls,
        left: int,
        top: int,
        width: int,
        height: int,
        text: str,
        color: c_t | str = "black",
        fontSize: int = 16,
    ):
        image = cls.to_image(left, top, width, height)
        if isinstance(color, str):
            color = ImageColor.getcolor(color, image.mode)

        else:
            # TODO - handle when IMAGE_MODE has more bands
            color = color.value

        ImageDraw.Draw(image).text(
            (0, 0),
            text,
            color,
            font=ImageFont.load_default(size=fontSize),
        )
        cls.draw_image(left, top, image)

    @classmethod
    def draw_multiline_text(
        cls,
        left: int,
        top: int,
        width: int,
        height: int,
        text: str,
        color: c_t | str = "black",
        fontSize: int = 16,
        align: str = "left",
    ):
        image = cls.to_image(left, top, width, height)
        if isinstance(color, str):
            color = ImageColor.getcolor(color, image.mode)

        else:
            # TODO - handle when IMAGE_MODE has more bands
            color = color.value

        ImageDraw.Draw(image).multiline_text(
            (0, 0),
            text,
            color,
            font=ImageFont.load_default(size=fontSize),
        )
        cls.draw_image(left, top, image)

    @classmethod
    def to_image(
        cls,
        left: int = 0,
        top: int = 0,
        width: int = None,
        height: int = None,
    ) -> Image:
        if width is None:
            width = cls.width()

        if height is None:
            height = cls.height()

        assert 0 <= left < cls.width(), f"left of {left} is invalid"
        assert 0 <= top < cls.height(), f"top of {top} is invalid"
        assert 0 < width <= cls.width() - left, f"width of {width} is invalid"
        assert 0 < height <= cls.height() - top, f"height of {height} is invalid"

        left += cls.x_offset()
        top += cls.y_offset()
        return _ensure_fb()["image"].crop((left, top, left + width, top + height))

    @staticmethod
    def getcolor(name_or_hex: str) -> c_t:
        return getrgb(name_or_hex)

    @classmethod
    def __getitem__(cls, key: int | slice | tuple[int, int]) -> c_t:
        f = _ensure_fb()
        if isinstance(key, tuple):
            x, y = key
            return cls.get_pixel(x, y)

        if isinstance(key, slice):
            startY = int(key.start / cls.width())
            endY = int(key.stop / cls.width())
            data = []
            for y in range(startY, endY + 1):
                startX = key.start - (startY * cls.width()) if y == startY else 0
                endX = (
                    key.stop - (endY * cls.width())
                    if y == endY
                    else cls.width() - startX
                )
                startOffset = cls.get_offset(startX, y)
                stopOffset = cls.get_offset(endX, y)
                step = key.step or 1
                data += f["data"][startOffset:stopOffset:step]

            return data

        if isinstance(key, int):
            y = int(key / cls.width())
            return f["data"][cls.get_offset(key - y, y)]

        raise NotImplementedError()

    @classmethod
    def __setitem__(
        cls,
        key: int | slice | tuple[int, int],
        value: c_t | str | Iterable[c_t] | Iterable[str],
    ) -> None:
        f = _ensure_fb()
        if isinstance(key, tuple):
            assert isinstance(value, c_t) or isinstance(value, str)
            x, y = key
            cls.set_pixel(x, y, value)

        elif isinstance(key, slice):
            assert isinstance(value, Iterable)
            value = [cls.getcolor(x) if isinstance(x, str) else x for x in value]
            startY = int(key.start / cls.width())
            endY = int(key.stop / cls.width())
            startValueOffset = 0
            for y in range(startY, endY + 1):
                startX = key.start - (startY * cls.width()) if y == startY else 0
                endX = (
                    key.stop - (endY * cls.width())
                    if y == endY
                    else cls.width() - startX
                )
                startOffset = cls.get_offset(startX, y)
                stopOffset = cls.get_offset(endX, y)
                step = key.step or 1
                size = stopOffset - startOffset
                stopValueOffset = startValueOffset + size
                f["data"][startOffset:stopOffset:step] = value[
                    startValueOffset:stopValueOffset:step
                ]
                startValueOffset += size

        elif isinstance(key, int):
            assert isinstance(value, c_t) or isinstance(value, str)
            y = int(key / cls.width())
            f["data"][cls.get_offset(key - y, y)] = value

        else:
            raise NotImplementedError()

    @classmethod
    def __iter__(cls) -> iter:
        return iter(_ensure_fb()["data"])

    @classmethod
    def __len__(cls) -> int:
        return cls.width() * cls.height()

    @classmethod
    def __contains__(cls, color: c_t | str | int) -> bool:
        if isinstance(color, str):
            color = cls.getcolor(color)

        if isinstance(color, c_t):
            color = color.value

        for y in range(0, cls.height()):
            if color in cls.get_row(0, y, cls.width()):
                return True

        return False

    @classmethod
    def draw_line(cls, x1: int, y1: int, x2: int, y2: int, color: c_t | str) -> None:
        for x, y in bresenham(x1, y1, x2, y2):
            cls.set_pixel(x, y, color)
