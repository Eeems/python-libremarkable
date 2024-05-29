import os

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
from ._rm2fb import send as rm2fb_send
from ._rm2fb import xochitl_data
from ._rm2fb import wait_sem_data


# As these may change at runtime, they are methods instead of stored at startup
def use_rm2fb() -> bool:
    return current == DeviceType.RM2 and os.path.exists("/dev/shm/swtfb.01")


def framebuffer_path():
    return "/dev/shm/swtfb.01" if use_rm2fb() else "/dev/fb0"


def open_framebuffer():
    return open(framebuffer_path(), "r+b")


def framebuffer_size():
    size = os.path.getsize(framebuffer_path()) if use_rm2fb() else getsize()
    assert size, "Framebuffer size is invalid"
    return size


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

    data = xochitl_data()
    data.x1 = x
    data.y1 = y
    data.x2 = x + width
    data.y2 = y + height
    data.waveform = waveform
    rm2fb_send(data)


def wait(marker: int) -> None:
    if use_rm2fb():
        mxcfb_wait(marker)
        return

    data = wait_sem_data()
    data.smem_name = f"/rm2fb.wait.{os.getpid()}"
    rm2fb_send(data)
