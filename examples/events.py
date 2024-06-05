from libremarkable import Input

for event in Input.events(block=True):
    print(event)
