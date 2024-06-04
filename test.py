# nuitka-project: --enable-plugin=pylint-warnings
# nuitka-project: --enable-plugin=upx
# nuitka-project: --warn-implicit-exceptions
# nuitka-project: --onefile
# nuitka-project: --lto=yes

import sys
import time

from ctypes import sizeof

from contextlib import contextmanager

from PIL import Image
from PIL import ImageColor

from libremarkable import deviceType
from libremarkable import FrameBuffer as fb

from libremarkable._mxcfb import MXCFB_SEND_UPDATE

from libremarkable._framebuffer import WaveformMode

from libremarkable._color import c_t
from libremarkable._color import rgb565_to_rgb888
from libremarkable._color import rgb888_to_rgb565


FAILED = False


@contextmanager
def performance_log(msg: str = ""):
    start = time.perf_counter_ns()
    yield
    end = time.perf_counter_ns()
    print(f"{msg}: {(end - start) / 1000000}ms")


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


assertv("WHITE", fb.getcolor("white").value, 0xFFFF)
assertv("BLACK", fb.getcolor("black").value, 0x0000)
color888 = ImageColor.getrgb("white")
assertv("rgb565_to_rgb888(white)", rgb565_to_rgb888(0xFFFF), color888)
assertv("rgb888_to_rgb565(white)", rgb888_to_rgb565(*color888), 0xFFFF)
color888 = ImageColor.getrgb("black")
assertv("rgb565_to_rgb888(black)", rgb565_to_rgb888(0x0000), color888)
assertv("rgb888_to_rgb565(black)", rgb888_to_rgb565(*color888), 0x0000)
assertv("MXCFB_SEND_UPDATE", MXCFB_SEND_UPDATE, 0x4048462E)
assertv("pixel_size", fb.pixel_size(), sizeof(c_t))
assertv("get_offset", fb.get_offset(0, 0), 0)
asserti("get_pixel", fb.get_pixel(0, 0), int)

print(f"Device Type: {deviceType}")
print(f"FrameBuffer path: {fb.path()}")
print(f"Size: {fb.size()}")
print(f"Width: {fb.width()}")
print(f"Height: {fb.height()}")


with performance_log("Init to white"):
    fb.set_color("white")

with performance_log("Screen Update"):
    fb.update_full(WaveformMode.HighQualityGrayscale, sync=True)

with performance_log("Total"):
    with performance_log("Black Rectangle"):
        fb.set_rect(10, 10, 500, 500, "black")

    with performance_log("Border"):
        fb.draw_rect(6, 6, 514, 514, "black", lineSize=3)

    with performance_log("Screen Update"):
        fb.update(0, 0, 520, 520, WaveformMode.Mono)

    with performance_log("Checkboard background"):
        fb.set_rect(210, 210, 100, 100, "white")

    with performance_log("Checkboard dots"):
        for y in range(210, 310, 2):
            for x in range(210, 310, 2):
                fb.set_pixel(x, y, "black")

    with performance_log("Screen Update"):
        fb.update(210, 210, 310, 310, WaveformMode.Mono)

    with performance_log("Draw text"):
        fb.draw_text(800, 800, 100, 100, "Hello World!")

    with performance_log("Screen Update"):
        fb.update(800, 800, 100, 100, WaveformMode.HighQualityGrayscale)

with performance_log("Save text from framebuffer"):
    image = fb.to_image(800, 800, 100, 100)
    image.save("/tmp/py.text.png")

with performance_log("Save entire framebuffer"):
    image = fb.to_image()
    image.save("/tmp/py.fb.png")

image = Image.open("/tmp/py.fb.png")
with performance_log("Replace framebuffer with contents of image"):
    fb.draw_image(0, 0, image)

fb.update_full(WaveformMode.HighQualityGrayscale)
fb.release()

if FAILED:
    sys.exit(1)
