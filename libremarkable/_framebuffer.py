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

from ._color import color_t
from ._color import getrgb

from ._device import DeviceType
from ._device import current

from ._mxcfb import WaveformMode
from ._mxcfb import UPDATE_MODE_PARTIAL
from ._mxcfb import UPDATE_MODE_FULL
from ._mxcfb import mxcfb_update_data
from ._mxcfb import TEMP_USE_REMARKABLE_DRAW

IMAGE_MODE = "I;16"  #: Image mode used by framebuffer
DEFAULT_FONT_SIZE = 24  #: Default font size

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
    """Framebuffer"""

    def __init__(self):
        implementation().setup()

    @staticmethod
    def path():
        """Path to framebuffer device"""
        return implementation().path()

    @classmethod
    def open(cls):
        """Open the framebuffer"""
        return open(cls.path(), "r+b")

    @staticmethod
    def size():
        """Get the size of the framebuffer in bytes"""
        size = implementation().getsize()
        assert size, "Framebuffer size is invalid"
        return size

    @staticmethod
    def width() -> int:
        """Get the width of the framebufffer"""
        return implementation().width()

    @staticmethod
    def height() -> int:
        """Get the height of the framebufffer"""
        return implementation().height()

    @staticmethod
    def pixel_size() -> int:
        """Get the pixel size of the framebufffer in bytes"""
        return implementation().pixel_size()

    @staticmethod
    def virtual_width() -> int:
        """Get the virtual width of the framebufffer"""
        return implementation().virtual_width()

    @staticmethod
    def virtual_height() -> int:
        """Get the virtual height of the framebufffer"""
        return implementation().virtual_height()

    @staticmethod
    def x_offset() -> int:
        """Get the x offset of the framebufffer"""
        return implementation().x_offset()

    @staticmethod
    def y_offset() -> int:
        """Get the y offset of the framebufffer"""
        return implementation().y_offset()

    @classmethod
    @contextmanager
    def mmap(cls):
        """memory map the framebuffer"""
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
                "data": (color_t * int(size / sizeof(color_t))).from_buffer(mm),
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
        """Release the framebuffer"""
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
        partial: bool = True,
        sync: bool = False,
    ) -> int:
        """Update a portion of the screen with the contents of the framebuffer memory

        :param x: x coordinate of area to update
        :param y: y coordinate of area to update
        :param width: width of area to update
        :param height:  height of area to update
        :param waveform: Waveform to use for the update
        :param marker: Update Marker
        :param partial: Partial or full screen update
        :param sync: Perform update synchronously
        :return: Update marker"""
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
        data.temp = TEMP_USE_REMARKABLE_DRAW
        data.update_marker = marker
        implementation().update(data)
        if sync:
            cls.wait(data.update_marker)

        return data.update_marker

    @classmethod
    def update_full(
        cls,
        waveform: WaveformMode,
        marker: int = None,
        sync: bool = False,
    ) -> int:
        """Update the screen with the contents of the framebuffer memory

        :param waveform: Waveform to use for the update
        :param marker: Update Marker
        :param sync: Perform update synchronously
        :return: Update marker"""
        return cls.update(
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
        """Wait for an update to finish

        :param marker: Update marker"""
        implementation().wait(marker)

    @classmethod
    def get_row_offset(cls, y: int) -> int:
        """Get the offset of a row on the framebuffer

        :param y: y coordinate of the row
        :return: byte offset"""
        assert 0 <= y <= cls.height()
        return (y + cls.y_offset()) * cls.virtual_width()

    @classmethod
    def get_offset(cls, x: int, y: int) -> int:
        """Get the offset of a x,y on the framebuffer

        :param x: x coordinate
        :param y: y coordinate
        :return: byte offset"""
        assert 0 <= x <= cls.width(), f"{x} not within bounds"
        assert 0 <= y <= cls.height(), f"{y} not within bounds"
        return cls.get_row_offset(y) + x + cls.x_offset()

    @classmethod
    def set_pixel(cls, x: int, y: int, color: color_t | str) -> None:
        """Set a pixel in the framebuffer memory to a colour

        :param x: x coordinate
        :param y: y coordinate
        :color: colour value or string name of colour to use"""
        if isinstance(color, str):
            color = cls.getcolor(color)

        _ensure_fb()["data"][cls.get_offset(x, y)] = color

    @classmethod
    def get_pixel(cls, x: int, y: int) -> int:
        """Get the value for a pixel in the framebuffer memory

        :param x: x coordinate
        :param y: y coordinate
        :return: pixel value"""
        return _ensure_fb()["data"][cls.get_offset(x, y)]

    @classmethod
    def set_row(cls, x: int, y: int, width: int, color: color_t | str) -> None:
        """Set a row in the framebuffer memory to a colour

        :param x: x coordinate
        :param y: y coordinate
        :param width: width on row to set
        :param color: colour value or string name of colour to use"""
        assert width > 0
        assert x + width <= cls.width()
        if isinstance(color, str):
            color = cls.getcolor(color)

        data = (color_t * width).from_buffer(bytearray(color) * width)
        _set_line_to_data(x, y, data)

    @classmethod
    def get_row(cls, x: int, y: int, width: int) -> tuple[int]:
        """Get the data for a row in the framebuffer memory

        :param x: x coordinate
        :param y: y coordinate
        :param width: width on row to get
        :return: slice of data from row"""
        return _ensure_fb()["data"][cls.get_offset(x, y) : cls.get_offset(x + width, y)]

    @classmethod
    def set_col(cls, x: int, y: int, height: int, color: color_t | str) -> None:
        """Set a column in the framebuffer memory to a colour

        :param x: x coordinate
        :param y: y coordinate
        :param height: height of column to set
        :param color: colour value or name of colour to use"""
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
        color: color_t | str,
    ) -> None:
        """Set a rectangle in the framebuffer memory to a colour

        :param left: x coordinate
        :param top: y coordinate
        :param width: width of rectangle
        :param height: height of rectangle
        :param color: colour value or name of colour to use"""
        assert 0 <= left < cls.width(), f"left of {left} is invalid"
        assert 0 <= top < cls.height(), f"top of {top} is invalid"
        assert 0 < width <= cls.width() - left, f"width of {width} is invalid"
        assert 0 < height <= cls.height() - top, f"height of {height} is invalid"
        if isinstance(color, str):
            color = cls.getcolor(color)

        data = (color_t * width).from_buffer(bytearray(color) * width)
        for y in range(top, top + height):
            _set_line_to_data(left, y, data)

    @classmethod
    def set_color(cls, color: color_t | str) -> None:
        """Set the framebuffer memory to a colour

        :param color: colour value or name of colour to use"""
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
        color: color_t | str,
        lineSize: int = 1,
    ) -> None:
        """Draw a rectangle in the framebuffer memory

        :param left: top left x coordinate
        :param top: top left y coordinate
        :param right: bottom right x coordinate
        :param bottom: bottom right y coordinate
        :param color: colour value or name of colour to use for the lines
        :param lineSize: size of lines to draw"""
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
        """Draw an image into the framebufffer memory

        :param left: x coordinate
        :param top: y coordinate
        :param image: Image to draw"""
        width = image.width
        height = image.height

        assert 0 <= left < cls.width(), f"left of {left} is invalid"
        assert 0 <= top < cls.height(), f"top of {top} is invalid"
        assert 0 < width <= cls.width() - left, f"width of {width} is invalid"
        assert 0 < height <= cls.height() - top, f"height of {height} is invalid"

        if image.mode != IMAGE_MODE:
            image = image.convert(IMAGE_MODE)

        data = (color_t * (image.width * image.height)).from_buffer_copy(
            image.tobytes()
        )
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
        color: color_t | str = "black",
        fontSize: int = DEFAULT_FONT_SIZE,
        rotation: float = 0,
    ):
        """Draw text on the framebuffer memory

        :param left: left coordinate
        :param top: right coordinate
        :param width: width of area to draw text to
        :param height: height of area to draw text to
        :param text: text to draw
        :param color: color value or name of color to use
        :param fontSize: Size of font to use
        :param rotation: Rotation to apply to the text"""
        image = cls.to_image(left, top, width, height)
        if isinstance(color, str):
            color = ImageColor.getcolor(color, image.mode)

        else:
            # TODO - handle when IMAGE_MODE has more bands
            color = color.value

        d = ImageDraw.Draw(image)
        d.fontmode = "L"
        d.text(
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
        color: color_t | str = "black",
        fontSize: int = DEFAULT_FONT_SIZE,
        align: str = "left",
        rotation: float = 0,
    ):
        """Draw multiline text on the framebuffer memory

        :param left: left coordinate
        :param top: right coordinate
        :param width: width of area to draw text to
        :param height: height of area to draw text to
        :param text: text to draw
        :param color: color value or name of color to use
        :param fontSize: Size of font to use
        :param align: text align
        :param rotation: Rotation to apply to the text"""
        image = cls.to_image(left, top, width, height)
        if isinstance(color, str):
            color = ImageColor.getcolor(color, image.mode)

        else:
            # TODO - handle when IMAGE_MODE has more bands
            color = color.value

        d = ImageDraw.Draw(image)
        d.fontmode = "L"
        d.multiline_text(
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
    ) -> Image.Image:
        """Get an image of the framebuffer memory

        :param left: x coordinate
        :param top: y coordinate
        :param width: width, defaults to entire width
        :param height: height, defaults to entire height"""
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
    def getcolor(name_or_hex: str) -> color_t:
        """Get the value for a colour name or hex

        :name_or_hex: colour name of hex
        :return: colour value"""
        return getrgb(name_or_hex)

    @classmethod
    def __getitem__(cls, key: int | slice | tuple[int, int]) -> color_t | list[color_t]:
        """Get data from the framebuffer memory

        :param key: byte offset, slice, or coordinate
        :return: colour value or list of colour values"""
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
        value: color_t | str | Iterable[color_t] | Iterable[str],
    ) -> None:
        """Set framebuffer memory

        :param key: byte offset, slice, or coordinate
        :param value: colour value, name of colour, list of colour values, or list of colour names
        """
        f = _ensure_fb()
        if isinstance(key, tuple):
            assert isinstance(value, color_t) or isinstance(value, str)
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
            assert isinstance(value, color_t) or isinstance(value, str)
            y = int(key / cls.width())
            f["data"][cls.get_offset(key - y, y)] = value

        else:
            raise NotImplementedError()

    @classmethod
    def __iter__(cls) -> iter:
        """Iterate through the framebuffer memory"""
        return iter(_ensure_fb()["data"])

    @classmethod
    def __len__(cls) -> int:
        """Get the size of the framebuffer memory"""
        return cls.width() * cls.height()

    @classmethod
    def __contains__(cls, color: color_t | str | int) -> bool:
        """Check to see if a colour is present in the framebuffer memory

        :param color: colour value or name of colour
        :return: if the framebuffer contains the colour"""
        if isinstance(color, str):
            color = cls.getcolor(color)

        if isinstance(color, color_t):
            color = color.value

        for y in range(0, cls.height()):
            if color in cls.get_row(0, y, cls.width()):
                return True

        return False

    @classmethod
    def draw_line(
        cls, x1: int, y1: int, x2: int, y2: int, color: color_t | str
    ) -> None:
        """Draw a line between two points in the framebuffer memory

        :param x1: starting x coordinate
        :param y1: starting y coordinate
        :param x2: ending x coordinate
        :param y2: ending y coordinate
        :param color: colour value or name of colour"""
        for x, y in bresenham(x1, y1, x2, y2):
            cls.set_pixel(x, y, color)
