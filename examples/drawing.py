from libremarkable import Input
from libremarkable import WacomEvent
from libremarkable import TouchEvent

from libremarkable import FrameBuffer as fb
from libremarkable._framebuffer import WaveformMode

from libremarkable._color import BLACK

for event in Input.events(block=True):
    if not isinstance(event, WacomEvent) and not isinstance(event, TouchEvent):
        continue

    if isinstance(event, WacomEvent) and event.is_hover:
        continue

    x, y = event.screenPos
    fb.set_pixel(x, y, BLACK)
    fb.update(x, y, 1, 1, WaveformMode.Mono)
