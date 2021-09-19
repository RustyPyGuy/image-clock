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
Signal Handler for image clock.
USE:
insert some directions here.

TEST:
just run this python file.  Adjust the frame rate at the end of the file. 30
fps works well for most applications.
"""

__author__ = "RustyPyGuy"
__version__ = "0.0.0"

import signal
import platform
# if __name__ != "__main__":
#     from __main__ import file_cat, LC  # specific variables in the clock_main.py file
#    from clock_main0_7 import file_cat, LC


class SignalHandler():
    """ This class handles signal events from the system for the image clock
    Current signals supported:
    10 SIGUSR1 - re-scans and reloads the image directory
    """

    def __init__(self, callback10, callback12, test=False):
        # NOTE: quick hack to prevent code from running in Windows due to lack of these signals support
        if platform.system() != 'Windows':
            signal.signal(signal.SIGUSR1, self._sigusr1)
            signal.signal(signal.SIGUSR2, self._sigusr2)
            self.callback10 = callback10
            self.callback12 = callback12
    #        signal.signal(signal.SIGTERM, handler)
            self.test = test

    def _sigusr1(self, one, two):  # signal used to recsan
        if one == 10 and self.test is False:
            print(
                "signal 10 SIGUSR1 received. Re-scanning image directory and re-initializing clock.")
            self.callback10()
        elif one == 10 and self.test is True:
            print("signal 10 SIGUSR1 received. Test Mode. No further action.")
            self.callback10()

    def _sigusr2(self, one, two):
        if one == 12 and self.test is False:
            print("signal 12 SIGUSR2 received. Doing something.")
            self.callback12()
            # execute functions to rescan everything
        elif one == 12 and self.test is True:
            print("signal 12 SIGUSR2 received. Test Mode. No further action.")
            self.callback12()


if __name__ == "__main__":
    """ This is executed when run from the command line """
    import time
    import os
    def signal10():
        """simple test function to test the callback"""
        print("function signal10 callback executed.")
    def signal12():
        """simple test function to test the callback"""
        print("function signal12 callback executed.")
    print(
        "Initiating signal handler test\nSend system signals to process",
        os.getpid())
    sig = SignalHandler(signal10,signal12,True)
    done = 0
    while(not done):
        time.sleep(1)
