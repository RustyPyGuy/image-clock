# The Image Clock
*A clock that displays a new named image every minute. Powered by pygame and a photography project*

## Description
The Image clock is a combination photography and programming project to learn Python and PyGame.  The concept is that there is a running clock that rotates the displayed image once per minute to indicate the time.  The original idea is to use a series of photographs of other clocks to display the time.  In total, for a unique image every minute, this would require 1,440 images.  When there is no image for the minute being displayed, the image clock with display an analog clock that looks similar to a German train clock, all rendered in PyGame.  This clock is intended to be run on a Raspberry Pi as a standalone clock, but will execute in a window or fullscreen on a Linux or Windows desktop.

And one other thing.  I wrote this while learning python.  You will probably see programming habits of a procedural programmer learning switch to OOP principles, and maybe some rookie mistakes.

## Execution Status
Successfully runs after significant configuration of data file directories and font downloads.

## System Requirements
* Python 3.x (need to check exact version)
* Pygame 1.9 or higher (need to check exact verion)
* for automated screen control, Raspberry Pi OS.
* Approximately 800 MB available RAM for a fullscreen display with HD display resolution.  The analog clock pre-renders all frames to memory.  Raspberry Pi 3/4 are powerful enough.  Pi Zero definitely not.

## Usage
* This software requires significant configuration.  Namely, downloading and installing fonts, and providing images. Future versions should have something to run immediately.
* Place image files in `/var/lib/image-clock/images/` the specified directory for your OS using the naming convention. This project does not include images, but I may include a few sample images in the future.  
* Download fonts _Indulta_ and _Plat Nomor_. Install fonts to `/var/lib/image-clock/fonts/` For now, check the source file for the font names. I'll add that here later.
* Configure the `image-clock.ini` file and the `settings.py` file.
* execute `clock_main.py` to run the main program and display to an X session or to the Windows desktop.
* Execute  `clock_main.py --help` to see a list of options. 
* To execute on an X display fullscreen and silence all terminal messages and detatch the execution, such as  in a startup script: `DISPLAY=":0" /usr/bin/env python3 ./clock_main.py -f > /dev/null 2>&1 & disown` Adjust program location to suit.

### Image file naming convention
All image files must be named with a specificed naming convention in any sub directory of the root image file location.

The first 6 characters of the filename must meet the following format:
* `X1234Yfancy_clock name.jpg`
* where `X` must be `A, P, or E` for AM, PM, or either.
* `1234` must be a valid 4-digit hour and minute time. P1200 is 12 noon, midday. A1200 is 12 midnight. It may also be A0000. PM clocks may use either 24 or 12 hour time notation.
* `Y` is a reserved field. It is not currently used, but reserved for the future. It is recommended to make this a space in the filename.
* `fancy_clock` is any descriptive text.

Examples:
* `A1234 clock.jpg` - An image for 12:34 AM at night.
* `P1234 mid noon.jpg` - An image for 12:34 PM in the afternoon.
* `E0800 clock.jpg` - Will match either 08:00 or 20:00
* BAD CLOCKS: `A1330 morning not afternoon.jpg` and `P2169 no such time.jpg` - These clocks will be skipped and not load because these are impossible times.

## Additional components
* `analog timepiece.py` - an analog clock that displays when there is no image available. The clock is deigned to be similar to a German railroad clock.  It will execute independently.  This component uses a lot of memory as every frame of the second hand is calculated and drawn to a pygame surface.
* `display_sleep.py` - For use with a Raspberry Pi. a simple script to turn of the display output when a signal is detected on a GPIO pin, usually for connection of a motion sensor.

## TODO:
Each component file has a TODO, but in general:
* Make this software shelf-ready to try without much configuration.
* Move all text fading and transition options to the `text_overlays.py`
* Include a few images for this github upload.
* Include more complete Raspberry Pi build information.
* Anonymize/Genericize the supporting shell scripts for updating and management.
* Have more robust file checking and alternatives for things like font files.

## License
*I believe in strong open source licenses, even for small projects like this.*

The Image Clock, a python clock that displays artwork to tell the time, and its component and supporting files (analog timepiece, file parser, and others) Copyright (C) 2021 github user: RustyPyGuy

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

See the file LICENSE for full details of the GPL v3.0.
