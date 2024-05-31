from enum import auto
from enum import Enum


class DeviceType(Enum):
    UNKNOWN = auto()
    RM1 = auto()
    RM2 = auto()


with open("/sys/devices/soc0/machine", "r") as f:
    modelName = f.read().strip()

if modelName in ("reMarkable 1.0", "reMarkable Prototype 1"):
    current = DeviceType.RM1

elif modelName == "reMarkable 2.0":
    current = DeviceType.RM2

else:
    current = DeviceType.UNKNOWN
