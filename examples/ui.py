from time import sleep

from libremarkable import FrameBuffer as fb

from libremarkable._widgets import Scene
from libremarkable._widgets import Text
from libremarkable._widgets import Rectangle

rectangle = Rectangle(0.45, 0.45, 0.55, 0.55)
text = Text(0, 0, 1, 1, "Hello World!")
rectangle.children.append(text)
scene = Scene(fb, [rectangle])
scene.update(True)
sleep(1)
# rectangle.move(-0.3, -0.3)
rectangle.left -= 0.3
rectangle.right -= 0.3
scene.update()
