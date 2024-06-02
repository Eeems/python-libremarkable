from typing import Iterator

from evdev import categorize
from evdev import list_devices
from evdev import InputDevice
from evdev import InputEvent
from evdev import SynEvent

from evdev.ecodes import EV_ABS
from evdev.ecodes import EV_KEY
from evdev.ecodes import EV_SYN
from evdev.ecodes import ABS_MT_TRACKING_ID
from evdev.ecodes import BTN_STYLUS
from evdev.ecodes import SYN_DROPPED

from selectors import DefaultSelector
from selectors import EVENT_READ


class Event:
    def __init__(self, device, events):
        self.device = device
        self.rawEvents = events


class Input:
    @classmethod
    def devices(cls) -> list[InputDevice]:
        return [InputDevice(path) for path in list_devices()]

    @classmethod
    def positionDevices(cls) -> list[InputDevice]:
        return [d for d in cls.devices() if EV_ABS in d.capabilities()]

    @classmethod
    def keyDevices(cls) -> list[InputDevice]:
        return [
            d
            for d in cls.devices()
            if d not in cls.positionDevices() and EV_KEY in d.capabilities()
        ]

    @classmethod
    def touchDevices(cls) -> list[InputDevice]:
        return [d for d in cls.positionDevices() if d.absinfo(ABS_MT_TRACKING_ID).max]

    @classmethod
    def wacomDevices(cls) -> list[InputDevice]:
        return [
            d
            for d in cls.positionDevices()
            if d not in cls.touchDevices() and BTN_STYLUS in d.capabilities()[EV_KEY]
        ]

    @classmethod
    def rawEvents(
        cls, devices: list[InputDevice] = None, block: bool = False
    ) -> Iterator[tuple[InputDevice, InputEvent] | tuple[None, None]]:
        selector = DefaultSelector()
        if devices is None:
            devices = cls.devices()

        for device in devices:
            selector.register(device, EVENT_READ)

        events = {}
        while True:
            for key, mask in selector.select(timeout=None if block else 0):
                device = key.fileobj
                for event in device.read():
                    if device.path not in events.keys():
                        events[device.path] = []

                    if event.type != EV_SYN:
                        events[device.path].append(event)
                        continue

                    if event.code == SYN_DROPPED:
                        events[device.path] = []
                        continue

                    for e in events[device.path]:
                        yield device, categorize(e)

                    yield device, categorize(event)
                    events[device.path] = []

            yield None, None

    @classmethod
    def rawPositionEvents(
        cls, block: bool = False
    ) -> Iterator[tuple[InputDevice, InputEvent] | tuple[None, None]]:
        for d, e in cls.rawEvents(cls.positionDevices(), block=block):
            yield d, e

    @classmethod
    def rawTouchEvents(
        cls, block: bool = False
    ) -> Iterator[tuple[InputDevice, InputEvent] | tuple[None, None]]:
        for d, e in cls.rawEvents(cls.touchDevices(), block=block):
            yield d, e

    @classmethod
    def rawWacomEvents(
        cls, block: bool = False
    ) -> Iterator[tuple[InputDevice, InputEvent] | tuple[None, None]]:
        for d, e in cls.rawEvents(cls.wacomDevices(), block=block):
            yield d, e

    @classmethod
    def rawKeyEvents(
        cls, block: bool = False
    ) -> Iterator[tuple[InputDevice, InputEvent] | tuple[None, None]]:
        for d, e in cls.rawEvents(cls.keyDevices(), block=block):
            yield d, e

    @classmethod
    def events(cls, block: bool = False) -> Event | None:
        states = {}
        for d, e in cls.rawEvents(block=block):
            if d is None:
                yield None
                continue
            if d.path not in states.keys():
                states[d.path] = {"events": []}

            state = states[d.path]
            if not isinstance(e, SynEvent):
                state["events"].append(e)
                continue

            yield Event(d, state["events"])
            state["events"] = []
