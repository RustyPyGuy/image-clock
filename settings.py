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
This file contains the default settings for the image clock and loads settings
from a config file.

TODO:
convert string to tuple
add some catch except statments

"""
import configparser
import os
import argparse

# some stackoverflow example
# def parse_tuple(string):
#     try:
#         s = eval(string)
#         if type(s) == tuple:
#             return s
#         return
#     except:
#         return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The settings module for the image clock")
    parser.add_argument('-w','--write_new', action='store_true', help='Write new config file based on internal defaults.')
    args = parser.parse_args()
else:
    # args.write_new = False
    pass
config = configparser.ConfigParser()

try:
    for config_file_path in ['~/image-clock/image-clock.ini',
                        './image-clock/image-clock.ini',
                        './image-clock.ini']:
        if os.path.isfile(config_file_path) is True:
            break
        else:
            config_file_path = ''
except:
    pass
else:
    pass

# Set the default values.  These will be written in a file write operation or read
# in a file read operation and overwritten.
# NOTE: need to figure out how the overwriting works.
config['GENERAL'] = {'FRAME_RATE': '30',
                     'SCREEN_SLEEP_MINUTES': '8'}
config['ANALOG_CLOCK'] = {'MARGIN':'150',
                          'STYLE':'DE'}
config['TEXT_OVERLAY'] = {'STYLE':'SIMPLE',
                          'COLOR':'(128,0,0)',
                          'SIZE':'10',
                          'FADE_TIME':'20',
                          'TRANSITION_TIME':'20'}

if 'args' in globals():
    if args.write_new is True and config_file_path != '':
        # config.write(config_file_path)
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)
        # breakpoint()
if config_file_path != '':
    # config.read(config_file_path)
    with open(config_file_path, 'r') as configfile:
        config.read(configfile)
        # breakpoint()
else:
    Exception('No config file present to read or write.')

# Rename config settings for ease of reference elsewhere in the project files
#NOTE: consider assigning by copy() if the reference is CPU costly.
FRAME_RATE = int(config['GENERAL']['FRAME_RATE']) # NOTE as currently written will be overriden by argparse default
SCREEN_SLEEP_MINUTES = int(config['GENERAL']['SCREEN_SLEEP_MINUTES'])
TYPE_COLOR = (128,0,0) # Color of font overlay fading text
TIME_FONT_PERCENT = int(config['TEXT_OVERLAY']['SIZE']) #height of time font as percent of display size
FADE_SECONDS = int(config['TEXT_OVERLAY']['FADE_TIME']) # Number of seconds for font fading
TRANSITION_TIME = int(config['TEXT_OVERLAY']['TRANSITION_TIME']) # Number of seconds for font fading
ANALOG_CLOCK_MARGIN = int(config['ANALOG_CLOCK']['MARGIN'])

