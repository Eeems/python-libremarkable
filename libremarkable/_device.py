import os

from enum import auto
from enum import Enum


class DeviceType(Enum):
    UNKNOWN = auto()
    RM1 = auto()
    RM2 = auto()

    @staticmethod
    def current():
        if hasattr(DeviceType, "__model"):
            return DeviceType.__model

        with open("/sys/devices/soc0/machine", "r") as f:
            modelName = f.read().strip()

        if modelName in ("reMarkable 1.0", "reMarkable Prototype 1"):
            DeviceType.__model = DeviceType.RM1

        elif modelName == "reMarkable 2.0":
            DeviceType.__model = DeviceType.RM2

        else:
            DeviceType.__model = DeviceType.UNKNOWN

        return DeviceType.__model
