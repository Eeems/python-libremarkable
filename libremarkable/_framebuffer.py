import os

from mmap import mmap
from contextlib import contextmanager

from ._device import DeviceType


# As these may change at runtime, they are methods instead of stored at startup
def use_rm2fb() -> bool:
    return DeviceType.current() == DeviceType.RM2 and os.path.exists(
        "/dev/shm/swtfb.01"
    )


def framebuffer_path():
    return "/dev/shm/swtfb.01" if use_rm2fb() else "/dev/fb0"


def open_framebuffer():
    return open(framebuffer_path(), "r+b")


@contextmanager
def mmap_framebuffer():
    with open_framebuffer() as f:
        with mmap(f.fileno(), 0) as mm:
            yield mm
