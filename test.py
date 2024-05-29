import sys

from io import SEEK_END

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

print(f"Device Type: {deviceType}")
print(f"FrameBuffer path: {framebuffer_path()}")
print(f"Size: {framebuffer_size()}")
print(f"rm2fb: {use_rm2fb()}")
print(f"Pixel Size: {framebuffer_pixel_size()}")
posY = posX = 0
width = height = 500
white = 0xFFFF
black = 0x0000
with mmap_framebuffer() as mm:
    for y in range(posY, height):
        for x in range(posX, width):
            set_pixel(mm, x, y, white)

    marker = 1
    update(posX, posY, width, height, WaveformMode.HighQualityGrayscale, marker)
    wait(marker)


if FAILED:
    sys.exit(1)
