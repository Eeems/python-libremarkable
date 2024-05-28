import io
import sys

from libremarkable._mxcfb import MXCFB_SEND_UPDATE
from libremarkable._rm2fb import send as rm2fb_send
from libremarkable._rm2fb import xochitl_data
from libremarkable._rm2fb import WaveformMode
from libremarkable._framebuffer import mmap_framebuffer
from libremarkable._framebuffer import framebuffer_path
from libremarkable._device import DeviceType

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

rm2fb_send(xochitl_data(0, 0, 10, 10, WaveformMode.HighQualityGrayscale, 0))

print(f"Device Type: {DeviceType.current()}")
print(f"FrameBuffer path: {framebuffer_path()}")
with mmap_framebuffer() as f:
    f.seek(0, io.SEEK_END)
    print(f"Size: {f.tell()}")

if FAILED:
    sys.exit(1)
