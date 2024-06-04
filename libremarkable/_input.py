import math

from typing import Iterator

from evdev import list_devices
from evdev import InputDevice
from evdev import InputEvent

from evdev.ecodes import EV_ABS
from evdev.ecodes import EV_KEY
from evdev.ecodes import EV_SYN
from evdev.ecodes import ABS_X
from evdev.ecodes import ABS_Y
from evdev.ecodes import ABS_TILT_X
from evdev.ecodes import ABS_TILT_Y
from evdev.ecodes import ABS_DISTANCE
from evdev.ecodes import ABS_MT_TRACKING_ID
from evdev.ecodes import ABS_MT_SLOT
from evdev.ecodes import ABS_MT_POSITION_X
from evdev.ecodes import ABS_MT_POSITION_Y
from evdev.ecodes import ABS_MT_PRESSURE
from evdev.ecodes import BTN_TOUCH
from evdev.ecodes import BTN_STYLUS
from evdev.ecodes import BTN_TOOL_PEN
from evdev.ecodes import SYN_DROPPED
from evdev.ecodes import SYN_REPORT
from evdev.ecodes import SYN_MT_REPORT

from selectors import DefaultSelector
from selectors import EVENT_READ

from . import _framebuffer as fb

from ._device import DeviceType
from ._device import current as deviceType


def _rotate(
    *points: tuple[int, int], center: tuple[int, int], angle: int
) -> tuple[int, int]:
    cx, cy = center
    angle = angle % 360
    ang_rad = math.radians(angle)
    cos_ang, sin_ang = (
        (0, 1)
        if angle == 90
        else (-1, 0)
        if angle == 180
        else (0, -1)
        if angle == 270
        else (math.cos(ang_rad), math.sin(ang_rad))
    )
    ret = tuple(
        (cx + cos_ang * dx - sin_ang * dy, cy + sin_ang * dx + cos_ang * dy)
        for dx, dy in ((x - cx, y - cy) for x, y in points)
    )
    return ret if len(ret) > 1 else ret[0]


class Event:
    def __init__(self, device, state):
        self.device = device
        self.rawEvents = state["events"]
        self.previousData = state["previous"]
        self.data = state["current"]

    def __repr__(self):
        return f"<InputEvent rawEvents={len(self.rawEvents)}>"

    def _get_abs_range(self, code) -> tuple[int, int]:
        info = self.device.absinfo(code)
        return info.min, info.max

    def _get_abs_float(self, type: int, code: int, default: int | None) -> float | None:
        value = self.data.get((type, code), None)
        if value is None:
            return default

        min, max = self._get_abs_range(code)
        return (value - min) / (max - min)


class TouchEvent(Event):
    def __repr__(self):
        return (
            f"<TouchEvent {self.trackingId} slot={self.slot} position={self.x},{self.y} "
            f"pressure={self.pressure} rawEvents={len(self.rawEvents)}>"
        )

    @property
    def x(self) -> float | None:
        return self._get_abs_float(EV_ABS, ABS_MT_POSITION_X, None)

    @property
    def y(self) -> float | None:
        return self._get_abs_float(EV_ABS, ABS_MT_POSITION_Y, None)

    @property
    def screenPos(self) -> tuple[int, int] | None:
        x, y = self.x, 1 - self.y
        if deviceType == DeviceType.RM1:
            x = 1 - x

        maxX, maxY = fb.width() - 1, fb.height() - 1
        return int(x * maxX), int(y * maxY)

    @property
    def pressure(self) -> float | None:
        return self._get_abs_float(EV_ABS, ABS_MT_PRESSURE, None)

    @property
    def slot(self) -> int:
        return self.data.get((EV_ABS, ABS_MT_SLOT), 0)

    @property
    def trackingId(self) -> int | None:
        return self.data.get((EV_ABS, ABS_MT_TRACKING_ID), None)


class WacomEvent(Event):
    def __repr__(self):
        return (
            f"<WacomEvent position={self.x},{self.y} distance={self.distance} pressure={self.pressure} "
            f"tilt={self.tilt} {' hover ' if self.is_hover else ''}{' pressed ' if self.is_down else ''}"
            f"rawEvents={len(self.rawEvents)}>"
        )

    @property
    def x(self) -> float | None:
        return self._get_abs_float(EV_ABS, ABS_X, None)

    @property
    def y(self) -> float | None:
        return self._get_abs_float(EV_ABS, ABS_Y, None)

    @property
    def screenPos(self) -> tuple[int, int] | None:
        x, y = self.x, self.y
        if deviceType in (DeviceType.RM1, DeviceType.RM2):
            x, y = _rotate((x, y), center=(0.5, 0.5), angle=270)

        maxX, maxY = fb.width() - 1, fb.height() - 1
        return int(x * maxX), int(y * maxY)

    @property
    def distance(self) -> float | None:
        return self._get_abs_float(EV_ABS, ABS_DISTANCE, None)

    @property
    def pressure(self) -> float | None:
        return self._get_abs_float(EV_ABS, ABS_MT_PRESSURE, None)

    @property
    def tilt(self) -> tuple[int, int]:
        return (
            self._get_abs_float(EV_ABS, ABS_TILT_X, 0),
            self._get_abs_float(EV_ABS, ABS_TILT_Y, 0),
        )

    @property
    def is_down(self) -> bool:
        return bool(self.data.get((EV_KEY, BTN_TOUCH), 0))

    @property
    def is_hover(self) -> bool:
        return not self.is_down and self.data.get((EV_KEY, BTN_TOOL_PEN), 0)


def KeyEvent(Event):
    def __repr__(self):
        return "<KeyEvent rawEvents={len(self.rawEvents)}>"


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
    def deviceType(cls, device: InputDevice) -> str:
        if device in cls.keyDevices():
            return "key"

        if device in cls.wacomDevices():
            return "wacom"

        if device in cls.touchDevices():
            return "touch"

        # TODO - add mouse and other pointer device support
        return "unknown"

    @classmethod
    def rawEvents(
        cls, devices: list[InputDevice] = None, block: bool = False
    ) -> Iterator[tuple[InputDevice | None, list[InputEvent]]]:
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

                    events[device.path].append(event)
                    if event.type != EV_SYN:
                        continue

                    if event.code == SYN_DROPPED:
                        events[device.path] = []
                        continue

                    yield device, events[device.path]
                    events[device.path] = []

            if not block:
                yield None, []

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
        for d, events in cls.rawEvents(block=block):
            if d is None or not events:
                if not block:
                    yield None

                continue

            if d.path not in states.keys():
                states[d.path] = {
                    "events": [],
                    "type": cls.deviceType(d),
                    "current": {},
                    "previous": {},
                }

            state = states[d.path]
            for e in events:
                # TODO - handle touch slots
                if e.type != EV_SYN or e.code not in (SYN_REPORT, SYN_MT_REPORT):
                    state["events"].append(e)
                    state["current"][(e.type, e.code)] = e.value
                    continue

                if state["type"] == "touch":
                    yield TouchEvent(d, state)

                elif state["type"] == "wacom":
                    yield WacomEvent(d, state)

                elif state["type"] == "key":
                    yield KeyEvent(d, state)

                else:
                    yield Event(d, state)

                state["events"] = []
                state["previous"] = state["current"]
