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

from ._color import c_t

from ._device import DeviceType
from ._device import current

from ._mxcfb import getsize
from ._mxcfb import WaveformMode
from ._mxcfb import update as mxcfb_update
from ._mxcfb import wait as mxcfb_wait
from ._mxcfb import width as mxcfb_width
from ._mxcfb import height as mxcfb_height
from ._mxcfb import pixel_size as mxcfb_pixel_size
from ._mxcfb import virtual_width as mxcfb_virtual_width
from ._mxcfb import virtual_height as mxcfb_virtual_height
from ._mxcfb import x_offset as mxcfb_x_offset
from ._mxcfb import y_offset as mxcfb_y_offset
from ._mxcfb import UPDATE_MODE_PARTIAL
from ._mxcfb import UPDATE_MODE_FULL

# from ._mxcfb import TEMP_USE_REMARKABLE_DRAW

from ._rm2fb import send as rm2fb_update
from ._rm2fb import wait as rm2fb_wait
from ._rm2fb import width as rm2fb_width
from ._rm2fb import height as rm2fb_height
from ._rm2fb import pixel_size as rm2fb_pixel_size
from ._rm2fb import virtual_width as rm2fb_virtual_width
from ._rm2fb import virtual_height as rm2fb_virtual_height
from ._rm2fb import x_offset as rm2fb_x_offset
from ._rm2fb import y_offset as rm2fb_y_offset
from ._rm2fb import mxcfb_update_data

IMAGE_MODE = "I;16"


# As these may change at runtime, they are methods instead of stored at startup
def use_rm2fb() -> bool:
    if current == DeviceType.RM1:
        return False

    if current == DeviceType.RM2:
        assert os.path.exists("/dev/shm/swtfb.01")
        return True

    return os.path.exists("/dev/shm/swtfb.01")


def framebuffer_path():
    return "/dev/shm/swtfb.01" if use_rm2fb() else "/dev/fb0"


def open_framebuffer():
    return open(framebuffer_path(), "r+b")


def framebuffer_size():
    size = os.path.getsize(framebuffer_path()) if use_rm2fb() else getsize()
    assert size, "Framebuffer size is invalid"
    return size


def framebuffer_width() -> int:
    return rm2fb_width() if use_rm2fb() else mxcfb_width()


def framebuffer_height() -> int:
    return rm2fb_height() if use_rm2fb() else mxcfb_height()


def framebuffer_pixel_size() -> int:
    return rm2fb_pixel_size() if use_rm2fb() else mxcfb_pixel_size()


def framebuffer_virtual_width() -> int:
    return rm2fb_virtual_width() if use_rm2fb() else mxcfb_virtual_width()


def framebuffer_virtual_height() -> int:
    return rm2fb_virtual_height() if use_rm2fb() else mxcfb_virtual_height()


def framebuffer_x_offset() -> int:
    return rm2fb_x_offset() if use_rm2fb() else mxcfb_x_offset()


def framebuffer_y_offset() -> int:
    return rm2fb_y_offset() if use_rm2fb() else mxcfb_y_offset()


_fb = None


@contextmanager
def mmap_framebuffer():
    global _fb
    if _fb is None:
        f = open_framebuffer()
        size = framebuffer_size()
        mm = mmap(
            f.fileno(),
            size,
            flags=MAP_SHARED | MAP_POPULATE,
            prot=PROT_READ | PROT_WRITE,
            access=ACCESS_DEFAULT,
        )
        offset = get_offset(0, 0)
        _fb = {
            "f": f,
            "mm": mm,
            "data": (c_t * int(size / sizeof(c_t))).from_buffer(mm),
            "offset": offset,
            "image": Image.frombuffer(
                IMAGE_MODE,
                (framebuffer_virtual_width(), framebuffer_virtual_height()),
                mm,
            ),
        }

    yield _fb["data"]


def close_mmap_framebuffer():
    global _fb
    if _fb is not None:
        _fb["image"].close()
        del _fb["data"]
        _fb["data"] = None
        _fb["mm"].close()
        _fb["f"].close()
        _fb = None


_marker = 0


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
    rm2fb_update(data) if use_rm2fb() else mxcfb_update(data)
    if sync:
        wait(data.update_marker)

    return data.update_marker


def update_full(waveform: WaveformMode, marker: int = None, sync=False):
    update(
        0,
        0,
        framebuffer_width(),
        framebuffer_height(),
        waveform,
        marker,
        partial=False,
        sync=sync,
    )


def wait(marker: int) -> None:
    rm2fb_wait(marker) if use_rm2fb() else mxcfb_wait(marker)


def get_row_offset(y: int) -> int:
    assert 0 <= y <= framebuffer_height()
    return (y + framebuffer_y_offset()) * framebuffer_virtual_width()


def get_offset(x: int, y: int) -> int:
    assert 0 <= x <= framebuffer_width(), f"{x} not within bounds"
    assert 0 <= y <= framebuffer_height(), f"{y} not within bounds"
    return get_row_offset(y) + x + framebuffer_x_offset()


def _ensure_fb():
    global _fb
    if _fb is None:
        mmap_framebuffer().__enter__()

    return _fb


def set_pixel(x: int, y: int, color: c_t) -> None:
    _ensure_fb()["data"][get_offset(x, y)] = color


def get_pixel(x: int, y: int) -> int:
    return _ensure_fb()["data"][get_offset(x, y)]


def _set_line_to_data(x: int, y: int, data) -> None:
    width = len(data)
    assert x + width <= framebuffer_width()
    _ensure_fb()["data"][get_offset(x, y) : get_offset(x + width, y)] = data


def set_row(x: int, y: int, width: int, color: c_t) -> None:
    assert width > 0
    assert x + width <= framebuffer_width()
    data = (c_t * width).from_buffer(bytearray(color) * width)
    _set_line_to_data(x, y, data)


def get_row(x: int, y: int, width: int) -> tuple[int]:
    return _ensure_fb()["data"][get_offset(x, y) : get_offset(x + width, y)]


def set_col(x: int, y: int, height: int, color: c_t) -> None:
    assert height
    assert x + height <= framebuffer_height()
    for i in range(y, y + height):
        set_pixel(x, i, color)


def set_rect(left: int, top: int, width: int, height: int, color: c_t) -> None:
    assert 0 <= left < framebuffer_width(), f"left of {left} is invalid"
    assert 0 <= top < framebuffer_height(), f"top of {top} is invalid"
    assert 0 < width <= framebuffer_width() - left, f"width of {width} is invalid"
    assert 0 < height <= framebuffer_height() - top, f"height of {height} is invalid"

    data = (c_t * width).from_buffer(bytearray(color) * width)
    for y in range(top, top + height):
        _set_line_to_data(left, y, data)


def set_color(color: c_t) -> None:
    data = _ensure_fb()["data"]
    size = len(data)
    data[0:size] = (c_t * size).from_buffer(bytearray(color) * size)


def draw_rect(
    left: int, top: int, right: int, bottom: int, color: c_t, lineSize: int = 1
) -> None:
    set_rect(left, top, right - left, lineSize, color)  # Top line
    set_rect(left, bottom - lineSize, right - left, lineSize, color)  # Bottom line
    set_rect(left, top, lineSize, bottom - top, color)  # Left line
    set_rect(right - lineSize, top, lineSize, bottom - top, color)  # Right line


def draw_image(left: int, top: int, image: Image) -> None:
    width = image.width
    height = image.height

    assert 0 <= left < framebuffer_width(), f"left of {left} is invalid"
    assert 0 <= top < framebuffer_height(), f"top of {top} is invalid"
    assert 0 < width <= framebuffer_width() - left, f"width of {width} is invalid"
    assert 0 < height <= framebuffer_height() - top, f"height of {height} is invalid"

    if image.mode != IMAGE_MODE:
        image = image.convert(IMAGE_MODE)

    data = (c_t * (image.width * image.height)).from_buffer_copy(image.tobytes())
    for y in range(0, image.height):
        _set_line_to_data(left, top + y, data[y * width : y * width + width])


def draw_text(
    left: int,
    top: int,
    width: int,
    height: int,
    text: str,
    color: str = "black",
    fontSize: int = 16,
):
    image = to_image(left, top, width, height)
    ImageDraw.Draw(image).text(
        (0, 0),
        text,
        ImageColor.getcolor(color, image.mode),
        font=ImageFont.load_default(size=fontSize),
    )
    draw_image(left, top, image)


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
    image = to_image(left, top, width, height)
    ImageDraw.Draw(image).multiline_text(
        (0, 0),
        text,
        ImageColor.getcolor(color, image.mode),
        font=ImageFont.load_default(size=fontSize),
    )
    draw_image(left, top, image)


def to_image(
    left: int = 0, top: int = 0, width: int = None, height: int = None
) -> Image:
    if width is None:
        width = framebuffer_width()

    if height is None:
        height = framebuffer_height()

    assert 0 <= left < framebuffer_width(), f"left of {left} is invalid"
    assert 0 <= top < framebuffer_height(), f"top of {top} is invalid"
    assert 0 < width <= framebuffer_width() - left, f"width of {width} is invalid"
    assert 0 < height <= framebuffer_height() - top, f"height of {height} is invalid"

    left += framebuffer_x_offset()
    top += framebuffer_y_offset()
    return _ensure_fb()["image"].crop((left, top, left + width, top + height))
