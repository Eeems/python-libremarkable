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
from ._mxcfb import pixel_size as mxcfb_pixel_size
from ._mxcfb import UPDATE_MODE_PARTIAL
from ._mxcfb import UPDATE_MODE_FULL
from ._mxcfb import TEMP_USE_REMARKABLE_DRAW

from ._rm2fb import send as rm2fb_update
from ._rm2fb import wait as rm2fb_wait
from ._rm2fb import width as rm2fb_width
from ._rm2fb import pixel_size as rm2fb_pixel_size
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


def framebuffer_pixel_size() -> int:
    return rm2fb_pixel_size() if use_rm2fb() else mxcfb_pixel_size()


def framebuffer_stride() -> int:
    return framebuffer_width() * framebuffer_pixel_size()


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
            "view": memoryview(mm),
        }

    yield _fb["data"]


def close_mmap_framebuffer():
    global _fb
    if _fb is not None:
        del _fb["data"]
        _fb["data"] = None
        _fb["view"].release()
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


def wait(marker: int) -> None:
    rm2fb_wait(marker) if use_rm2fb() else mxcfb_wait(marker)


def get_address(x: int, y: int) -> int:
    # For use with memoryview
    return y * framebuffer_stride() + (x * framebuffer_pixel_size())


def get_offset(x: int, y: int) -> int:
    # For use with c_ushort array
    return y * framebuffer_width() + x


def set_pixel(x: int, y: int, color: c_t) -> None:
    global _fb
    if _fb is None:
        mmap_framebuffer().__enter__()

    _fb["data"][get_offset(x, y)] = color


def set_row(x: int, y: int, width: int, color: c_t) -> None:
    global _fb
    if _fb is None:
        mmap_framebuffer().__enter__()

    _fb["view"][get_address(x, y) : get_address(x + width, y)] = bytes(color) * width


def set_col(x: int, y: int, height: int, color: c_t) -> None:
    global _fb
    if _fb is None:
        mmap_framebuffer().__enter__()

    for i in range(y, y + height):
        set_pixel(x, i, color)
