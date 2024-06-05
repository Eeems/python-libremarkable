from libremarkable import Input
from libremarkable import KeyEvent

# from libremarkable import FrameBuffer as fb
# from libremarkable import WaveformMode

# fb.set_color("white")
# fb.update_full(WaveformMode.HighQualityGrayscale, sync=True)

for event in Input.events(block=True):
    if not isinstance(event, KeyEvent) or event.keycode is None:
        continue

    if event.is_press:
        continue

    text = event.text
    if text is not None:
        print(text, end="", flush=True)
