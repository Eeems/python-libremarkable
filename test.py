import sys
import time

from io import SEEK_END

from ctypes import c_uint

from contextlib import contextmanager

from libremarkable._mxcfb import MXCFB_SEND_UPDATE
from libremarkable._framebuffer import mmap_framebuffer
from libremarkable._framebuffer import framebuffer_path
from libremarkable._framebuffer import framebuffer_size
from libremarkable._framebuffer import framebuffer_pixel_size
from libremarkable._framebuffer import update
from libremarkable._framebuffer import wait
from libremarkable._framebuffer import set_pixel
from libremarkable._framebuffer import WaveformMode
from libremarkable._framebuffer import use_rm2fb
from libremarkable._color import WHITE
from libremarkable._color import BLACK
from libremarkable import deviceType

FAILED = False


def assertv(name, value, expected):
    global FAILED
    print(f"Testing {name}: ", end="")
    if value == expected:
        print("pass")
        return

    FAILED = True
    print("fail")
    print(f"  {value} != {expected}")


assertv("MXCFB_SEND_UPDATE", MXCFB_SEND_UPDATE, 0x4048462E)
assertv("pixel_size", framebuffer_pixel_size(), 2)

print(f"Device Type: {deviceType}")
print(f"FrameBuffer path: {framebuffer_path()}")
print(f"Size: {framebuffer_size()}")
print(f"rm2fb: {use_rm2fb()}")


@contextmanager
def performance_log(msg: str = ""):
    start = time.perf_counter_ns()
    yield
    end = time.perf_counter_ns()
    print(f"{msg}: {(end - start) / 1000000}ms")


with mmap_framebuffer() as mm:
    posY = posX = 0
    width = height = 500
    with performance_log("Pixel Painting"):
        for y in range(posY, height):
            for x in range(posX, width):
                set_pixel(mm, x, y, WHITE)

    marker = 1
    with performance_log("Send Update"):
        update(posX, posY, width, height, WaveformMode.HighQualityGrayscale, marker)

    with performance_log("Wait on screen"):
        wait(marker)

    marker += 1

    del mm  # required to avoid a BufferError


if FAILED:
    sys.exit(1)
