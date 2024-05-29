import os
import sys

from mmap import mmap
from mmap import MAP_SHARED
from mmap import PROT_READ
from mmap import PROT_WRITE
from mmap import ACCESS_DEFAULT

from contextlib import contextmanager

from ._device import DeviceType
from ._device import current
from ._mxcfb import getsize
from ._mxcfb import WaveformMode
from ._mxcfb import update as mxcfb_update
from ._mxcfb import wait as mxcfb_wait
from ._mxcfb import width as mxcfb_width
from ._rm2fb import send as rm2fb_send
from ._rm2fb import width as rm2fb_width
from ._rm2fb import mxcfb_update_data
from ._rm2fb import wait_sem_data


# As these may change at runtime, they are methods instead of stored at startup
def use_rm2fb() -> bool:
    if current == DeviceType.RM1:
        return False

    if current == DeviceType.UNKNOWN:
        return os.path.exists("/dev/shm/swtfb.01")

    if current == DeviceType.RM2:
        assert os.path.exists("/dev/shm/swtfb.01")
        return True


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


@contextmanager
def mmap_framebuffer():
    with open_framebuffer() as f:
        with mmap(
            f.fileno(),
            framebuffer_size(),
            flags=MAP_SHARED,
            prot=PROT_READ | PROT_WRITE,
            access=ACCESS_DEFAULT,
        ) as mm:
            yield mm


def update(
    x: int, y: int, width: int, height: int, waveform: WaveformMode, marker: int = 0
) -> None:
    if not use_rm2fb():
        mxcfb_update(x, y, width, height, waveform, marker)
        return

    data = mxcfb_update_data()
    data.update_region.left = x
    data.update_region.top = y
    data.update_region.width = width
    data.update_region.height = height
    data.waveform_mode = waveform
    data.update_marker = marker
    rm2fb_send(data)


def wait(marker: int) -> None:
    if not use_rm2fb():
        mxcfb_wait(marker)
        return

    data = wait_sem_data()
    data.smem_name = f"/rm2fb.wait.{os.getpid()}"
    rm2fb_send(data)


def set_pixel(mm: mmap, x: int, y: int, color: int) -> None:
    mm.seek(y * framebuffer_width() + x)
    mm.write(color.to_bytes(32, sys.byteorder))
