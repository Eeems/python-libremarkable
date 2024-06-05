import time

from contextlib import contextmanager

from PIL import Image

from libremarkable import deviceType
from libremarkable import FrameBuffer as fb

from libremarkable._framebuffer import WaveformMode


@contextmanager
def performance_log(msg: str = ""):
    start = time.perf_counter_ns()
    yield
    end = time.perf_counter_ns()
    print(f"{msg}: {(end - start) / 1000000}ms")


print(f"Device Type: {deviceType}")
print(f"FrameBuffer path: {fb.path()}")
print(f"Size: {fb.size()}")
print(f"Width: {fb.width()}")
print(f"Height: {fb.height()}")


with performance_log("Init to white"):
    fb.set_color("white")

with performance_log("Screen Update"):
    fb.update_full(WaveformMode.HighQualityGrayscale, sync=True)

with performance_log("Total"):
    with performance_log("Black Rectangle"):
        fb.set_rect(10, 10, 500, 500, "black")

    with performance_log("Border"):
        fb.draw_rect(6, 6, 514, 514, "black", lineSize=3)

    with performance_log("Screen Update"):
        fb.update(0, 0, 520, 520, WaveformMode.Mono)

    with performance_log("Checkboard background"):
        fb.set_rect(210, 210, 100, 100, "white")

    with performance_log("Checkboard dots"):
        for y in range(210, 310, 2):
            for x in range(210, 310, 2):
                fb.set_pixel(x, y, "black")

    with performance_log("Screen Update"):
        fb.update(210, 210, 310, 310, WaveformMode.Mono)

    with performance_log("Draw text"):
        fb.draw_text(800, 800, 150, 100, "Hello World!")

    with performance_log("Screen Update"):
        fb.update(800, 800, 150, 100, WaveformMode.HighQualityGrayscale)

    with performance_log("Draw multiline text"):
        fb.draw_text(800, 900, 100, 100, "This is\nMultiline!")

    with performance_log("Screen Update"):
        fb.update(800, 900, 100, 100, WaveformMode.HighQualityGrayscale)

with performance_log("Save text from framebuffer"):
    image = fb.to_image(800, 800, 150, 100)
    image.save("/tmp/py.text.png")

with performance_log("Save entire framebuffer"):
    image = fb.to_image()
    image.save("/tmp/py.fb.png")

image = Image.open("/tmp/py.fb.png")
with performance_log("Replace framebuffer with contents of image"):
    fb.draw_image(0, 0, image)

fb.update_full(WaveformMode.HighQualityGrayscale)
fb.release()
