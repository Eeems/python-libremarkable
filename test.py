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
from libremarkable._framebuffer import framebuffer_pixel_size
from libremarkable._framebuffer import update
from libremarkable._framebuffer import wait
from libremarkable._framebuffer import set_pixel
from libremarkable._framebuffer import set_row
from libremarkable._framebuffer import set_col
from libremarkable._framebuffer import WaveformMode
from libremarkable._framebuffer import use_rm2fb
from libremarkable._framebuffer import get_address
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
assertv("get_address(0, 0)", get_address(0, 0), 0)

print(f"Device Type: {deviceType}")
print(f"FrameBuffer path: {framebuffer_path()}")
print(f"Size: {framebuffer_size()}")
print(f"rm2fb: {use_rm2fb()}")
print(f"Width: {framebuffer_width()}")


@contextmanager
def performance_log(msg: str = ""):
    start = time.perf_counter_ns()
    yield
    end = time.perf_counter_ns()
    print(f"{msg}: {(end - start) / 1000000}ms")


marker = 1
with performance_log("White Rectangle"):
    for y in range(0, 500):
        set_row(0, y, 500, WHITE)

with performance_log("Border"):
    set_row(0, 501, 500, BLACK)
    set_row(0, 502, 500, BLACK)
    set_row(0, 503, 500, BLACK)
    set_col(501, 0, 500, BLACK)
    set_col(502, 0, 500, BLACK)
    set_col(503, 0, 500, BLACK)

update(0, 0, 503, 503, WaveformMode.HighQualityGrayscale, marker)
wait(marker)
marker += 1
with performance_log("Checkboard"):
    for y in range(200, 300, 2):
        for x in range(200, 300, 2):
            set_pixel(x, y, BLACK)

update(200, 200, 300, 300, WaveformMode.Mono, marker)
wait(marker)
marker += 1

close_mmap_framebuffer()

if FAILED:
    sys.exit(1)
