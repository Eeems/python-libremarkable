from libremarkable import Input
from libremarkable import WacomEvent
from libremarkable import TouchEvent

from libremarkable import FrameBuffer as fb
from libremarkable._framebuffer import WaveformMode

fb.set_color("white")
fb.update_full(WaveformMode.HighQualityGrayscale, sync=True)

black = fb.getcolor("black")
for event in Input.events(block=True):
    if not isinstance(event, WacomEvent) and not isinstance(event, TouchEvent):
        continue

    # Touch lifted
    if isinstance(event, TouchEvent) and event.trackingId == -1:
        continue

    # Pen not touching
    if isinstance(event, WacomEvent) and event.is_hover:
        continue

    screenPos = event.screenPos
    if screenPos is None:
        continue

    x2, y2 = screenPos
    x1, y1 = (
        event.previousScreenPos
        if not isinstance(event, WacomEvent) or event.was_down
        else None
    ) or (x2, y2)
    fb.draw_line(x1, y1, x2, y2, black)
    fb.update(x1, y1, x2 - x1 + 1, y2 - y1 + 1, WaveformMode.Mono)
