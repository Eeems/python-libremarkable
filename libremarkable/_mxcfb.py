from ctypes import c_char
from ctypes import c_int
from ctypes import c_ushort
from ctypes import c_uint
from ctypes import c_ulong
from ctypes import Structure

from enum import auto
from enum import IntEnum

from ._ioctl import _IO
from ._ioctl import _IOW
from ._ioctl import _IOWR
from ._ioctl import _IOR

from fcntl import ioctl

FBIOGET_VSCREENINFO = 0x4600
FBIOPUT_VSCREENINFO = 0x4601
FBIOGET_FSCREENINFO = 0x4602


class Waveform(IntEnum):
    INIT = 0
    DU = 1
    GC16 = 2
    GL16 = 3
    GLR16 = 4
    GLD16 = 5
    A2 = 6
    DU4 = 7
    UNKNOWN = 8
    INIT2 = 9


class WaveformMode(IntEnum):
    """Waveform mode to use during an update"""

    #: Initialize the framebuffer
    Initialize = Waveform.INIT
    #: Black and white mode
    Mono = Waveform.DU
    #: Grayscale mode
    Grayscale = Waveform.GL16
    #: High quality mode
    HighQualityGrayscale = Waveform.GC16
    #: Highlight mode
    Highlight = Waveform.UNKNOWN


class fb_fix_screeninfo(Structure):
    _fields_ = [
        ("id", c_char * 16),
        ("smem_start", c_ulong),
        ("smem_len", c_uint),
        ("type", c_uint),
        ("type_aux", c_uint),
        ("visual", c_uint),
        ("xpanstep", c_ushort),
        ("ypanstep", c_ushort),
        ("ywrapstep", c_ushort),
        ("line_length", c_uint),
        ("mmio_start", c_ulong),
        ("mmio_len", c_uint),
        ("accel", c_uint),
        ("capabilities", c_ushort),
        ("reserved", c_ushort * 2),
    ]


class fb_bitfield(Structure):
    _fields_ = [
        ("offset", c_uint),
        ("length", c_uint),
        ("msb_right", c_uint),
    ]


class fb_var_screeninfo(Structure):
    _fields_ = [
        ("xres", c_uint),
        ("yres", c_uint),
        ("xres_virtual", c_uint),
        ("yres_virtual", c_uint),
        ("xoffset", c_uint),
        ("yoffset", c_uint),
        ("bits_per_pixel", c_uint),
        ("grayscale", c_uint),
        ("red", fb_bitfield),
        ("green", fb_bitfield),
        ("blue", fb_bitfield),
        ("transp", fb_bitfield),
        ("nonstd", c_uint),
        ("activate", c_uint),
        ("height", c_uint),
        ("width", c_uint),
        ("accel_flags", c_uint),
        ("pixclock", c_uint),
        ("left_margin", c_uint),
        ("right_margin", c_uint),
        ("upper_margin", c_uint),
        ("lower_margin", c_uint),
        ("hsync_len", c_uint),
        ("vsync_len", c_uint),
        ("sync", c_uint),
        ("vmode", c_uint),
        ("rotate", c_uint),
        ("colorspace", c_uint),
        ("reserved", c_uint * 4),
    ]


class mxcfb_gbl_alpha(Structure):
    _fields_ = [
        ("enable", c_int),
        ("alpha", c_int),
    ]


class mxcfb_loc_alpha(Structure):
    _fields_ = [
        ("enable", c_int),
        ("alpha_in_pixel", c_int),
        ("alpha_phy_addr0", c_ulong),
        ("alpha_phy_addr1", c_ulong),
    ]


class mxcfb_color_key(Structure):
    _fields_ = [
        ("enable", c_int),
        ("color_key", c_uint),
    ]


class mxcfb_pos(Structure):
    _fields_ = [
        ("x", c_ushort),
        ("y", c_ushort),
    ]


class mxcfb_gamma(Structure):
    _fields_ = [
        ("enable", c_int),
        ("constk", c_int * 16),
        ("slopek", c_int * 16),
    ]


class mxcfb_gpu_split_fmt(Structure):
    _fields_ = [
        ("var", fb_var_screeninfo),
        ("offset", c_ulong),
    ]


class mxcfb_rect(Structure):
    _fields_ = [
        ("top", c_uint),
        ("left", c_uint),
        ("width", c_uint),
        ("height", c_uint),
    ]


GRAYSCALE_8BIT = 0x1
GRAYSCALE_8BIT_INVERTED = 0x2
GRAYSCALE_4BIT = 0x3
GRAYSCALE_4BIT_INVERTED = 0x4

AUTO_UPDATE_MODE_REGION_MODE = 0
AUTO_UPDATE_MODE_AUTOMATIC_MODE = 1

UPDATE_SCHEME_SNAPSHOT = 0
UPDATE_SCHEME_QUEUE = 1
UPDATE_SCHEME_QUEUE_AND_MERGE = 2

UPDATE_MODE_PARTIAL = 0x0
UPDATE_MODE_FULL = 0x1

WAVEFORM_MODE_GLR16 = 4
WAVEFORM_MODE_GLD16 = 5
WAVEFORM_MODE_AUTO = 257

TEMP_USE_AMBIENT = 0x1000
TEMP_USE_REMARKABLE_DRAW = 0x0018

EPDC_FLAG_ENABLE_INVERSION = 0x01
EPDC_FLAG_FORCE_MONOCHROME = 0x02
EPDC_FLAG_USE_CMAP = 0x04
EPDC_FLAG_USE_ALT_BUFFER = 0x100
EPDC_FLAG_TEST_COLLISION = 0x200
EPDC_FLAG_GROUP_UPDATE = 0x400
EPDC_FLAG_USE_DITHERING_Y1 = 0x2000
EPDC_FLAG_USE_DITHERING_Y4 = 0x4000
EPDC_FLAG_USE_REGAL = 0x8000


class mxcfb_dithering_mode(IntEnum):
    EPDC_FLAG_USE_DITHERING_PASSTHROUGH = 0x0
    EPDC_FLAG_USE_DITHERING_FLOYD_STEINBERG = auto()
    EPDC_FLAG_USE_DITHERING_ATKINSON = auto()
    EPDC_FLAG_USE_DITHERING_ORDERED = auto()
    EPDC_FLAG_USE_DITHERING_QUANT_ONLY = auto()
    EPDC_FLAG_USE_DITHERING_MAX = auto()


FB_POWERDOWN_DISABLE = -1
FB_TEMP_AUTO_UPDATE_DISABLE = -1


class mxcfb_alt_buffer_data(Structure):
    _fields_ = [
        ("phys_addr", c_uint),
        ("width", c_uint),
        ("height", c_uint),
        ("alt_update_region", mxcfb_rect),
    ]


class mxcfb_update_data(Structure):
    _fields_ = [
        ("update_region", mxcfb_rect),
        ("waveform_mode", c_uint),
        ("update_mode", c_uint),
        ("update_marker", c_uint),
        ("temp", c_int),
        ("flags", c_uint),
        ("dither_mode", c_int),
        ("quant_bit", c_int),
        ("alt_buffer_data", mxcfb_alt_buffer_data),
    ]


class mxcfb_update_marker_data(Structure):
    _fields_ = [
        ("update_marker", c_uint),
        ("collision_test", c_uint),
    ]


class mxcfb_waveform_modes(Structure):
    _fields_ = [
        ("mode_init", c_int),
        ("mode_du", c_int),
        ("mode_gc4", c_int),
        ("mode_gc8", c_int),
        ("mode_gc16", c_int),
        ("mode_gc32", c_int),
    ]


class mxcfb_csc_matrix(Structure):
    _fields_ = [
        ("update_marker", c_int * 5 * 3),
    ]


MXCFB_WAIT_FOR_VSYNC = _IOW("F", 0x20, c_uint)
MXCFB_SET_GBL_ALPHA = _IOW("F", 0x21, mxcfb_gbl_alpha)
MXCFB_SET_CLR_KEY = _IOW("F", 0x22, mxcfb_color_key)
MXCFB_SET_OVERLAY_POS = _IOWR("F", 0x24, mxcfb_pos)
MXCFB_GET_FB_IPU_CHAN = _IOR("F", 0x25, c_uint)
MXCFB_SET_LOC_ALPHA = _IOWR("F", 0x26, mxcfb_loc_alpha)
MXCFB_SET_LOC_ALP_BUF = _IOW("F", 0x27, c_ulong)
MXCFB_SET_GAMMA = _IOW("F", 0x28, mxcfb_gamma)
MXCFB_GET_FB_IPU_DI = _IOR("F", 0x29, c_uint)
MXCFB_GET_DIFMT = _IOR("F", 0x2A, c_uint)
MXCFB_GET_FB_BLANK = _IOR("F", 0x2B, c_uint)
MXCFB_SET_DIFMT = _IOW("F", 0x2C, c_uint)
MXCFB_CSC_UPDATE = _IOW("F", 0x2D, mxcfb_csc_matrix)
MXCFB_SET_GPU_SPLIT_FMT = _IOW("F", 0x2F, mxcfb_gpu_split_fmt)
MXCFB_SET_PREFETCH = _IOW("F", 0x30, c_int)
MXCFB_GET_PREFETCH = _IOR("F", 0x31, c_int)

MXCFB_SET_WAVEFORM_MODES = _IOW("F", 0x2B, mxcfb_waveform_modes)
MXCFB_SET_TEMPERATURE = _IOW("F", 0x2C, c_int)
MXCFB_SET_AUTO_UPDATE_MODE = _IOW("F", 0x2D, c_uint)
MXCFB_SEND_UPDATE = _IOW("F", 0x2E, mxcfb_update_data)
MXCFB_WAIT_FOR_UPDATE_COMPLETE = _IOWR("F", 0x2F, mxcfb_update_marker_data)
MXCFB_SET_PWRDOWN_DELAY = _IOW("F", 0x30, c_int)
MXCFB_GET_PWRDOWN_DELAY = _IOR("F", 0x31, c_int)
MXCFB_SET_UPDATE_SCHEME = _IOW("F", 0x32, c_uint)
MXCFB_GET_WORK_BUFFER = _IOWR("F", 0x34, c_ulong)
MXCFB_SET_TEMP_AUTO_UPDATE_PERIOD = _IOW("F", 0x36, c_int)
MXCFB_DISABLE_EPDC_ACCESS = _IO("F", 0x35)
MXCFB_ENABLE_EPDC_ACCESS = _IO("F", 0x36)

FB_PATH = "/dev/fb0"


class MXCFBException(Exception):
    pass


def get_var_screeninfo() -> fb_var_screeninfo:
    with open(FB_PATH, "rb") as f:
        info = fb_var_screeninfo()
        res = ioctl(f.fileno(), FBIOGET_VSCREENINFO, info)
        if res < 0:
            raise MXCFBException(res)

        return info


def get_fix_screeninfo() -> fb_fix_screeninfo:
    with open(FB_PATH, "rb") as f:
        info = fb_fix_screeninfo()
        res = ioctl(f.fileno(), FBIOGET_FSCREENINFO, info)
        if res < 0:
            raise MXCFBException(res)

        return info


def getsize() -> int:
    return get_fix_screeninfo().smem_len


_width = None
_height = None
_v_width = None
_v_height = None
_x_offset = None
_y_offset = None
_pixel_width = None


def setup():
    pass


def width() -> int:
    global _width
    if _width is None:
        _width = get_var_screeninfo().xres

    return _width


def height() -> int:
    global _height
    if _height is None:
        _height = get_var_screeninfo().yres

    return _height


def virtual_width() -> int:
    global _v_width
    if _v_width is None:
        _v_width = get_var_screeninfo().xres_virtual

    return _v_width


def virtual_height() -> int:
    global _v_height
    if _v_height is None:
        _v_height = get_var_screeninfo().yres_virtual

    return _v_height


def x_offset() -> int:
    global _x_offset
    if _x_offset is None:
        _x_offset = get_var_screeninfo().xoffset

    return _x_offset


def y_offset() -> int:
    global _y_offset
    if _y_offset is None:
        _y_offset = get_var_screeninfo().yoffset

    return _y_offset


def pixel_size() -> int:
    global _pixel_width
    if _pixel_width is None:
        _pixel_width = int(get_var_screeninfo().bits_per_pixel / 8)

    return _pixel_width


def _fileno():
    from ._framebuffer import _ensure_fb

    return _ensure_fb()["f"].fileno()


def update(data: mxcfb_update_data) -> None:
    res = ioctl(_fileno(), MXCFB_SEND_UPDATE, data)
    if res < 0:
        raise MXCFBException(res)


def path() -> str:
    return "/dev/fb0"


def wait(marker: int) -> None:
    data = mxcfb_update_marker_data()
    data.update_marker = marker
    res = ioctl(_fileno(), MXCFB_WAIT_FOR_UPDATE_COMPLETE, data)
    if res < 0:
        raise MXCFBException(res)
