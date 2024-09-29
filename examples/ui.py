from time import sleep

from libremarkable import FrameBuffer as fb

from libremarkable._widgets import Scene
from libremarkable._widgets import Text
from libremarkable._widgets import Rectangle

rectangle = Rectangle(0.4, 0.4, 0.6, 0.6)
text = Text(0, 0, 1, 1)
text.text = "Hello World!"
rectangle.children.append(text)
scene = Scene(fb, [rectangle])
scene.update()
sleep(1)
rectangle.left -= 0.3
rectangle.right -= 0.3
scene.update()
