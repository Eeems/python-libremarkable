import os
import sys

from mmap import mmap
from mmap import MAP_SHARED
from mmap import MAP_POPULATE
from mmap import PROT_READ
from mmap import PROT_WRITE
from mmap import ACCESS_DEFAULT

from ctypes import sizeof

from contextlib import contextmanager

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
from ._mxcfb import stride as mxcfb_stride
from ._mxcfb import UPDATE_MODE_PARTIAL
from ._mxcfb import UPDATE_MODE_FULL
from ._mxcfb import TEMP_USE_REMARKABLE_DRAW

from ._rm2fb import send as rm2fb_update
from ._rm2fb import wait as rm2fb_wait
from ._rm2fb import width as rm2fb_width
from ._rm2fb import height as rm2fb_height
from ._rm2fb import pixel_size as rm2fb_pixel_size
from ._rm2fb import stride as rm2fb_stride
from ._rm2fb import mxcfb_update_data
from ._rm2fb import wait_sem_data


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


def framebuffer_stride() -> int:
    return rm2fb_stride() if use_rm2fb() else mxcfb_stride()


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
        _fb = {
            "f": f,
            "mm": mm,
            "data": (c_t * int(size / sizeof(c_t))).from_buffer(mm),
        }

    yield _fb["data"]


def close_mmap_framebuffer():
    global _fb
    if _fb is not None:
        del _fb["data"]
        _fb["data"] = None
        _fb["mm"].close()
        _fb["f"].close()
        _fb = None


def update(
    x: int,
    y: int,
    width: int,
    height: int,
    waveform: WaveformMode,
    marker: int = 0,
    partial=True,
    sync=False,
) -> None:
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
    if wait:
        wait(marker)


def update_full(waveform: WaveformMode, marker: int = 0, sync=False):
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
    return y * framebuffer_stride()


def get_offset(x: int, y: int) -> int:
    assert 0 <= x <= framebuffer_width(), f"{x} not within bounds"
    assert 0 <= y <= framebuffer_height(), f"{y} not within bounds"
    return get_row_offset(y) + x


def _ensure_fb():
    global _fb
    if _fb is None:
        mmap_framebuffer().__enter__()

    return _fb


def set_pixel(x: int, y: int, color: c_t) -> None:
    _ensure_fb()["data"][get_offset(x, y)] = color


def set_row(x: int, y: int, width: int, color: c_t) -> None:
    assert width > 0
    assert x + width <= framebuffer_width()
    data = (c_t * width).from_buffer(bytearray(color) * width)
    _ensure_fb()["data"][get_offset(x, y) : get_offset(x + width, y)] = data


def set_col(x: int, y: int, height: int, color: c_t) -> None:
    assert height
    assert x + height <= framebuffer_height()
    for i in range(y, y + height):
        set_pixel(x, i, color)


def set_rect(left: int, top: int, width: int, height: int, color: c_t) -> None:
    for y in range(top, top + height):
        set_row(left, y, width, color)
