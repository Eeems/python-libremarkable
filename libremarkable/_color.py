from ctypes import c_ushort as color_t  # Aliased to allow changing easily

from PIL import ImageColor

_rgb8_to_5_lut = []
for x in range(0, 256):
    _rgb8_to_5_lut.insert(x, (x >> 3) & 0x1F)

_rgb8_to_6_lut = []
for x in range(0, 256):
    _rgb8_to_6_lut.insert(x, (x >> 2) & 0x3F)


def rgb888_to_rgb565(r: int, g: int, b: int) -> int:
    """Convert a rgb888 tuple into a rgb565 integer"""
    global _rgb8_to_5_lut
    global _rgb8_to_6_lut
    return _rgb8_to_5_lut[r] << 11 | _rgb8_to_6_lut[g] << 5 | _rgb8_to_5_lut[b]


def get_rgb565(color: int) -> tuple[int]:
    """Convert a rgb565 integer into a rgb565 tuple"""
    return (
        (color >> 11) & 0x1F,
        (color >> 5) & 0x3F,
        color & 0x1F,
    )


_rgb5_to_8_lut = []
for x in range(0, 32):
    _rgb5_to_8_lut.insert(x, (x * 527 + 23) >> 6)

# Pad to 256 entries for use with PIL.Image.point
_rgb5_to_8_lut += [0] * (256 - len(_rgb5_to_8_lut))

_rgb6_to_8_lut = []
for x in range(0, 64):
    _rgb6_to_8_lut.insert(x, (x * 259 + 33) >> 6)

# Pad to 256 entries for use with PIL.Image.point
_rgb6_to_8_lut += [0] * (256 - len(_rgb6_to_8_lut))


def rgb565_to_rgb888(color: int) -> tuple[int]:
    """Convert a rgb565 integer into a rgb888 tuple"""
    global _rgb5_to_8_lut
    global _rgb6_to_8_lut
    r, g, b = get_rgb565(color)
    return _rgb5_to_8_lut[r], _rgb6_to_8_lut[g], _rgb5_to_8_lut[b]


def getrgb(color: str) -> color_t:
    return color_t(rgb888_to_rgb565(*ImageColor.getrgb(color)))
