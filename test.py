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
from libremarkable._framebuffer import framebuffer_width
from libremarkable._framebuffer import framebuffer_height
from libremarkable._framebuffer import framebuffer_stride
from libremarkable._framebuffer import framebuffer_pixel_size
from libremarkable._framebuffer import update
from libremarkable._framebuffer import update_full
from libremarkable._framebuffer import set_pixel
from libremarkable._framebuffer import set_row
from libremarkable._framebuffer import set_col
from libremarkable._framebuffer import set_rect
from libremarkable._framebuffer import set_color
from libremarkable._framebuffer import WaveformMode
from libremarkable._framebuffer import use_rm2fb
from libremarkable._framebuffer import get_offset
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
assertv("get_offset(0, 0)", get_offset(0, 0), 0)

print(f"Device Type: {deviceType}")
print(f"FrameBuffer path: {framebuffer_path()}")
print(f"Size: {framebuffer_size()}")
print(f"Stride: {framebuffer_stride()}")
print(f"rm2fb: {use_rm2fb()}")
print(f"Width: {framebuffer_width()}")
print(f"Height: {framebuffer_height()}")


@contextmanager
def performance_log(msg: str = ""):
    start = time.perf_counter_ns()
    yield
    end = time.perf_counter_ns()
    print(f"{msg}: {(end - start) / 1000000}ms")


marker = 1
with performance_log("Init to white"):
    set_color(WHITE)

with performance_log("Screen Update"):
    update_full(WaveformMode.HighQualityGrayscale, marker, sync=True)
    marker += 1

with performance_log("Total"):
    with performance_log("Black Rectangle"):
        set_rect(0, 0, 500, 500, BLACK)
        set_pixel(500, 500, BLACK)

    with performance_log("Border"):
        set_rect(0, 501, 504, 3, BLACK)
        set_rect(501, 0, 3, 504, BLACK)

    with performance_log("Screen Update"):
        update(0, 0, 504, 504, WaveformMode.Mono, marker, sync=True)

    marker += 1
    with performance_log("Checkboard background"):
        set_rect(200, 200, 100, 100, WHITE)

    with performance_log("Checkboard dots"):
        for y in range(200, 300, 2):
            for x in range(200, 300, 2):
                set_pixel(x, y, BLACK)

    with performance_log("Screen Update"):
        update(200, 200, 300, 300, WaveformMode.Mono, marker, sync=True)

    marker += 1

close_mmap_framebuffer()

if FAILED:
    sys.exit(1)
