from ctypes import c_ushort as c_t  # Aliased to allow changing easily

WHITE = c_t(0xFFFF)
BLACK = c_t(0x0000)

_rgb8_to_5_lut = []
for x in range(0, 256):
    _rgb8_to_5_lut.insert(x, (x >> 3) & 0x1F)

_rgb8_to_6_lut = []
for x in range(0, 256):
    _rgb8_to_6_lut.insert(x, (x >> 2) & 0x3F)


def rgb888_to_rgb565(r: int, g: int, b: int) -> int:
    global _rgb8_to_5_lut
    global _rgb8_to_6_lut
    return _rgb8_to_5_lut[r] << 11 | _rgb8_to_6_lut[g] << 5 | _rgb8_to_5_lut[b]


def get_rgb565(color: int) -> tuple[int]:
    return (
        (color >> 11) & 0x1F,
        (color >> 5) & 0x3F,
        color & 0x1F,
    )


_rgb5_to_8_lut = []
for x in range(0, 32):
    _rgb5_to_8_lut.insert(x, (x * 527 + 23) >> 6)

_rgb6_to_8_lut = []
for x in range(0, 64):
    _rgb6_to_8_lut.insert(x, (x * 259 + 33) >> 6)


def rgb565_to_rgb888(color: int) -> tuple[int]:
    global _rgb5_to_8_lut
    global _rgb6_to_8_lut
    r, g, b = get_rgb565(color)
    return _rgb5_to_8_lut[r], _rgb6_to_8_lut[g], _rgb5_to_8_lut[b]
