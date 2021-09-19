#!/usr/bin/env python3

# The Image Clock, a python clock that displays artwork to tell the time, and its
# component and supporting files (analog clock, file parser, and others)
# Copyright (C) 2021 github user: RustyPyGuy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# To contact the author: send a message to RustyPyGuy on Github.

"""
Standalone program to blank the display of a Raspberry Pi based on input from a
GPIO pin. This may be used independently, but designed to be used in
conjunction with a PIR and the image clock.

depends on settings.py for the minutes variable.
"""

# Set GPIO input. This depends on what you actually plugged it to.
GPIO_INPUT = 24

import time
import settings as s
#from subprocess import call, run, locals
from subprocess import *
from datetime import datetime
import RPi.GPIO as GPIO # NOTE: This module will not build on a x86 AFAIK. Linter error.

# countdown for sleep in seconds
COUNTDOWN_START = s.SCREEN_SLEEP_MINUTES * 60

# prepare GPIO monitoring NOTE: only may be tested on native hardware
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN)
print("Starting monitoring of PIR")
sleep_increment = 0.1
timer = float(COUNTDOWN_START)

while True:
    i = GPIO.input(GPIO_INPUT)
    if i == 0:
#        print("Screen off", i)
        timer = round(timer - sleep_increment, 2) 
        if timer <= sleep_increment and timer >= 0:
            print("Timer Expired. Screen off. time:",  datetime.now())
            run(["/usr/bin/vcgencmd", "display_power", "0"], stdout = DEVNULL)
        elif timer < 0:
            run(["/usr/bin/vcgencmd", "display_power", "0"], stdout = DEVNULL)

    elif i == 1:
        if timer != COUNTDOWN_START:
            print("Motion Detected at timer interval:", timer, \
                  "Screen on. Timer reset to:", COUNTDOWN_START, "time:",  datetime.now())
        timer = COUNTDOWN_START
        call(["/usr/bin/vcgencmd", "display_power", "1"], stdout = DEVNULL)
    time.sleep(sleep_increment)
