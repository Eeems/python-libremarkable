from libremarkable import Input
from libremarkable import KeyEvent
from libremarkable import FrameBuffer as fb
from libremarkable import WaveformMode

from PIL import ImageFont

from evdev.ecodes import KEY_BACKSPACE
from evdev.ecodes import KEY_ENTER

white = fb.getcolor("white")
print("Clearing screen...")
fb.set_color(white)
fb.update_full(WaveformMode.HighQualityGrayscale)

font = ImageFont.load_default(size=32)
fontHeight = sum(font.getmetrics())
x, y = 0, 0


def nextLine():
    global x, y, fontHeight
    x = 0
    y += fontHeight
    if y >= fb.height():
        y = 0


print("Ready for you to type:")
for event in Input.events(block=True):
    if not isinstance(event, KeyEvent) or event.keycode is None:
        continue

    if event.is_press:
        continue

    text = event.text
    if text is None:
        continue

    print(text, end="", flush=True)

    if event.keycode == KEY_BACKSPACE:
        continue

    if event.keycode == KEY_ENTER:
        nextLine()
        continue

    _, _, w, h = font.getbbox(text)
    if x + w >= fb.width():
        nextLine()

    fb.set_rect(x, y, w, h, white)
    fb.draw_text(x, y, w, h, text, fontSize=32)
    fb.update(x, y, w, h, WaveformMode.HighQualityGrayscale)
    x += w
    lastText = text
