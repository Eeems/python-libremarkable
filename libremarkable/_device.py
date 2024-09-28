import os

from enum import auto
from enum import Enum


class DeviceType(Enum):
    #: Unknown device
    UNKNOWN = auto()
    #: reMarkable 1
    RM1 = auto()
    #: reMarkable 2
    RM2 = auto()
    #: reMarkable Paper Pro
    RMPP = auto()


if os.path.exists("/sys/devices/soc0/machine"):
    with open("/sys/devices/soc0/machine", "r") as f:
        modelName = f.read().strip()

else:
    import platform as p

    c = p.processor()
    if not c:
        c = p.machine()

    modelName = f"{p.system()} {c if c else 'Unknown'}"
    del p
    del c


if modelName in ("reMarkable 1.0", "reMarkable Prototype 1"):
    current = DeviceType.RM1

elif modelName == "reMarkable 2.0":
    current = DeviceType.RM2

elif modelName == "reMarkable Ferrari":
    current = DeviceType.RMPP

else:
    current = DeviceType.UNKNOWN

__all__ = [
    "DeviceType",
    "current",
]
