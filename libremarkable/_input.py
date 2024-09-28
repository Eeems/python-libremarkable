import math

from errno import ENODEV

from copy import deepcopy

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
from evdev.ecodes import KEY_LEFTSHIFT
from evdev.ecodes import KEY_RIGHTSHIFT

from selectors import DefaultSelector
from selectors import EVENT_READ

from ._framebuffer import FrameBuffer as fb

from ._device import DeviceType
from ._device import current as deviceType

from ._keymap import keymap as DEFAULT_KEYMAP


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
    """Input event"""

    def __init__(self, device, state):
        self.device = device  #: Event device
        self.rawEvents = state["events"]  #: Raw events
        self.previousData = state["previous"].get(
            state["slot"], {}
        )  #: Previous event data
        self.data = state["current"].get(state["slot"], {})  #: Current event data

    def __repr__(self):
        return f"Event(rawEvents={len(self.rawEvents)})"

    def _get_abs_range(self, code) -> tuple[int, int]:
        info = self.device.absinfo(code)
        return info.min, info.max

    def _get_abs_float(self, type: int, code: int, default: int | None) -> float | None:
        value = self.data.get((type, code), None)
        if value is None:
            return default

        min, max = self._get_abs_range(code)
        return (value - min) / (max - min)

    def _get_previous_abs_float(
        self, type: int, code: int, default: int | None
    ) -> float | None:
        value = self.previousData.get((type, code), None)
        if value is None:
            return default

        min, max = self._get_abs_range(code)
        return (value - min) / (max - min)


class TouchEvent(Event):
    """Touch Event"""

    def __init__(self, device, state):
        super().__init__(device, state)
        if self.previousTrackingId == -1:
            self.previousData = {(EV_ABS, ABS_MT_TRACKING_ID): -1}

    def __repr__(self):
        return (
            f"TouchEvent({self.trackingId} slot={self.slot} position={self.x},{self.y} "
            f"pressure={self.pressure} rawEvents={len(self.rawEvents)})"
        )

    def _screenPos(self, x: int | None, y: int | None) -> tuple[int, int] | None:
        if x is None or y is None:
            return None

        y = 1 - y
        if deviceType == DeviceType.RM1:
            x = 1 - x

        maxX, maxY = fb.width() - 1, fb.height() - 1
        return int(x * maxX), int(y * maxY)

    @property
    def x(self) -> float | None:
        """x coordinate"""
        return self._get_abs_float(EV_ABS, ABS_MT_POSITION_X, None)

    @property
    def y(self) -> float | None:
        """y coordinate"""
        return self._get_abs_float(EV_ABS, ABS_MT_POSITION_Y, None)

    @property
    def screenPos(self) -> tuple[int, int] | None:
        """Screen coordinates"""
        return self._screenPos(self.x, self.y)

    @property
    def pressure(self) -> float | None:
        """Touch pressure"""
        return self._get_abs_float(EV_ABS, ABS_MT_PRESSURE, None)

    @property
    def slot(self) -> int:
        """Touch slot"""
        return self.data.get((EV_ABS, ABS_MT_SLOT), 0)

    @property
    def trackingId(self) -> int | None:
        """Tracking ID"""
        return self.data.get((EV_ABS, ABS_MT_TRACKING_ID), None)

    @property
    def previousX(self) -> float | None:
        """Previous x coordinate"""
        return self._get_previous_abs_float(EV_ABS, ABS_MT_POSITION_X, None)

    @property
    def previousY(self) -> float | None:
        """Previous y coordinate"""
        return self._get_previous_abs_float(EV_ABS, ABS_MT_POSITION_Y, None)

    @property
    def previousScreenPos(self) -> tuple[int, int] | None:
        """Previous screen coordinates"""
        return self._screenPos(self.previousX, self.previousY)

    @property
    def previousPressure(self) -> float | None:
        """Previous touch pressure"""
        return self._get_previous_abs_float(EV_ABS, ABS_MT_PRESSURE, None)

    @property
    def previousTrackingId(self) -> int | None:
        """Previous tracking ID"""
        return self.previousData.get((EV_ABS, ABS_MT_TRACKING_ID), None)


class WacomEvent(Event):
    """Tablet Event"""

    def __init__(self, device, state):
        super().__init__(device, state)
        if not self.was_down and not self.was_hover:
            self.previousData = {}

    def __repr__(self):
        return (
            f"WacomEvent(position={self.x},{self.y} distance={self.distance} pressure={self.pressure} "
            f"tilt={self.tilt} {' hover ' if self.is_hover else ''}{' pressed ' if self.is_down else ''}"
            f"rawEvents={len(self.rawEvents)})"
        )

    def _screenPos(self, x: int | None, y: int | None) -> tuple[int, int] | None:
        if x is None or y is None:
            return None

        if deviceType in (DeviceType.RM1, DeviceType.RM2):
            x, y = _rotate((x, y), center=(0.5, 0.5), angle=270)

        maxX, maxY = fb.width() - 1, fb.height() - 1
        return int(x * maxX), int(y * maxY)

    @property
    def x(self) -> float | None:
        """x coordinate"""
        return self._get_abs_float(EV_ABS, ABS_X, None)

    @property
    def y(self) -> float | None:
        """y coordinate"""
        return self._get_abs_float(EV_ABS, ABS_Y, None)

    @property
    def screenPos(self) -> tuple[int, int] | None:
        """screen coordinates"""
        return self._screenPos(self.x, self.y)

    @property
    def distance(self) -> float | None:
        """Pen distance from screen"""
        return self._get_abs_float(EV_ABS, ABS_DISTANCE, None)

    @property
    def pressure(self) -> float | None:
        """Pen pressure"""
        return self._get_abs_float(EV_ABS, ABS_MT_PRESSURE, None)

    @property
    def tilt(self) -> tuple[int, int]:
        """Pen tilt"""
        return (
            self._get_abs_float(EV_ABS, ABS_TILT_X, 0),
            self._get_abs_float(EV_ABS, ABS_TILT_Y, 0),
        )

    @property
    def is_down(self) -> bool:
        """If pen is touching the screen"""
        return bool(self.data.get((EV_KEY, BTN_TOUCH), 0))

    @property
    def is_hover(self) -> bool:
        """If the pen is hovering over the screen"""
        return not self.is_down and self.data.get((EV_KEY, BTN_TOOL_PEN), 0)

    @property
    def previousX(self) -> float | None:
        """Previous x coordinate"""
        return self._get_previous_abs_float(EV_ABS, ABS_X, None)

    @property
    def previousY(self) -> float | None:
        """Previous y coordinate"""
        return self._get_previous_abs_float(EV_ABS, ABS_Y, None)

    @property
    def previousScreenPos(self) -> tuple[int, int] | None:
        """Previous screen coordinates"""
        return self._screenPos(self.previousX, self.previousY)

    @property
    def previousDistance(self) -> float | None:
        """Previous distance of pen from screen"""
        return self._get_previous_abs_float(EV_ABS, ABS_DISTANCE, None)

    @property
    def previousPressure(self) -> float | None:
        """Previous pen pressure"""
        return self._get_previous_abs_float(EV_ABS, ABS_MT_PRESSURE, None)

    @property
    def previousTilt(self) -> tuple[int, int]:
        """Previous tilt of pen"""
        return (
            self._get_previous_abs_float(EV_ABS, ABS_TILT_X, 0),
            self._get_previous_abs_float(EV_ABS, ABS_TILT_Y, 0),
        )

    @property
    def was_down(self) -> bool:
        """If the pen was touching the screen in the previous event"""
        return bool(self.previousData.get((EV_KEY, BTN_TOUCH), 0))

    @property
    def was_hover(self) -> bool:
        """If the pen was hovering over the screen in the previous event"""
        return not self.was_down and self.previousData.get((EV_KEY, BTN_TOOL_PEN), 0)


class KeyEvent(Event):
    keymap: dict[int, tuple[str | None, str | None]] = DEFAULT_KEYMAP

    def __init__(self, device, state):
        super().__init__(device, state)
        # TODO - sort out key states

    def __repr__(self):
        return (
            f"KeyEvent(pressed={self.pressed or '{}'} released={self.released or '{}'}"
            f"{' press ' if self.is_press else ''}"
            f"{' release ' if self.is_release else ''}"
            f"{' repeat ' if self.is_repeat else ''}"
            f" rawEvents={len(self.rawEvents)})"
        )

    @property
    def keycode(self) -> int | None:
        """keycode that was modified this event"""
        for e in self.rawEvents:
            if e.type == EV_KEY:
                return e.code

        return None

    @property
    def pressed(self) -> set[int]:
        """Keys that were pressed"""
        keys = set()
        for k, v in self.data.items():
            if k[0] == EV_KEY and v:
                keys.add(k[1])

        return keys

    @property
    def released(self) -> set[int]:
        """Keys that were released"""
        pressed = self.pressed
        keys = set()
        for k, v in self.previousData.items():
            if k[0] == EV_KEY and v and k[1] not in pressed:
                keys.add(k[1])

        return keys

    @property
    def is_repeat(self) -> bool:
        """If this is a repeat event"""
        for e in self.rawEvents:
            if e.type == EV_KEY and e.value == 2:
                return True

        return False

    @property
    def is_press(self) -> bool:
        """If this was a press event"""
        for e in self.rawEvents:
            if e.type == EV_KEY and e.value == 1:
                return True

        return False

    @property
    def is_release(self) -> bool:
        """If this was a release event"""
        for e in self.rawEvents:
            if e.type == EV_KEY and e.value == 0:
                return True

        return False

    @property
    def is_shift(self) -> bool:
        """If shift is pressed"""
        pressed = self.pressed
        return KEY_LEFTSHIFT in pressed or KEY_RIGHTSHIFT in pressed

    @property
    def text(self) -> str | None:
        """Text representation of key pressed"""
        return self.keymap[self.keycode][int(self.is_shift)]


class Input:
    """Input API"""

    @classmethod
    def devices(cls) -> list[InputDevice]:
        """Input devices"""
        return [InputDevice(path) for path in list_devices()]

    @classmethod
    def positionDevices(cls) -> list[InputDevice]:
        """Input devices that support EV_ABS"""
        return [d for d in cls.devices() if EV_ABS in d.capabilities()]

    @classmethod
    def keyDevices(cls) -> list[InputDevice]:
        """Input devices that support EV_KEY"""
        return [
            d
            for d in cls.devices()
            if d not in cls.positionDevices() and EV_KEY in d.capabilities()
        ]

    @classmethod
    def touchDevices(cls) -> list[InputDevice]:
        """Input devices that support multitouch"""
        return [d for d in cls.positionDevices() if d.absinfo(ABS_MT_TRACKING_ID).max]

    @classmethod
    def wacomDevices(cls) -> list[InputDevice]:
        """Input devices that use a stylus"""
        return [
            d
            for d in cls.positionDevices()
            if d not in cls.touchDevices() and BTN_STYLUS in d.capabilities()[EV_KEY]
        ]

    @classmethod
    def deviceType(cls, device: InputDevice) -> str:
        """Gets the string representation of the device type for an input device

        :returns: key, wacom, touch, or unknown"""
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
        """Get the raw events for input devices

        :param devices: Optional list of devices to listen to
        :param block: If listening should block until events are recieved. If you are not blocking, you will recieve an empty event every 100ms if no event happens
        :return: Generator of events
        """
        selector = DefaultSelector()
        for device in devices if devices is not None else cls.devices():
            selector.register(device, EVENT_READ)

        events = {}
        while True:
            try:
                for key, mask in selector.select(timeout=100 if block else 0):
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

                # TODO - don't require another input event to register when a keyboard has been added again
                if devices is None:
                    # Add any newly added devices if we aren't filtering to a specific set of events
                    for device in cls.devices():
                        if device not in [
                            k.fileobj for k in selector.get_map().values()
                        ]:
                            selector.register(device, EVENT_READ)

            except OSError as err:
                if err.errno != ENODEV:
                    raise

                selector.unregister(device)

            if not block:
                yield None, []

    @classmethod
    def rawPositionEvents(
        cls, block: bool = False
    ) -> Iterator[tuple[InputDevice, InputEvent] | tuple[None, None]]:
        """Get the raw events for position input devices

        :param block: If listening should block until events are recieved. If you are not blocking, you will recieve an empty event every 100ms if no event happens
        :return: Generator of events"""
        for d, e in cls.rawEvents(cls.positionDevices(), block=block):
            yield d, e

    @classmethod
    def rawTouchEvents(
        cls, block: bool = False
    ) -> Iterator[tuple[InputDevice, InputEvent] | tuple[None, None]]:
        """Get the raw events for touch input devices

        :param block: If listening should block until events are recieved. If you are not blocking, you will recieve an empty event every 100ms if no event happens
        :return: Generator of events"""
        for d, e in cls.rawEvents(cls.touchDevices(), block=block):
            yield d, e

    @classmethod
    def rawWacomEvents(
        cls, block: bool = False
    ) -> Iterator[tuple[InputDevice, InputEvent] | tuple[None, None]]:
        """Get the raw events for tablet input devices

        :param block: If listening should block until events are recieved. If you are not blocking, you will recieve an empty event every 100ms if no event happens
        :return: Generator of events"""
        for d, e in cls.rawEvents(cls.wacomDevices(), block=block):
            yield d, e

    @classmethod
    def rawKeyEvents(
        cls, block: bool = False
    ) -> Iterator[tuple[InputDevice, InputEvent] | tuple[None, None]]:
        """Get the raw events for key input devices

        :param block: If listening should block until events are recieved. If you are not blocking, you will recieve an empty event every 100ms if no event happens
        :return: Generator of events"""
        for d, e in cls.rawEvents(cls.keyDevices(), block=block):
            yield d, e

    @classmethod
    def _event(cls, device: InputDevice, state: dict) -> Event:
        if state["type"] == "touch":
            return TouchEvent(device, state)

        if state["type"] == "wacom":
            return WacomEvent(device, state)

        if state["type"] == "key":
            return KeyEvent(device, state)

        return Event(device, state)

    @classmethod
    def events(cls, block: bool = False) -> Iterator[Event | None]:
        """Listen for input events

        :param block: If listening should block until events are recieved. If you are not blocking, you will recieve an empty event every 100ms if no event happens
        :return: Generator of events"""
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
                    "slot": 0,
                }

            state = states[d.path]

            for e in events:
                if e.type == EV_SYN and e.code in (SYN_REPORT, SYN_MT_REPORT):
                    yield cls._event(d, state)
                    state["events"] = []
                    state["previous"] = deepcopy(state["current"])
                    continue

                current = state["current"]
                if e.type == EV_ABS and e.code == ABS_MT_SLOT:
                    if state["events"]:
                        yield cls._event(d, state)
                        state["events"] = []
                        state["previous"] = deepcopy(state["current"])

                    state["slot"] = e.value

                state["events"].append(e)
                if state["slot"] not in current.keys():
                    current[state["slot"]] = {}

                current[state["slot"]][(e.type, e.code)] = e.value
                continue
