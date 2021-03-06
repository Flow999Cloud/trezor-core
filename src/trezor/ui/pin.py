from micropython import const
from trezor import ui
from trezor.crypto import random
from trezor.ui import display
from trezor.ui.button import Button, BTN_CLICKED


def digit_area(i):
    if i == 9:  # 0-position
        i = 10  # display it in the middle
    return ui.grid(i + 3)  # skip the first line


def generate_digits(with_zero):
    if with_zero:
        digits = list(range(0, 10))  # 0-9
    else:
        digits = list(range(1, 10))  # 1-9
    random.shuffle(digits)
    return digits


class PinMatrix(ui.Widget):

    def __init__(self, label, pin='', maxlength=9, with_zero=False):
        self.label = label
        self.pin = pin
        self.maxlength = maxlength
        self.digits = generate_digits(with_zero)

        # we lay out the buttons top-left to bottom-right, but the order of the
        # digits is defined as bottom-left to top-right (on numpad)
        reordered_digits = self.digits[6:] + self.digits[3:6] + self.digits[:3]

        self.pin_buttons = [Button(digit_area(i), str(d))
                            for i, d in enumerate(reordered_digits)]
        self.onchange = None

    def render(self):
        # clear canvas under input line
        display.bar(0, 0, 240, 45, ui.BG)

        # input line with a header
        header = '*' * len(self.pin) if self.pin else self.label
        display.text_center(120, 36, header, ui.BOLD, ui.GREY, ui.BG)

        # pin matrix buttons
        for btn in self.pin_buttons:
            btn.render()

    def touch(self, event, pos):
        for btn in self.pin_buttons:
            if btn.touch(event, pos) == BTN_CLICKED:
                if len(self.pin) < self.maxlength:
                    self.change(self.pin + btn.content)
                break

    def change(self, pin):
        self.pin = pin
        if self.onchange:
            self.onchange()
