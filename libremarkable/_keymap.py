from evdev.ecodes import *

keymap = {
    KEY_0: ("0", ")"),
    KEY_1: ("1", "!"),
    KEY_102ND: (None, None),
    KEY_10CHANNELSDOWN: (None, None),
    KEY_10CHANNELSUP: (None, None),
    KEY_2: ("2", "@"),
    KEY_3: ("3", "#"),
    KEY_3D_MODE: (None, None),
    KEY_4: ("4", "$"),
    KEY_5: ("5", "%"),
    KEY_6: ("6", "^"),
    KEY_7: ("7", "&"),
    KEY_8: ("8", "*"),
    KEY_9: ("9", "("),
    KEY_A: ("a", "A"),
    KEY_AB: (None, None),
    KEY_ADDRESSBOOK: (None, None),
    KEY_AGAIN: (None, None),
    KEY_ALS_TOGGLE: (None, None),
    KEY_ALTERASE: (None, None),
    KEY_ANGLE: (None, None),
    KEY_APOSTROPHE: ("'", '"'),
    KEY_APPSELECT: (None, None),
    KEY_ARCHIVE: (None, None),
    KEY_ASPECT_RATIO: (None, None),
    KEY_ASSISTANT: (None, None),
    KEY_ATTENDANT_OFF: (None, None),
    KEY_ATTENDANT_ON: (None, None),
    KEY_ATTENDANT_TOGGLE: (None, None),
    KEY_AUDIO: (None, None),
    KEY_AUDIO_DESC: (None, None),
    KEY_AUX: (None, None),
    KEY_B: ("b", "B"),
    KEY_BACK: (None, None),
    KEY_BACKSLASH: ("\\", "|"),
    KEY_BACKSPACE: ("\b", "\b"),
    KEY_BASSBOOST: (None, None),
    KEY_BATTERY: (None, None),
    KEY_BLUE: (None, None),
    KEY_BLUETOOTH: (None, None),
    KEY_BOOKMARKS: (None, None),
    KEY_BREAK: (None, None),
    KEY_BRIGHTNESSDOWN: (None, None),
    KEY_BRIGHTNESSUP: (None, None),
    KEY_BRIGHTNESS_AUTO: (None, None),
    KEY_BRIGHTNESS_CYCLE: (None, None),
    KEY_BRIGHTNESS_MAX: (None, None),
    KEY_BRIGHTNESS_MIN: (None, None),
    KEY_BRIGHTNESS_TOGGLE: (None, None),
    KEY_BRIGHTNESS_ZERO: (None, None),
    KEY_BRL_DOT1: (None, None),
    KEY_BRL_DOT10: (None, None),
    KEY_BRL_DOT2: (None, None),
    KEY_BRL_DOT3: (None, None),
    KEY_BRL_DOT4: (None, None),
    KEY_BRL_DOT5: (None, None),
    KEY_BRL_DOT6: (None, None),
    KEY_BRL_DOT7: (None, None),
    KEY_BRL_DOT8: (None, None),
    KEY_BRL_DOT9: (None, None),
    KEY_BUTTONCONFIG: (None, None),
    KEY_C: ("c", "C"),
    KEY_CALC: (None, None),
    KEY_CALENDAR: (None, None),
    KEY_CAMERA: (None, None),
    KEY_CAMERA_DOWN: (None, None),
    KEY_CAMERA_FOCUS: (None, None),
    KEY_CAMERA_LEFT: (None, None),
    KEY_CAMERA_RIGHT: (None, None),
    KEY_CAMERA_UP: (None, None),
    KEY_CAMERA_ZOOMIN: (None, None),
    KEY_CAMERA_ZOOMOUT: (None, None),
    KEY_CANCEL: (None, None),
    KEY_CAPSLOCK: (None, None),
    KEY_CD: (None, None),
    KEY_CHANNEL: (None, None),
    KEY_CHANNELDOWN: (None, None),
    KEY_CHANNELUP: (None, None),
    KEY_CHAT: (None, None),
    KEY_CLEAR: (None, None),
    KEY_CLOSE: (None, None),
    KEY_CLOSECD: (None, None),
    KEY_CNT: (None, None),
    KEY_COFFEE: (None, None),
    KEY_COMMA: (",", "<"),
    KEY_COMPOSE: (None, None),
    KEY_COMPUTER: (None, None),
    KEY_CONFIG: (None, None),
    KEY_CONNECT: (None, None),
    KEY_CONTEXT_MENU: (None, None),
    KEY_CONTROLPANEL: (None, None),
    KEY_COPY: (None, None),
    KEY_CUT: (None, None),
    KEY_CYCLEWINDOWS: (None, None),
    KEY_D: ("d", "D"),
    KEY_DASHBOARD: (None, None),
    KEY_DATA: (None, None),
    KEY_DATABASE: (None, None),
    KEY_DELETE: (None, None),
    KEY_DELETEFILE: (None, None),
    KEY_DEL_EOL: (None, None),
    KEY_DEL_EOS: (None, None),
    KEY_DEL_LINE: (None, None),
    KEY_DIGITS: (None, None),
    KEY_DIRECTION: (None, None),
    KEY_DIRECTORY: (None, None),
    KEY_DISPLAYTOGGLE: (None, None),
    KEY_DISPLAY_OFF: (None, None),
    KEY_DOCUMENTS: (None, None),
    KEY_DOLLAR: (None, None),
    KEY_DOT: (".", ">"),
    KEY_DOWN: (None, None),
    KEY_DVD: (None, None),
    KEY_E: ("e", "E"),
    KEY_EDIT: (None, None),
    KEY_EDITOR: (None, None),
    KEY_EJECTCD: (None, None),
    KEY_EJECTCLOSECD: (None, None),
    KEY_EMAIL: (None, None),
    KEY_END: (None, None),
    KEY_ENTER: ("\n", "\n"),
    KEY_EPG: (None, None),
    KEY_EQUAL: ("=", "+"),
    KEY_ESC: (None, None),
    KEY_EURO: (None, None),
    KEY_EXIT: (None, None),
    KEY_F: ("f", "F"),
    KEY_F1: (None, None),
    KEY_F10: (None, None),
    KEY_F11: (None, None),
    KEY_F12: (None, None),
    KEY_F13: (None, None),
    KEY_F14: (None, None),
    KEY_F15: (None, None),
    KEY_F16: (None, None),
    KEY_F17: (None, None),
    KEY_F18: (None, None),
    KEY_F19: (None, None),
    KEY_F2: (None, None),
    KEY_F20: (None, None),
    KEY_F21: (None, None),
    KEY_F22: (None, None),
    KEY_F23: (None, None),
    KEY_F24: (None, None),
    KEY_F3: (None, None),
    KEY_F4: (None, None),
    KEY_F5: (None, None),
    KEY_F6: (None, None),
    KEY_F7: (None, None),
    KEY_F8: (None, None),
    KEY_F9: (None, None),
    KEY_FASTFORWARD: (None, None),
    KEY_FASTREVERSE: (None, None),
    KEY_FAVORITES: (None, None),
    KEY_FILE: (None, None),
    KEY_FINANCE: (None, None),
    KEY_FIND: (None, None),
    KEY_FIRST: (None, None),
    KEY_FN: (None, None),
    KEY_FN_1: (None, None),
    KEY_FN_2: (None, None),
    KEY_FN_B: (None, None),
    KEY_FN_D: (None, None),
    KEY_FN_E: (None, None),
    KEY_FN_ESC: (None, None),
    KEY_FN_F: (None, None),
    KEY_FN_F1: (None, None),
    KEY_FN_F10: (None, None),
    KEY_FN_F11: (None, None),
    KEY_FN_F12: (None, None),
    KEY_FN_F2: (None, None),
    KEY_FN_F3: (None, None),
    KEY_FN_F4: (None, None),
    KEY_FN_F5: (None, None),
    KEY_FN_F6: (None, None),
    KEY_FN_F7: (None, None),
    KEY_FN_F8: (None, None),
    KEY_FN_F9: (None, None),
    KEY_FN_S: (None, None),
    KEY_FORWARD: (None, None),
    KEY_FORWARDMAIL: (None, None),
    KEY_FRAMEBACK: (None, None),
    KEY_FRAMEFORWARD: (None, None),
    KEY_FRONT: (None, None),
    KEY_FULL_SCREEN: (None, None),
    KEY_G: ("g", "G"),
    KEY_GAMES: (None, None),
    KEY_GOTO: (None, None),
    KEY_GRAPHICSEDITOR: (None, None),
    KEY_GRAVE: ("`", "~"),
    KEY_GREEN: (None, None),
    KEY_H: ("h", "H"),
    KEY_HANGEUL: (None, None),
    KEY_HANGUEL: (None, None),
    KEY_HANJA: (None, None),
    KEY_HELP: (None, None),
    KEY_HENKAN: (None, None),
    KEY_HIRAGANA: (None, None),
    KEY_HOME: (None, None),
    KEY_HOMEPAGE: (None, None),
    KEY_HP: (None, None),
    KEY_I: ("i", "I"),
    KEY_IMAGES: (None, None),
    KEY_INFO: (None, None),
    KEY_INSERT: (None, None),
    KEY_INS_LINE: (None, None),
    KEY_ISO: (None, None),
    KEY_J: ("j", "J"),
    KEY_JOURNAL: (None, None),
    KEY_K: ("k", "K"),
    KEY_KATAKANA: (None, None),
    KEY_KATAKANAHIRAGANA: (None, None),
    KEY_KBDILLUMDOWN: (None, None),
    KEY_KBDILLUMTOGGLE: (None, None),
    KEY_KBDILLUMUP: (None, None),
    KEY_KBDINPUTASSIST_ACCEPT: (None, None),
    KEY_KBDINPUTASSIST_CANCEL: (None, None),
    KEY_KBDINPUTASSIST_NEXT: (None, None),
    KEY_KBDINPUTASSIST_NEXTGROUP: (None, None),
    KEY_KBDINPUTASSIST_PREV: (None, None),
    KEY_KBDINPUTASSIST_PREVGROUP: (None, None),
    KEY_KBD_LAYOUT_NEXT: (None, None),
    KEY_KEYBOARD: (None, None),
    KEY_KP0: (None, None),
    KEY_KP1: (None, None),
    KEY_KP2: (None, None),
    KEY_KP3: (None, None),
    KEY_KP4: (None, None),
    KEY_KP5: (None, None),
    KEY_KP6: (None, None),
    KEY_KP7: (None, None),
    KEY_KP8: (None, None),
    KEY_KP9: (None, None),
    KEY_KPASTERISK: (None, None),
    KEY_KPCOMMA: (None, None),
    KEY_KPDOT: (None, None),
    KEY_KPENTER: (None, None),
    KEY_KPEQUAL: (None, None),
    KEY_KPJPCOMMA: (None, None),
    KEY_KPLEFTPAREN: (None, None),
    KEY_KPMINUS: (None, None),
    KEY_KPPLUS: (None, None),
    KEY_KPPLUSMINUS: (None, None),
    KEY_KPRIGHTPAREN: (None, None),
    KEY_KPSLASH: (None, None),
    KEY_L: ("l", "L"),
    KEY_LANGUAGE: (None, None),
    KEY_LAST: (None, None),
    KEY_LEFT: (None, None),
    KEY_LEFTALT: (None, None),
    KEY_LEFTBRACE: (None, None),
    KEY_LEFTCTRL: (None, None),
    KEY_LEFTMETA: (None, None),
    KEY_LEFTSHIFT: (None, None),
    KEY_LEFT_DOWN: (None, None),
    KEY_LEFT_UP: (None, None),
    KEY_LIGHTS_TOGGLE: (None, None),
    KEY_LINEFEED: (None, None),
    KEY_LIST: (None, None),
    KEY_LOGOFF: (None, None),
    KEY_M: ("m", "M"),
    KEY_MACRO: (None, None),
    KEY_MAIL: (None, None),
    KEY_MAX: (None, None),
    KEY_MEDIA: (None, None),
    KEY_MEDIA_REPEAT: (None, None),
    KEY_MEDIA_TOP_MENU: (None, None),
    KEY_MEMO: (None, None),
    KEY_MENU: (None, None),
    KEY_MESSENGER: (None, None),
    KEY_MHP: (None, None),
    KEY_MICMUTE: (None, None),
    KEY_MINUS: ("-", "_"),
    KEY_MIN_INTERESTING: (None, None),
    KEY_MODE: (None, None),
    KEY_MOVE: (None, None),
    KEY_MP3: (None, None),
    KEY_MSDOS: (None, None),
    KEY_MUHENKAN: (None, None),
    KEY_MUTE: (None, None),
    KEY_N: ("n", "N"),
    KEY_NEW: (None, None),
    KEY_NEWS: (None, None),
    KEY_NEXT: (None, None),
    KEY_NEXTSONG: (None, None),
    KEY_NEXT_FAVORITE: (None, None),
    KEY_NUMERIC_0: (None, None),
    KEY_NUMERIC_1: (None, None),
    KEY_NUMERIC_11: (None, None),
    KEY_NUMERIC_12: (None, None),
    KEY_NUMERIC_2: (None, None),
    KEY_NUMERIC_3: (None, None),
    KEY_NUMERIC_4: (None, None),
    KEY_NUMERIC_5: (None, None),
    KEY_NUMERIC_6: (None, None),
    KEY_NUMERIC_7: (None, None),
    KEY_NUMERIC_8: (None, None),
    KEY_NUMERIC_9: (None, None),
    KEY_NUMERIC_A: (None, None),
    KEY_NUMERIC_B: (None, None),
    KEY_NUMERIC_C: (None, None),
    KEY_NUMERIC_D: (None, None),
    KEY_NUMERIC_POUND: (None, None),
    KEY_NUMERIC_STAR: (None, None),
    KEY_NUMLOCK: (None, None),
    KEY_O: ("o", "O"),
    KEY_OK: (None, None),
    KEY_ONSCREEN_KEYBOARD: (None, None),
    KEY_OPEN: (None, None),
    KEY_OPTION: (None, None),
    KEY_P: ("p", "P"),
    KEY_PAGEDOWN: (None, None),
    KEY_PAGEUP: (None, None),
    KEY_PASTE: (None, None),
    KEY_PAUSE: (None, None),
    KEY_PAUSECD: (None, None),
    KEY_PAUSE_RECORD: (None, None),
    KEY_PC: (None, None),
    KEY_PHONE: (None, None),
    KEY_PLAY: (None, None),
    KEY_PLAYCD: (None, None),
    KEY_PLAYER: (None, None),
    KEY_PLAYPAUSE: (None, None),
    KEY_POWER: (None, None),
    KEY_POWER2: (None, None),
    KEY_PRESENTATION: (None, None),
    KEY_PREVIOUS: (None, None),
    KEY_PREVIOUSSONG: (None, None),
    KEY_PRINT: (None, None),
    KEY_PROG1: (None, None),
    KEY_PROG2: (None, None),
    KEY_PROG3: (None, None),
    KEY_PROG4: (None, None),
    KEY_PROGRAM: (None, None),
    KEY_PROPS: (None, None),
    KEY_PVR: (None, None),
    KEY_Q: ("q", "Q"),
    KEY_QUESTION: (None, None),
    KEY_R: ("r", "R"),
    KEY_RADIO: (None, None),
    KEY_RECORD: (None, None),
    KEY_RED: (None, None),
    KEY_REDO: (None, None),
    KEY_REFRESH: (None, None),
    KEY_REPLY: (None, None),
    KEY_RESERVED: (None, None),
    KEY_RESTART: (None, None),
    KEY_REWIND: (None, None),
    KEY_RFKILL: (None, None),
    KEY_RIGHT: (None, None),
    KEY_RIGHTALT: (None, None),
    KEY_RIGHTBRACE: (None, None),
    KEY_RIGHTCTRL: (None, None),
    KEY_RIGHTMETA: (None, None),
    KEY_RIGHTSHIFT: (None, None),
    KEY_RIGHT_DOWN: (None, None),
    KEY_RIGHT_UP: (None, None),
    KEY_RO: (None, None),
    KEY_ROOT_MENU: (None, None),
    KEY_ROTATE_DISPLAY: (None, None),
    KEY_ROTATE_LOCK_TOGGLE: (None, None),
    KEY_S: ("s", "S"),
    KEY_SAT: (None, None),
    KEY_SAT2: (None, None),
    KEY_SAVE: (None, None),
    KEY_SCALE: (None, None),
    KEY_SCREEN: (None, None),
    KEY_SCREENLOCK: (None, None),
    KEY_SCREENSAVER: (None, None),
    KEY_SCROLLDOWN: (None, None),
    KEY_SCROLLLOCK: (None, None),
    KEY_SCROLLUP: (None, None),
    KEY_SEARCH: (None, None),
    KEY_SELECT: (None, None),
    KEY_SEMICOLON: (";", ":"),
    KEY_SEND: (None, None),
    KEY_SENDFILE: (None, None),
    KEY_SETUP: (None, None),
    KEY_SHOP: (None, None),
    KEY_SHUFFLE: (None, None),
    KEY_SLASH: ("/", "?"),
    KEY_SLEEP: (None, None),
    KEY_SLOW: (None, None),
    KEY_SLOWREVERSE: (None, None),
    KEY_SOUND: (None, None),
    KEY_SPACE: (" ", " "),
    KEY_SPELLCHECK: (None, None),
    KEY_SPORT: (None, None),
    KEY_SPREADSHEET: (None, None),
    KEY_STOP: (None, None),
    KEY_STOPCD: (None, None),
    KEY_STOP_RECORD: (None, None),
    KEY_SUBTITLE: (None, None),
    KEY_SUSPEND: (None, None),
    KEY_SWITCHVIDEOMODE: (None, None),
    KEY_SYSRQ: (None, None),
    KEY_T: ("t", "T"),
    KEY_TAB: ("\t", "\t"),
    KEY_TAPE: (None, None),
    KEY_TASKMANAGER: (None, None),
    KEY_TEEN: (None, None),
    KEY_TEXT: (None, None),
    KEY_TIME: (None, None),
    KEY_TITLE: (None, None),
    KEY_TOUCHPAD_OFF: (None, None),
    KEY_TOUCHPAD_ON: (None, None),
    KEY_TOUCHPAD_TOGGLE: (None, None),
    KEY_TUNER: (None, None),
    KEY_TV: (None, None),
    KEY_TV2: (None, None),
    KEY_TWEN: (None, None),
    KEY_U: ("u", "U"),
    KEY_UNDO: (None, None),
    KEY_UNKNOWN: (None, None),
    KEY_UNMUTE: (None, None),
    KEY_UP: (None, None),
    KEY_UWB: (None, None),
    KEY_V: ("v", "V"),
    KEY_VCR: (None, None),
    KEY_VCR2: (None, None),
    KEY_VENDOR: (None, None),
    KEY_VIDEO: (None, None),
    KEY_VIDEOPHONE: (None, None),
    KEY_VIDEO_NEXT: (None, None),
    KEY_VIDEO_PREV: (None, None),
    KEY_VOD: (None, None),
    KEY_VOICECOMMAND: (None, None),
    KEY_VOICEMAIL: (None, None),
    KEY_VOLUMEDOWN: (None, None),
    KEY_VOLUMEUP: (None, None),
    KEY_W: ("w", "W"),
    KEY_WAKEUP: (None, None),
    KEY_WIMAX: (None, None),
    KEY_WLAN: (None, None),
    KEY_WORDPROCESSOR: (None, None),
    KEY_WPS_BUTTON: (None, None),
    KEY_WWAN: (None, None),
    KEY_WWW: (None, None),
    KEY_X: ("x", "X"),
    KEY_XFER: (None, None),
    KEY_Y: ("y", "Y"),
    KEY_YELLOW: (None, None),
    KEY_YEN: (None, None),
    KEY_Z: ("z", "Z"),
    KEY_ZENKAKUHANKAKU: (None, None),
    KEY_ZOOM: (None, None),
    KEY_ZOOMIN: (None, None),
    KEY_ZOOMOUT: (None, None),
    KEY_ZOOMRESET: (None, None),
}
