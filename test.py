# nuitka-project: --enable-plugin=pylint-warnings
# nuitka-project: --enable-plugin=upx
# nuitka-project: --warn-implicit-exceptions
# nuitka-project: --onefile
# nuitka-project: --lto=yes

import sys
import difflib

from ctypes import sizeof

from PIL import ImageColor

from libremarkable import FrameBuffer as fb
from libremarkable import DeviceType
from libremarkable import deviceType

from libremarkable._mxcfb import MXCFB_SEND_UPDATE


from libremarkable._color import c_t
from libremarkable._color import rgb565_to_rgb888
from libremarkable._color import rgb888_to_rgb565

from libremarkable.geometry import Point
from libremarkable.geometry import Rect
from libremarkable.geometry import Region


FAILED = False


def assertv(name, value, expected):
    global FAILED
    print(f"Testing {name}: ", end="")
    if value == expected:
        print("pass")
        return

    FAILED = True
    print("fail")
    for diff in difflib.ndiff(str(expected).splitlines(), str(value).splitlines()):
        print(f"  {diff}")


def asserta(name, value, expected):
    global FAILED
    print(f"Testing {name}: ", end="")
    if value == expected:
        print("pass")
        return

    FAILED = True
    print("fail")
    for diff in difflib.ndiff(
        [str(x) for x in expected],
        [str(x) for x in value],
    ):
        print(f"  {diff}")


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
if deviceType != DeviceType.UNKNOWN:
    assertv("get_offset", fb.get_offset(0, 0), 0)
    asserti("get_pixel", fb.get_pixel(0, 0), int)
    assertv("pixel_size", fb.pixel_size(), sizeof(c_t))

a = Point(0, 0)
b = Point(10, 10)
assertv(f"{a} < {b}", a < b, True)
assertv(f"not {b} < {a}", b < a, False)
a = Point(10, 10)
b = Point(0, 0)
assertv(f"{a} > {b}", a > b, True)
assertv(f"not {b} > {a}", b > a, False)
a = Point(0, 0)
b = Point(0, 10)
assertv(f"{a} < {b}", a < b, True)
assertv(f"not {b} < {a}", b < a, False)
a = Point(0, 10)
b = Point(0, 0)
assertv(f"{a} > {b}", a > b, True)
assertv(f"not {b} > {a}", b > a, False)
a = Point(0, 0)
b = Point(10, 0)
assertv(f"{a} < {b}", a < b, True)
assertv(f"not {b} < {a}", b < a, False)
a = Point(10, 0)
b = Point(0, 0)
assertv(f"{a} > {b}", a > b, True)
assertv(f"not {b} > {a}", b > a, False)

x, y = Point(10, 10)

assertv("x, y = Point(10, 10)", (x, y), (10, 10))

a = Rect(0, 0, 1, 1)
b = Rect(0.5, 0.5, 1.5, 1.5)
assertv(f"{a} & {b}", a & b, Rect(0.5, 0.5, 1, 1))
asserta(
    f"{a} - {b}",
    list(a - b),
    [
        Rect(0, 0, 0.5, 0.5),
        Rect(0, 0.5, 0.5, 1),
        Rect(0.5, 0, 1, 0.5),
    ],
)

b = Rect(0.25, 0.25, 1.25, 0.75)
assertv(f"{a} & {b}", a & b, Rect(0.25, 0.25, 1, 0.75))
asserta(
    f"{a} - {b}",
    list(a - b),
    [
        Rect(0, 0, 0.25, 0.25),
        Rect(0, 0.25, 0.25, 0.75),
        Rect(0, 0.75, 0.25, 1),
        Rect(0.25, 0, 1, 0.25),
        Rect(0.25, 0.75, 1, 1),
    ],
)

b = Rect(0.25, 0.25, 0.75, 0.75)
assertv(f"{a} & {b}", a & b, Rect(0.25, 0.25, 0.75, 0.75))
asserta(
    f"{a} - {b}",
    list(a - b),
    [
        Rect(0, 0, 0.25, 0.25),
        Rect(0, 0.25, 0.25, 0.75),
        Rect(0, 0.75, 0.25, 1),
        Rect(0.25, 0, 0.75, 0.25),
        Rect(0.25, 0.75, 0.75, 1),
        Rect(0.75, 0, 1, 0.25),
        Rect(0.75, 0.25, 1, 0.75),
        Rect(0.75, 0.75, 1, 1),
    ],
)

b = Rect(5, 5, 10, 10)
assertv(f"{a} & {b}", a & b, None)
asserta(
    f"{a} - {b}",
    sorted(a - b),
    sorted(
        [
            Rect(0, 0, 1, 1),
        ]
    ),
)

b = Rect(-5, -5, 10, 10)
assertv(f"{a} & {b}", a & b, Rect(0, 0, 1, 1))
asserta(f"{a} - {b}", sorted(a - b), [])

a = Region()
b = Rect(0, 0, 1, 1)
asserta(
    f"{a} + {b}",
    sorted(a + b),
    [
        Rect(0, 0, 1, 1),
    ],
)

a = Region(Rect(5, 5, 10, 10))
b = Rect(5, 5, 10, 10)
asserta(f"{a} - {b}", sorted(a - b), [])

a = Region(Rect(5, 5, 10, 10))
b = Rect(5, 5, 20, 20)
asserta(
    f"{a} + {b}",
    sorted(a + b),
    sorted(
        [
            # Rect(5, 5, 20, 20), # This would be ideal after adding merging
            Rect(5, 5, 10, 10),
            Rect(10, 5, 20, 10),
            Rect(5, 10, 10, 20),
            Rect(10, 10, 20, 20),
        ]
    ),
)

a = Region(Rect(5, 5, 10, 10))
b = Region(
    Rect(0, 5, 20, 10),
    Rect(5, 0, 10, 20),
)
asserta(
    f"{a} + {b}",
    sorted(a + b),
    sorted(
        [
            # Rect(5, 5, 20, 20), # This would be ideal after adding merging
            Rect(10, 5, 20, 10),
            Rect(5, 0, 10, 5),
            Rect(5, 10, 10, 20),
            Rect(5, 5, 10, 10),
            Rect(0, 5, 5, 10),
        ]
    ),
)


a = Region(
    Rect(10, 5, 20, 10),
    Rect(5, 0, 10, 5),
    Rect(5, 10, 10, 20),
    Rect(5, 5, 10, 10),
    Rect(0, 5, 5, 10),
)
assertv(f"{a}.boundingRect", a.boundingRect, Rect(0, 0, 20, 20))

a = Rect(0, 0, 20, 20)
b = Rect(10, 10, 20, 30)
asserta(
    f"{a} ^ {b}",
    a ^ b,
    Region(
        Rect(0, 0, 10, 10),
        Rect(0, 10, 10, 20),
        Rect(10, 20, 20, 30),
        Rect(10, 0, 20, 10),
    ),
)

if FAILED:
    sys.exit(1)
