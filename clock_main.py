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
The image clock displays artwork as sets of images once a minute, to tell the time.
The original purpose is to display one photgraph of a clock per minute in a image
format that is square-cropped.

TODO 18 Sep 2021
* If possible, add some intro text when the analog clock is computing and there is
  a blank screen. Previous attepts have been overwritten.
* Move all settings to the settings file and set up file imports.
* Complete the text_overlays module for different text overlay operations and options.
* Some optimizations in the AnalogTimepiece that may improve computation speed.
* Code better algorithms.  There are some O(n^2) algorithms that may be improved and some
  O(n) algoritms that could possibly be O(1).  Currently execution time of these segments
  is not an issue, this would be more of a academic and learning improvement.
* Most other project improvements are outside of python and with supporting shell scripts.
"""

## import required python standard libraries
import argparse
from datetime import datetime
import math
import os
import platform
import stat
import sys
import time

## import pygame and specific libraries and functions
import pygame
from pygame.locals import *
from pygame import Surface

## import additional project files
import settings as s
from analog_timepiece import AnalogTimepiece
from file_enumeration import FileCatalog2
from signal_handler import SignalHandler

## define file paths based on platform.


try:
    if platform.system() == 'Linux':
        IMAGE_PATH = "/var/lib/image-clock/images/"
        FONTPATH_TIME=FONTPATH_DATE=FONTPATH_NEXT=\
         "/var/lib/image-clock/fonts/Indulta/Indulta-SemiSerif-boldFFP.otf"
        if not os.path.exists(FONTPATH_TIME):
            FONTPATH_TIME =""
            print("Font not loaded in configured directory.  Will default to default system font.")

    elif platform.system() == 'Windows':
        IMAGE_PATH = "C:/ProgramData/image-clock/images/"
        FONTPATH_TIME=FONTPATH_DATE=FONTPATH_NEXT=\
        "C:/ProgramData/image-clock/fonts/Indulta/Indulta-SemiSerif-boldFFP.otf"
        if not os.path.exists(FONTPATH_TIME):
            FONTPATH_TIME =""
            print("Font not loaded in configured directory.  Will default to default system font.")
except:
        print("File storage location not defined for OS type:",
        platform.system(), " or font not loaded in configured directory.  Will default to detault system font.")
        FONTPATH = ""

## Variables moved to settings.py and image-clock.ini
# TIMEZONE = "CET"  # not currently used
# FRAME_RATE = 30 # NOTE as currently written will be overriden by argparse default
# TYPE_COLOR = (128,0,0) # Color of font overlay fading text
# TIME_FONT_PERCENT = 10 #height of time font as percent of display size
# FADE_SECONDS = 20 # Number of seconds for font fading

""" Set up argument parser for command line options """
parser = argparse.ArgumentParser(description="The image clock displays the time using images stored in a default image directory. Part function, part form, it is designed to be run continuously.")
parser.add_argument('-w','--windowed', action='store_true', help='Launch clock in windowed mode. (default action)')
parser.add_argument('-f','--fullscreen', action='store_true', help='Launch in fullscreen mode.')
parser.add_argument('-v','--verbose', action='store_true', help='Display verbose console messages.')
parser.add_argument('-i','--invalidfiles', action='store_true', help='Print invalid image files to console and exit.')
parser.add_argument('-r','--framerate', action='store', type=int, default=30, help='Set the frame rate with an integer instead of the program default of 30.')
parser.add_argument('-l','--listfiles', action='store_true', help='List inputted files and exit. Do not execute graphical clock.')
parser.add_argument('-m','--missing', action='store', type=int, default=-1, help='Display the  missing clocks. Takes an arguement 0-23 for the hour. Use 24 to search all hours.')
args = parser.parse_args()

s.FRAME_RATE = args.framerate # Assign frame rate to command line argument

## pygame needs inititiation for some functions to define
pygame.init() # Initialize pygame
pygame.mixer.quit() # Immediately disabling sound mixer to save processor

#####
##### begin function definitions
#####

def time4():
    """
    Outputs the current local time as a 4 digit integer format HHMM
    """
    return int(datetime.now().hour*100) + int(datetime.now().minute)

def hour_search(time4_f, image_file_list_f, start_index_f=0):
    """
    This function when given a 4 digit integer time, a list coprising of
    objects of class file_catalog_alt, and a start_index (0 is default) returns
    a 2 element list of the stopping index and number matched at index
    """
    i = start_index_f
    j = 0
    len_f = len(image_file_list_f)
    while i < len_f:
        if i+1 == len_f and time4_f > image_file_list_f[i].clock4:
        #if the next index will be out of range, then the next clock image msut be after midnight
            return [0, 0]
        elif i+1 == len_f and time4_f < image_file_list_f[i].clock4:
        # if the next index will be out of range and the time is less than the current clock image, select the current index
            return [i, 0]
        elif time4_f == image_file_list_f[i].clock4:
        # if there's a match of current time and current clock, check for how many
        # total elements match by looping with iterate j
            j = 1
            while i+j+1 <= len_f:
            # run a loop to check how many total elements match
                if time4_f == image_file_list_f[i].clock4 \
                and time4_f == image_file_list_f[i+j].clock4:
                    j += 1
                else:
                    return [i,j] # return if all elements found. indexes preserved
            return [i,j] # return if loop does not execute because the last index is being tested
        elif time4_f > image_file_list_f[i].clock4 \
        and time4_f >= image_file_list_f[i+1].clock4:
        # iterate if current time is beyond current and next clock time
            i += 1
            j = 0

        elif time4_f > image_file_list_f[i].clock4 \
        and time4_f <= image_file_list_f[i+1].clock4:
        # iterate if current time is beyond current clock but less or equal to next
            i += 1
            j = 0
        elif time4_f < image_file_list_f[i].clock4 \
        and time4_f < image_file_list_f[i+1].clock4:
        # break out of loop if the next 2 clock times are greater than current
            return [i, j]
        else:
        # return -1 to indicate error
            return [-1, -1]
    # If no condition matches, something is quite wrong, so raise an exception.
    raise Exception("Time search matched no condition for input {}  Likely bug.".format(time4_f))
#    return [i, j]  # is this ever used?


def center_square(scr1):
    """ finds the center square of a surface (typically the screen surface)
     and returns a Rect """
    [scr_width, scr_height] = scr1.get_size()
    if  scr_height <= scr_width:
        return pygame.Rect((scr_width-scr_height)//2,0,scr_height,scr_height)
    else:
        return pygame.Rect(0,(scr_height-scr_width)//2,scr_width,scr_width)

class Fade_Surface(pygame.Surface):
    """
    should be called each clock as needed and returns a value to be used as an
    alpha for fade from 255 to zero. can be nonlinear and decrements the index
    each execution clock_step can be frame rate and cloc_start can be seconds
    """
    def __init__(self, w, h, flags=pygame.SRCALPHA, **args):
        pygame.Surface.__init__(self, size=(w, h), flags=flags, **args)
        self.alpha =255
        self.clock_start=s.FRAME_RATE*s.FADE_SECONDS
        self.clock_step1=int(s.FRAME_RATE*s.FADE_SECONDS)
        self.surfacecopy = self.copy()
        self.alphasurface = pygame.Surface((w,h),flags=pygame.SRCALPHA)
        self.alphasurface.fill((255,255,255,255))
    def fade_down(self,reset=False,start=255):
        if reset==True:
            self.alpha = min(start,255)
            self.clock_start=s.FRAME_RATE*s.FADE_SECONDS
            self.clock_step1=s.FRAME_RATE*s.FADE_SECONDS
            reset=False
#            self = self.surfacecopy.copy()
            return self.blit(self.surfacecopy,(0,0))
        else:
            self.alpha = int(max(255*(self.clock_step1/self.clock_start),0))
#            self.fill((0,0,0,255))
            self.alphasurface.fill((255,255,255,self.alpha))
            self.blit(self.surfacecopy,(0,0))
            self.blit(self.alphasurface,(0,0), special_flags=pygame.BLEND_RGBA_MULT)
            self.clock_step1 -= 1

class LoopVars():
    """ display states per frame/loop
     1 New minute and new image
     2 exisiting image with static text
     3 existing image with fading text
     4 existing image with no text
     5 new minute with no image (analog clock ticking)
     6 existing no-image clock with static text
     7 existing no-image clock with fading text
     8 existing no-image clock with no text, (analog clock ticking)
     9 exit and exception conditions
    """

    def __init__(self):
        self.new_minute=True
        self.fade_active=True
        self.fade_index=255
        self.image_active=False
        self.image_index=0
        self.matched_images=0
        self.matched_image_selected=0
        self.analog_clock_active=0
        self.time4_current=0
    """ Below are methods to change states and state variables. """
    def SetStartNewMinute(self):
        """ New minite initiated with or without image: states 1, 5 """
        self.new_minute=True
        self.fade_active=True
        self.fade_index=255
        self.time4_current=time4()
        [self.image_index,self.matched_images] = hour_search(time4(), file_cat.image_file_list,self.image_index)
        self.image_active = False
    def SetContinueMinute(self):
        """ No new minute, opposite case of SetStartNewMinute:  many states """
        self.new_minute=False
        self.time4_current = time4()
    def SetImageMatched(self,image_index,matched_images):
        """ An image matched: states  """
        if matched_images > 0:
            self.image_index=image_index
            self.matched_images=matched_images
            return self.matched_images
#            self.image_active = True
        else:
             self.image_index = image_index
             self.matched_images =0
             return 0
    def GetImageMatched(self):
        return [self.image_index,self.matched_images]
    def SetImageSelected(self, matched_image_selected):
        """ A specific image selected to display """
        self.matched_image_selected=matched_image_selected
        self.analog_clock_active=0
    def GetImageSelected(self):
        return self.matched_image_selected
    def SetImageLoaded(self):
        self.image_active=True
    def SetNoImageMatched(self):
        """ No current image matched to display """
        self.image_active=False
        self.matched_image_selected=0
        self.analog_clock_active=1
    def ResetAll(self):
        """ Reset all class attributes """
        self.__init__()

#####
##### Main execution starts. Functions defined.
#####
print("Processing files from directory:", IMAGE_PATH)
file_cat = FileCatalog2(IMAGE_PATH)
file_cat.catalog_files()

if args.invalidfiles is True:
    print("image files processed. total clocks:", len(file_cat.image_file_list))
    print("Total error files", len(file_cat.error_file_list))
    for obj in file_cat.error_file_list:
        print (obj.image_filepath)
    print("\nExiting")
    quit()

if args.missing >= 0:
    print("Listing the Missing clocks for hour",args.missing)
    print(file_cat.return_missing(args.missing))
    print("\nExiting")
    quit()

if args.verbose is True or args.listfiles is True:
    print("\nSorting file list and displaying below\n")
    for obj in file_cat.image_file_list:
        print (obj.clock4, obj.image_filepath, obj.description)
print("image files processed. total clocks:", len(file_cat.image_file_list))

if args.listfiles is True:
    print("\nExiting")
    quit()

if not pygame.image.get_extended():
    raise Exception("Pygame install isn't built with extended image support. Exiting")
modes = pygame.display.list_modes()

if args.fullscreen is True:
    screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN|HWSURFACE|DOUBLEBUF)
    pygame.mouse.set_visible(False)
    print("Display in fullscreen. max display mode:", max(modes),
    "selected mode:", screen.get_size())
else:
    screen=pygame.display.set_mode((850,720),HWSURFACE|DOUBLEBUF|RESIZABLE)
    print("Display in windowed mode:", screen.get_size(), " Apparent max mode:", max(modes))

screen_width, screen_height= screen.get_size()
centerRect = center_square(screen)
print("centered square x,y,w,h: ", centerRect)
print("frame rate:", s.FRAME_RATE)

pygame.display.set_caption("Image Clock")
pygame.event.set_blocked(pygame.MOUSEMOTION)

# initiate the pygame Clock
Clock = pygame.time.Clock()

# Initialize the analog clock timepiece
a_clock = AnalogTimepiece(screen, centerRect, s.FRAME_RATE)

# Create fonts. Use default system font if fonts not loaded.
if FONTPATH_TIME:
    introFont = pygame.font.Font(FONTPATH_TIME, int(screen_height*(s.TIME_FONT_PERCENT/200)))
    timeFont = pygame.font.Font(FONTPATH_TIME, int(screen_height*(s.TIME_FONT_PERCENT/100)))
    dateFont = pygame.font.Font(FONTPATH_DATE, int(screen_height*(s.TIME_FONT_PERCENT/100)*.3))
    nextImageFont = pygame.font.Font(FONTPATH_NEXT, int(screen_height*(s.TIME_FONT_PERCENT/100)*.3))
else:
    DEFAULT_FONT = pygame.font.get_default_font()
    introFont = pygame.font.SysFont(DEFAULT_FONT, int(screen_height*(s.TIME_FONT_PERCENT/200)))
    timeFont = pygame.font.SysFont(DEFAULT_FONT, int(screen_height*(s.TIME_FONT_PERCENT/100)))
    dateFont = pygame.font.SysFont(DEFAULT_FONT, int(screen_height*(s.TIME_FONT_PERCENT/100)*.3))
    nextImageFont = pygame.font.SysFont(DEFAULT_FONT, int(screen_height*(s.TIME_FONT_PERCENT/100)*.3))

text_rect = pygame.Rect(0,0,0,0)

#####
##### Define variables for game loop control and initialization.
##### Includes variables these need to persist beyond each loop instance.
#####

done = False # whether no exit signal give to exit the loop
c_index = 0
c_match = 0
timeLabelFade = Fade_Surface(0,0)
dateLabelFade = Fade_Surface(0,0)
nextImageFade = Fade_Surface(0,0)

LC = LoopVars() # Loop control class object

# set up the signal handler.
# NOTE: This is not the best practice, but unfortunately I think the 2 function
# definitions have to be here otherwise I know of no other way to perform
# actions on defined objects.
def signal10():
    # execute functions to re-catalog the files and reset clock state
    file_cat.clear_catalog_files()
    file_cat.catalog_files()
    LC.ResetAll()
def signal12():
    # reserved for future use.
    pass
sig = SignalHandler(signal10,signal12)

# Text to display when screen is blank. Does not work.
introTextSurf = introFont.render("Preparing clock. Standby...", True, s.TYPE_COLOR)
screen.blit(introTextSurf, (centerRect.x+10, centerRect.y+50))
#####
##### Game Loop starts here.
#####
while(not done):
    now_time = datetime.now()
    if LC.image_index == len(file_cat.image_file_list):
    # reset the variables to zero if we have reached the end of the list
        LC.ResetAll()
    if LC.time4_current != time4():
    # flag new minutes to reduce unnecessary execution in loops
        LC.SetStartNewMinute()
        [c_index, c_match] = hour_search(time4(), file_cat.image_file_list,LC.image_index)
        LC.SetImageMatched(c_index, c_match)
    else:
        LC.SetContinueMinute()
## Start of Test code comment out for normal run """
#    [c_index, c_match] = hour_search(1200, image_file_list,0)  #### FOR TESTING
#    LC.SetStartNewMinute()
#    LC.SetImageMatched(c_index, c_match)
## End of test code

    """
    Execution block for a new minute and a successful image match. Load and
    resize the image to prepare for a blit to the screen.
    """
    if LC.matched_images >=1:
        # if there's at least one matching image, display an image
        LC.SetImageSelected(LC.image_index)
        if LC.matched_images > 1:
            #if there's a match on more than one image, select one based on day
            LC.SetImageSelected(LC.image_index + (now_time.day // (30 // LC.matched_images)))
        if LC.image_active is False:
        # If an image hasn't been loaded yet, load it. This is processor intensive
            ImgSurface = pygame.image.load(file_cat.image_file_list[LC.matched_image_selected].image_filepath)
            ImgSurface = ImgSurface.convert()
            tempX,tempY=ImgSurface.get_size()
            ratio = tempX/tempY
            tempSize = (centerRect.w,centerRect.h)
            if args.verbose is True:
                print("time: ",file_cat.image_file_list[LC.matched_image_selected].clock4, \
                      "match image index: ",c_index,"matches: ",c_match, \
                    "selected display index: ",LC.matched_image_selected)
                print (str(ImgSurface.get_size())+" to "+ str(tempSize) +"and ratio: "+str(ratio))
            # rescale the image to fit the current display
            ImgSurface = pygame.transform.smoothscale(ImgSurface, tempSize)
            LC.SetImageLoaded()

    if LC.matched_images == 0:
        """
        Execute the analog clock function if there are no image matches.
        """
        a_clock.compute_timepiece(now_time)

    if LC.new_minute is True:
        """
        If there is a new minute, render the text once and prepare the
        fading surfaces
        """
        timeText=now_time.strftime("%I:%M%p")
        dateText=now_time.strftime("%B %d, %Y")
        nextImageText = "next " + str(file_cat.image_file_list[c_index].clock4 // 100)+\
        ":"+ str((file_cat.image_file_list[c_index].clock4 % 100) // 10)+\
        str((file_cat.image_file_list[c_index].clock4 % 100) % 10)
        #font.render(text, antialias, color, background=None) -> Surface
        timeLabel = timeFont.render(timeText, True, s.TYPE_COLOR)
        dateLabel = dateFont.render(dateText, True, s.TYPE_COLOR)
        nextImageLabel = nextImageFont.render(nextImageText, True, (200,200,200))

        timeLabelRect = timeLabel.get_rect()
        dateLabelRect = dateLabel.get_rect()
        nextImageLabelRect = nextImageLabel.get_rect()
        timeWidth, timeHeight= timeLabelRect.size
        dateWidth, dateHeight= dateLabelRect.size
        nextImageWidth, nextImageHeight = nextImageLabelRect.size
        #Position of the text based on positioning of the centered square
        timeLabelRect.topleft = (centerRect.x+10, centerRect.y+centerRect.h-timeHeight-5)
        dateLabelRect.topleft = (centerRect.x+centerRect.w-dateWidth-10, centerRect.y+centerRect.h-dateHeight-nextImageHeight-20)
        nextImageLabelRect.topleft = (centerRect.x+centerRect.w-nextImageWidth-10, centerRect.y+centerRect.h-nextImageHeight-20)

        timeLabelFade = Fade_Surface(timeWidth, timeHeight, SRCALPHA)
        dateLabelFade = Fade_Surface(dateWidth, dateHeight, SRCALPHA)
        nextImageFade = Fade_Surface(nextImageWidth, nextImageHeight, SRCALPHA)

        timeLabelFade.fill((0,0,0,0))
        dateLabelFade.fill((0,0,0,0))
        nextImageFade.fill((0,0,0,0))

        dateLabelFade.blit(dateLabel,(0,0))
        timeLabelFade.blit(timeLabel,(0,0))
        nextImageFade.blit(nextImageLabel, (0,0))

        timeLabelFade.fade_down(True,240) #prepare fade with a start alpha
        dateLabelFade.fade_down(True,240)
        nextImageFade.fade_down(True)
    if timeLabelFade.alpha > 0:
        # If the text is visible, perform fading operations.
        # Do not fade the next image text.
        timeLabelFade.fill((0,0,0,0))
        dateLabelFade.fill((0,0,0,0))
        timeLabelFade.blit(timeLabel,(0,0))
        dateLabelFade.blit(dateLabel,(0,0))
        timeLabelFade.fade_down(False) # fade only the time and date
        dateLabelFade.fade_down(False)
    # Perform blits to screen.
    # conditions based on whether there is an image to display
    if LC.new_minute is True and LC.image_active is False:
        # screen.fill((0,0,0),centerRect)
        a_clock.blit_request(centerRect)
    if LC.image_active is True:
        screen.blit(ImgSurface, (centerRect.x, centerRect.y))
    if LC.image_active is False:
        # Blit the analog clock changes.
        a_clock.blit_changes()
    if LC.image_active is False and timeLabelFade.alpha > 0:
        # If the analog clock is running, blit the portions under the text.
        a_clock.blit_request(nextImageLabelRect)
        a_clock.blit_request(timeLabelRect)
        a_clock.blit_request(dateLabelRect)
        screen.blit(nextImageLabel,nextImageLabelRect)
    if  timeLabelFade.alpha > 0:
        # Always blit the fading text
        screen.blit(timeLabelFade, timeLabelRect)
        screen.blit(dateLabelFade, dateLabelRect)

    if LC.new_minute is True:
        pygame.display.flip()
    else:
        pygame.display.update(centerRect)

##### Image operations complete.
##### Next execution blocks are run for each loop for housekeeping and exit control.
    for event in pygame.event.get():  # Hit the ESC key to quit.
        if event.type == KEYDOWN and event.key == K_b:
            breakpoint()
        elif (event.type == QUIT or
            (event.type == KEYDOWN and (event.key == K_ESCAPE or event.key == K_q))):
            done = True
        elif event.type==VIDEORESIZE:
            screen=pygame.display.set_mode(event.dict['size'],HWSURFACE|DOUBLEBUF|RESIZABLE)
            screen_width, screen_height= screen.get_size()
            centerRect = center_square(screen)
            analogClockRect = centerRect.copy()
            screen.blit(pygame.transform.smoothscale(screen,event.dict['size']),(centerRect.h,centerRect.w))
            LC.ResetAll()
    Clock.tick(s.FRAME_RATE) # tick the clock at the given frame rate

##### End of main loop.
##### Everything after this is program cleanup.
print("Exiting")
pygame.quit()
