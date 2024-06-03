from ctypes import CDLL

libc = CDLL("libc.so.6", use_errno=True)
msgsnd = libc.msgsnd
msgget = libc.msgget
