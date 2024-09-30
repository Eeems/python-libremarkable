import gi
import atexit

from threading import Thread
from PIL import Image
from tempfile import NamedTemporaryFile

from ._color import getrgb

from ._mxcfb import fb_var_screeninfo
from ._mxcfb import fb_fix_screeninfo
from ._mxcfb import mxcfb_update_data

from ._framebuffer import _ensure_fb
from ._framebuffer import IMAGE_MODE

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk  # noqa: E402

_app = None
_image = None
_file = NamedTemporaryFile()
_png = NamedTemporaryFile(suffix=".png")


def _on_activate(app):
    global _image
    global _png
    global _app
    _app = app
    win = Gtk.ApplicationWindow(
        application=app,
        default_width=width(),
        default_height=height(),
        resizable=False,
    )
    _image = Gtk.Image.new_from_file(_png.name)
    win.set_child(_image)
    win.present()


def _on_exit():
    global _png
    global _file
    if _png is not None:
        _png.close()

    if _file is not None:
        _file.close()

    if _app is not None:
        _app.quit()


def _task():
    app = Gtk.Application(application_id="codes.eeems.libremarkable")
    app.connect("activate", _on_activate)
    app.run(None)


def get_var_screeninfo() -> fb_var_screeninfo:
    info = fb_var_screeninfo()
    return info


def get_fix_screeninfo() -> fb_fix_screeninfo:
    info = fb_fix_screeninfo()
    info.smem_len = _size
    return info


_size = 0


def getsize() -> int:
    return _size


def setup():
    global _file
    global _size
    image = Image.new(IMAGE_MODE, (width(), height()), getrgb("white").value)
    image.save(_png.name)
    data = image.tobytes()
    _size = len(data)
    _file.write(data)
    _file.flush()
    atexit.register(_on_exit)

    thread = Thread(target=_task)
    thread.daemon = True
    thread.start()


def width() -> int:
    return 1404


def height() -> int:
    return 1872


virtual_width = width
virtual_height = height


def x_offset() -> int:
    return 0


y_offset = x_offset


def update(data: mxcfb_update_data) -> None:
    global _png
    global _image
    if _png is None:
        return

    _ensure_fb()["image"].save(_png.name)
    if _image is not None:
        _image.set_from_file(_png.name)


def path() -> str:
    global _file
    return _file.name


def wait(marker: int) -> None:
    pass
