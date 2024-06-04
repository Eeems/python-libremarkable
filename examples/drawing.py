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

    x1, y1 = screenPos
    x2, y2 = event.previousScreenPos or (x1, y1)
    # print((x1, y1), (x2, y2))
    print("data:", event.data)
    print("previous:", event.previousData)
    fb.draw_line(x1, y1, x2, y2, black)
    fb.update(x1, y1, x2 - x1 + 1, y2 - y1 + 1, WaveformMode.Mono)
