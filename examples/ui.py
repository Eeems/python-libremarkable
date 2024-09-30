import os

from time import sleep

from libremarkable import FrameBuffer as fb

from libremarkable._widgets import Scene
from libremarkable._widgets import Text
from libremarkable._widgets import Rectangle
from libremarkable._widgets import Picture
from libremarkable._widgets import Ellipse

image_path = "/opt/usr/share/icons/oxide/48x48/apps/image.png"
if not os.path.exists(image_path):
    image_path = "/usr/share/icons/hicolor/48x48/status/bluetooth-active.png"

text = Text("Hello World!", 0.015, 0.015, 0.985, 0.985)
rectangle = Rectangle(
    0.45,
    0.45,
    0.55,
    0.55,
    color="black",
    lineWidth=3,
    children=[
        text,
        Ellipse(0, 0, 1, 1, color="black", background="white", lineWidth=3),
    ],
)
scene = Scene(
    fb,
    children=[
        rectangle,
        Ellipse(0.9, 0.9, 0.99, 0.99, color="black", background="white", lineWidth=3),
        Picture(image_path, 0, 0, 0.03, 0.03),
    ],
)
scene.update()
sleep(1)
rectangle.translate(-0.3, 0)
scene.update()
sleep(1)
text.text = "Yo!"
scene.update()
