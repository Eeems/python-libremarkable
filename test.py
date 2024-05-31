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

from PIL import ImageColor

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
from libremarkable._framebuffer import draw_rect
from libremarkable._framebuffer import draw_text
from libremarkable._framebuffer import WaveformMode
from libremarkable._framebuffer import use_rm2fb
from libremarkable._framebuffer import get_offset
from libremarkable._framebuffer import to_image
from libremarkable._framebuffer import get_pixel
from libremarkable._framebuffer import get_row
from libremarkable._color import WHITE
from libremarkable._color import BLACK
from libremarkable._color import c_t
from libremarkable._color import rgb565_to_rgb888
from libremarkable._color import rgb888_to_rgb565
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


def asserti(name, value, expected):
    global FAILED
    print(f"Testing {name}: ", end="")
    if isinstance(value, expected):
        print("pass")
        return

    FAILED = True
    print("fail")
    print(f"  {type(value).__name__} not instance of {expected.__name__}")


assertv("WHITE", WHITE.value, 0xFFFF)
assertv("BLACK", BLACK.value, 0x0000)
color888 = ImageColor.getrgb("white")
assertv("rgb565_to_rgb888(white)", rgb565_to_rgb888(0xFFFF), color888)
assertv("rgb888_to_rgb565(white)", rgb888_to_rgb565(*color888), 0xFFFF)
color888 = ImageColor.getrgb("black")
assertv("rgb565_to_rgb888(black)", rgb565_to_rgb888(0x0000), color888)
assertv("rgb888_to_rgb565(black)", rgb888_to_rgb565(*color888), 0x0000)
assertv("MXCFB_SEND_UPDATE", MXCFB_SEND_UPDATE, 0x4048462E)
assertv("pixel_size", framebuffer_pixel_size(), sizeof(c_t))
assertv("get_offset", get_offset(0, 0), 0)
asserti("get_pixel", get_pixel(0, 0), int)

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
        set_rect(10, 10, 500, 500, BLACK)

    with performance_log("Border"):
        draw_rect(6, 6, 514, 514, BLACK, lineSize=3)

    with performance_log("Screen Update"):
        update(0, 0, 520, 520, WaveformMode.Mono, marker)
        marker += 1

    with performance_log("Checkboard background"):
        set_rect(210, 210, 100, 100, WHITE)

    with performance_log("Checkboard dots"):
        for y in range(210, 310, 2):
            for x in range(210, 310, 2):
                set_pixel(x, y, BLACK)

    with performance_log("Screen Update"):
        update(210, 210, 310, 310, WaveformMode.Mono, marker)
        marker += 1

    with performance_log("Draw text"):
        draw_text(800, 800, 100, 100, "Hello World!")

    with performance_log("Screen Update"):
        update(800, 800, 100, 100, WaveformMode.HighQualityGrayscale, marker)
        marker += 1

with performance_log("Save framebuffer"):
    to_image().save("/home/root/py.fb.png")

close_mmap_framebuffer()

if FAILED:
    sys.exit(1)
