import os

from ._device import DeviceType


def use_rm2fb() -> bool:
    return DeviceType.current() == DeviceType.RM2 and os.path.exists(
        "/dev/shm/swtfb.01"
    )
