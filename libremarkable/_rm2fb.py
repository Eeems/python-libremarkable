import os
import errno

from ctypes import byref
from ctypes import c_char
from ctypes import c_int
from ctypes import c_long
from ctypes import c_ushort
from ctypes import c_uint32
from ctypes import get_errno
from ctypes import sizeof
from ctypes import Structure
from ctypes import Union

from enum import auto
from enum import IntEnum

from typing import overload

from ._mxcfb import mxcfb_update_data
from ._mxcfb import Waveform
from ._libc import msgsnd
from ._libc import msgget


class MSG_TYPE(IntEnum):
    INIT = 1
    UPDATE = auto()
    XO = auto()
    WAIT = auto()


class xochitl_data(Union):
    _fields_ = [
        ("x1", c_int),
        ("y1", c_int),
        ("x2", c_int),
        ("y2", c_int),
        ("waveform", c_int),
        ("flags", c_int),
    ]


class wait_sem_data(Union):
    _fields_ = [
        ("sem_name", c_int),
    ]


class swtfb_update_mdata(Union):
    _fields_ = [
        ("xochitl_update", xochitl_data),
        ("update", mxcfb_update_data),
        ("wait_update", wait_sem_data),
    ]


class swtfb_update(Structure):
    _fields_ = [
        ("mtype", c_long),
        ("length", c_uint32),
        ("mdata", swtfb_update_mdata),
    ]


class RM2FBException(Exception):
    pass


IPC_CREAT = 512
msg_q_id = 0x2257C
msqid = msgget(msg_q_id, IPC_CREAT | 600)
if msqid < 0:
    err = os.strerror(get_errno())
    raise RM2FBException(f"Failed to get message queue: {err}")


@overload
def send(data: wait_sem_data) -> None:
    ...


@overload
def send(data: xochitl_data) -> None:
    ...


@overload
def send(data: mxcfb_update_data) -> None:
    ...


def send(data):
    global msqid
    msg = swtfb_update()
    if isinstance(data, wait_sem_data):
        msg.mtype = MSG_TYPE.WAIT
        msg.mdata.wait_update = data
        res = msgsnd(msqid, byref(msg), sizeof(msg.mdata.wait_update), 0)
        if res < 0:
            err = os.strerror(get_errno())
            raise RM2FBException(f"Error sending wait update: {err} {res}")

    elif isinstance(data, xochitl_data):
        msg.mtype = MSG_TYPE.XO
        msg.mdata.xochitl_update = data
        res = msgsnd(msqid, byref(msg), sizeof(msg.mdata.xochitl_update), 0)
        if res < 0:
            err = os.strerror(get_errno())
            raise RM2FBException(f"Error sending xochitl update: {err} {res}")

    elif isinstance(data, mxcfb_update_data):
        msg.mtype = MSG_TYPE.UPDATE
        msg.mdata.update = data
        res = msgsnd(msqid, byref(msg), sizeof(msg.mdata.update), 0)
        if res < 0:
            err = os.strerror(get_errno())
            raise RM2FBException(f"Error sendng mxcfb update: {err} {res}")

    else:
        raise NotImplementedError()


def width():
    return 1404


def pixel_size():
    return sizeof(c_ushort)


def wait(marker: int) -> None:
    data = wait_sem_data()
    data.smem_name = f"/rm2fb.wait.{os.getpid()}"
    send(data)
