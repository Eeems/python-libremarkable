# nuitka-project: --enable-plugin=pylint-warnings
# nuitka-project: --enable-plugin=upx
# nuitka-project: --warn-implicit-exceptions
# nuitka-project: --onefile
# nuitka-project: --lto=yes

import sys
import time

from io import SEEK_END

from ctypes import sizeof

from contextlib import contextmanager

from libremarkable._mxcfb import MXCFB_SEND_UPDATE
from libremarkable._framebuffer import mmap_framebuffer
from libremarkable._framebuffer import close_mmap_framebuffer
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
from libremarkable._color import c_t
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
assertv("pixel_size", framebuffer_pixel_size(), sizeof(c_t))

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


posY = posX = 0
width = height = 500
with performance_log("Pixel Painting"):
    for y in range(posY, height):
        for x in range(posX, width):
            set_pixel(x, y, WHITE)

marker = 1
with performance_log("Send Update"):
    update(posX, posY, width, height, WaveformMode.HighQualityGrayscale, marker)

with performance_log("Wait on screen"):
    wait(marker)

marker += 1

close_mmap_framebuffer()

if FAILED:
    sys.exit(1)
