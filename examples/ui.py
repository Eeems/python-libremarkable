from time import sleep

from libremarkable import FrameBuffer as fb

from libremarkable._widgets import Scene
from libremarkable._widgets import Text
from libremarkable._widgets import Rectangle
from libremarkable._widgets import Picture

rectangle = Rectangle(0.45, 0.45, 0.55, 0.55, color="black", lineWidth=3)
text = Text(0.015, 0.015, 0.985, 0.985, "Hello World!")
rectangle.children.append(text)
scene = Scene(
    fb,
    [
        rectangle,
        Picture(0, 0, 0.03, 0.03, "/opt/usr/share/icons/oxide/48x48/apps/image.png"),
    ],
)
scene.update()
sleep(1)
rectangle.translate(-0.3, 0)
scene.update()
sleep(1)
text.text = "Yo!"
scene.update()
