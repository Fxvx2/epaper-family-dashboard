"""Display abstraction: PNG output (Mac/dev) or real e-paper (Pi)."""

import sys
import time
import platform
import os
from PIL import Image

# Display dimensions for 9.7" Waveshare e-Paper
WIDTH = 1200
HEIGHT = 825

_screen_counter = 0


class PNGDisplay:
    """Virtual display that saves to PNG files for development."""

    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width = width
        self.height = height
        self.frame_buf = Image.new('L', (width, height), 0xFF)

    def draw_full(self, mode=None):
        global _screen_counter
        _screen_counter += 1
        path = os.path.join('cache', 'screen_{}.png'.format(_screen_counter))
        self.frame_buf.save(path)
        print("Saved: {} ({}x{})".format(path, self.width, self.height))

    def draw_partial(self, mode=None):
        self.draw_full(mode)

    def clear(self):
        self.frame_buf.paste(0xFF, box=(0, 0, self.width, self.height))
        self.draw_full()


def create_display(virtual=False, vcom=-2.06):
    """Create the appropriate display instance.

    On Mac or with --virtual flag: PNGDisplay (saves screenshots).
    On Pi: AutoEPDDisplay (real IT8951 hardware).
    """
    if virtual or platform.system() == 'Darwin':
        return _create_virtual()
    return _create_real(vcom)


def _create_virtual():
    os.makedirs('cache', exist_ok=True)
    print("Using PNG display ({}x{}) -- output in cache/".format(WIDTH, HEIGHT))
    return PNGDisplay(WIDTH, HEIGHT)


def _create_real(vcom):
    try:
        from IT8951.display import AutoEPDDisplay
        print("Using real e-Paper display (vcom={})".format(vcom))
        display = AutoEPDDisplay(vcom=vcom)
        print("Display size: {}x{}".format(display.width, display.height))
        return display
    except (ImportError, RuntimeError) as e:
        print("Cannot initialize real display: {}".format(e))
        print("Falling back to PNG display")
        return _create_virtual()


def show(display, mode=None):
    """Push frame_buf to the display."""
    if mode is None and not isinstance(display, PNGDisplay):
        from IT8951.constants import DisplayModes
        mode = DisplayModes.GC16
    display.draw_full(mode)


def smart_sleep(display, seconds):
    """Sleep (no Tkinter needed with PNG mode)."""
    time.sleep(seconds)
