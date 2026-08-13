#!/usr/bin/env python3
"""Send Ctrl+Shift+V via evdev/uinput."""
import sys
from evdev import UInput, ecodes

def paste():
    events = {
        ecodes.EV_KEY: [ecodes.KEY_LEFTCTRL, ecodes.KEY_LEFTSHIFT, ecodes.KEY_V]
    }
    with UInput(events, "dictate-paste") as ui:
        for c in events[ecodes.EV_KEY]:
            ui.write(ecodes.EV_KEY, c, 1)  # press
        ui.syn()
        import time
        time.sleep(0.05)
        for c in reversed(events[ecodes.EV_KEY]):
            ui.write(ecodes.EV_KEY, c, 0)  # release
        ui.syn()

if __name__ == "__main__":
    paste()
