import evdev

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
