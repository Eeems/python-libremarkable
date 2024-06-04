import os

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

    @staticmethod
    def open():
        return open(FrameBuffer.path(), "r+b")

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

    @staticmethod
    @contextmanager
    def mmap():
        global _fb
        if _fb is None:
            f = FrameBuffer.open()
            size = FrameBuffer.size()
            mm = mmap(
                f.fileno(),
                size,
                flags=MAP_SHARED | MAP_POPULATE,
                prot=PROT_READ | PROT_WRITE,
                access=ACCESS_DEFAULT,
            )
            offset = FrameBuffer.get_offset(0, 0)
            _fb = {
                "f": f,
                "mm": mm,
                "data": (c_t * int(size / sizeof(c_t))).from_buffer(mm),
                "offset": offset,
                "image": Image.frombuffer(
                    IMAGE_MODE,
                    (FrameBuffer.virtual_width(), FrameBuffer.virtual_height()),
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

    @staticmethod
    def update(
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
            FrameBuffer.wait(data.update_marker)

        return data.update_marker

    @staticmethod
    def update_full(waveform: WaveformMode, marker: int = None, sync=False):
        FrameBuffer.update(
            0,
            0,
            FrameBuffer.width(),
            FrameBuffer.height(),
            waveform,
            marker,
            partial=False,
            sync=sync,
        )

    @staticmethod
    def wait(marker: int) -> None:
        implementation().wait(marker)

    @staticmethod
    def get_row_offset(y: int) -> int:
        assert 0 <= y <= FrameBuffer.height()
        return (y + FrameBuffer.y_offset()) * FrameBuffer.virtual_width()

    @staticmethod
    def get_offset(x: int, y: int) -> int:
        assert 0 <= x <= FrameBuffer.width(), f"{x} not within bounds"
        assert 0 <= y <= FrameBuffer.height(), f"{y} not within bounds"
        return FrameBuffer.get_row_offset(y) + x + FrameBuffer.x_offset()

    @staticmethod
    def set_pixel(x: int, y: int, color: c_t) -> None:
        _ensure_fb()["data"][FrameBuffer.get_offset(x, y)] = color

    @staticmethod
    def get_pixel(x: int, y: int) -> int:
        return _ensure_fb()["data"][FrameBuffer.get_offset(x, y)]

    @staticmethod
    def set_row(x: int, y: int, width: int, color: c_t) -> None:
        assert width > 0
        assert x + width <= FrameBuffer.width()
        data = (c_t * width).from_buffer(bytearray(color) * width)
        _set_line_to_data(x, y, data)

    @staticmethod
    def get_row(x: int, y: int, width: int) -> tuple[int]:
        return _ensure_fb()["data"][
            FrameBuffer.get_offset(x, y) : FrameBuffer.get_offset(x + width, y)
        ]

    @staticmethod
    def set_col(x: int, y: int, height: int, color: c_t) -> None:
        assert height
        assert x + height <= height()
        for i in range(y, y + height):
            FrameBuffer.set_pixel(x, i, color)

    @staticmethod
    def set_rect(left: int, top: int, width: int, height: int, color: c_t) -> None:
        assert 0 <= left < FrameBuffer.width(), f"left of {left} is invalid"
        assert 0 <= top < FrameBuffer.height(), f"top of {top} is invalid"
        assert 0 < width <= FrameBuffer.width() - left, f"width of {width} is invalid"
        assert (
            0 < height <= FrameBuffer.height() - top
        ), f"height of {height} is invalid"

        data = (c_t * width).from_buffer(bytearray(color) * width)
        for y in range(top, top + height):
            _set_line_to_data(left, y, data)

    @staticmethod
    def set_color(color: c_t) -> None:
        FrameBuffer.set_rect(0, 0, FrameBuffer.width(), FrameBuffer.height(), color)

    @staticmethod
    def draw_rect(
        left: int, top: int, right: int, bottom: int, color: c_t, lineSize: int = 1
    ) -> None:
        FrameBuffer.set_rect(left, top, right - left, lineSize, color)  # Top line
        FrameBuffer.set_rect(
            left, bottom - lineSize, right - left, lineSize, color
        )  # Bottom line
        FrameBuffer.set_rect(left, top, lineSize, bottom - top, color)  # Left line
        FrameBuffer.set_rect(
            right - lineSize, top, lineSize, bottom - top, color
        )  # Right line

    @staticmethod
    def draw_image(left: int, top: int, image: Image) -> None:
        width = image.width
        height = image.height

        assert 0 <= left < FrameBuffer.width(), f"left of {left} is invalid"
        assert 0 <= top < FrameBuffer.height(), f"top of {top} is invalid"
        assert 0 < width <= FrameBuffer.width() - left, f"width of {width} is invalid"
        assert (
            0 < height <= FrameBuffer.height() - top
        ), f"height of {height} is invalid"

        if image.mode != IMAGE_MODE:
            image = image.convert(IMAGE_MODE)

        data = (c_t * (image.width * image.height)).from_buffer_copy(image.tobytes())
        for y in range(0, image.height):
            _set_line_to_data(left, top + y, data[y * width : y * width + width])

    @staticmethod
    def draw_text(
        left: int,
        top: int,
        width: int,
        height: int,
        text: str,
        color: str = "black",
        fontSize: int = 16,
    ):
        image = FrameBuffer.to_image(left, top, width, height)
        ImageDraw.Draw(image).text(
            (0, 0),
            text,
            ImageColor.getcolor(color, image.mode),
            font=ImageFont.load_default(size=fontSize),
        )
        FrameBuffer.draw_image(left, top, image)

    @staticmethod
    def draw_multiline_text(
        left: int,
        top: int,
        width: int,
        height: int,
        text: str,
        color: str = "black",
        fontSize: int = 16,
        align: str = "left",
    ):
        image = FrameBuffer.to_image(left, top, width, height)
        ImageDraw.Draw(image).multiline_text(
            (0, 0),
            text,
            ImageColor.getcolor(color, image.mode),
            font=ImageFont.load_default(size=fontSize),
        )
        FrameBuffer.draw_image(left, top, image)

    @staticmethod
    def to_image(
        left: int = 0, top: int = 0, width: int = None, height: int = None
    ) -> Image:
        if width is None:
            width = FrameBuffer.width()

        if height is None:
            height = FrameBuffer.height()

        assert 0 <= left < FrameBuffer.width(), f"left of {left} is invalid"
        assert 0 <= top < FrameBuffer.height(), f"top of {top} is invalid"
        assert 0 < width <= FrameBuffer.width() - left, f"width of {width} is invalid"
        assert (
            0 < height <= FrameBuffer.height() - top
        ), f"height of {height} is invalid"

        left += FrameBuffer.x_offset()
        top += FrameBuffer.y_offset()
        return _ensure_fb()["image"].crop((left, top, left + width, top + height))
