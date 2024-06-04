from libremarkable import Input
from libremarkable import WacomEvent
from libremarkable import TouchEvent

from libremarkable import FrameBuffer as fb
from libremarkable._framebuffer import WaveformMode

for event in Input.events(block=True):
    if not isinstance(event, WacomEvent) and not isinstance(event, TouchEvent):
        continue

    if isinstance(event, WacomEvent) and event.is_hover:
        continue

    x, y = event.screenPos
    fb[(x, y)] = "black"
    fb.update(x, y, 1, 1, WaveformMode.Mono)
