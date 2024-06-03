from libremarkable import Input
from libremarkable import WacomEvent
from libremarkable import TouchEvent

from libremarkable._framebuffer import WaveformMode
from libremarkable._framebuffer import update
from libremarkable._framebuffer import set_pixel

from libremarkable._color import BLACK

for event in Input.events(block=True):
    if not isinstance(event, WacomEvent) and not isinstance(event, TouchEvent):
        continue

    if isinstance(event, WacomEvent) and event.is_hover:
        continue

    x, y = event.screenPos
    set_pixel(x, y, BLACK)
    update(x, y, 1, 1, WaveformMode.Mono)
