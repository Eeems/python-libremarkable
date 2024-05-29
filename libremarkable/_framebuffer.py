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
