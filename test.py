import sys

from io import SEEK_END

from libremarkable._mxcfb import MXCFB_SEND_UPDATE
from libremarkable._framebuffer import mmap_framebuffer
from libremarkable._framebuffer import framebuffer_path
from libremarkable._framebuffer import framebuffer_size
from libremarkable._framebuffer import update
from libremarkable._framebuffer import wait
from libremarkable._framebuffer import WaveformMode
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
with mmap_framebuffer() as f:
    pass

marker = 1
update(0, 0, 500, 500, WaveformMode.HighQualityGrayscale, marker)
wait(marker)

if FAILED:
    sys.exit(1)
