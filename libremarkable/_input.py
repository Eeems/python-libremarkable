from typing import Iterator

from evdev import list_devices
from evdev import InputDevice
from evdev import InputEvent

from evdev.ecodes import EV_ABS
from evdev.ecodes import EV_KEY
from evdev.ecodes import ABS_MT_TRACKING_ID
from evdev.ecodes import BTN_STYLUS

from selectors import DefaultSelector
from selectors import EVENT_READ


class Input:
    @classmethod
    def devices(cls):
        return [InputDevice(path) for path in list_devices()]

    @classmethod
    def positionDevices(cls):
        return [d for d in cls.devices() if EV_ABS in d.capabilities()]

    @classmethod
    def keyDevices(cls):
        return [
            d
            for d in cls.devices()
            if d not in cls.positionDevices() and EV_KEY in d.capabilities()
        ]

    @classmethod
    def touchDevices(cls):
        return [d for d in cls.positionDevices() if d.absinfo(ABS_MT_TRACKING_ID).max]

    @classmethod
    def wacomDevices(cls):
        return [
            d
            for d in cls.positionDevices()
            if d not in cls.touchDevices() and BTN_STYLUS in d.capabilities()[EV_KEY]
        ]

    @classmethod
    def events(
        cls, devices: list[InputDevice], block: bool = False
    ) -> Iterator[tuple[InputDevice, InputEvent] | tuple[None, None]]:
        selector = DefaultSelector()
        for device in devices:
            selector.register(device, EVENT_READ)

        while True:
            for key, mask in selector.select(timeout=None if block else 0):
                device = key.fileobj
                for event in device.read():
                    yield device, event

            yield None, None
