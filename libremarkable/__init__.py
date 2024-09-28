from ._device import DeviceType
from ._device import current as deviceType

from ._input import Input
from ._input import Event
from ._input import TouchEvent
from ._input import WacomEvent
from ._input import KeyEvent
from ._input import DEFAULT_KEYMAP

from ._framebuffer import FrameBuffer as _FrameBuffer
from ._framebuffer import WaveformMode
from ._framebuffer import DEFAULT_FONT_SIZE

from ._color import color_t

# Must be done to expose __setitem__
FrameBuffer = _FrameBuffer()  #: Framebuffer instance

__all__ = [
    "DeviceType",
    "deviceType",
    "Input",
    "Event",
    "TouchEvent",
    "WacomEvent",
    "KeyEvent",
    "FrameBuffer",
    "WaveformMode",
    "color_t",
    "DEFAULT_KEYMAP",
    "DEFAULT_FONT_SIZE",
]
