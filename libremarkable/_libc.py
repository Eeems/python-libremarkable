from ctypes import cdll
from ctypes import c_int
from ctypes import c_ulong
from ctypes import get_errno

libc = cdll.LoadLibrary("libc.so.6")


def ioctl(fd, request, *args):
    res = libc.ioctl(c_int(fd), c_ulong(request), *args)
    if res < 0:
        err = get_errno()
        raise OSError(err, os.strerror(err))

    return res
