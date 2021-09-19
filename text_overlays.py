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
A set of object definitions to deal with fading text in Pygame.  The
text_overlays script is in progress.  Not fully implemented yet.

USE:

TEST:

TODO:
* Finish this and document it.
"""
import pygame

import settings as s

# General Class TextOverlay
# contains loop control and initial conditions

# Sub classes for each display type

# methods: compute, blit (similar to Analog Timepiece)
class TextOverlay:
    def __init__(self,
            parentdrawSurface: pygame.Surface,
            parentdrawRect: pygame.Rect,
            blit_position: tuple,
            text: str,
            fps: int,
            sequence: int,
            color: tuple = (255,255,255,255) ):
        """ The TextOverlay class creates classes of objects for dynamic
        fading, shifting, or other visual effects in a pygame game loop.  The
        intended object is derived from text. This is intended to be used as
        a parent class for specific effects. Methods are designed to be uniform
        accross different child classes and inherit as much common logic and
        funtionality as possible. For processor efficency, methods are designed
        to blit to a screen surface and not other intermediate surfaces. Copies
        of background surfaces are preserved in the class to enable this."""
        # final surface to draw to, usually screen
        self.parentdrawSurface: pygame.Surface = parentdrawSurface
        # the rectangle defining the area of the parent surface that is used for drawing.
        self.parentdrawRect: pygame.Rect = parentdrawRect
        # intended blit position relative to the parentdrawRect. Can be modified later.
        self.blit_position_x: int = blit_position[0]
        self.blit_position_y: int = blit_position[1]
        # the text string to be overlayed.
        self.text: str = text
        # the FPS of the running pygame program.
        self.fps: int = fps
        # NOTE: What is this variable sequence for? I forgot already
        self.sequence: int = sequence
        # counter for fading effects. Starts at a high point and decreases to zero normally.
        self.counter: int = self.fps * s.TRANSITION_TIME
        # intermediate surface for drawing and rendering calculations
        # may be redifined with a render operation.
        self.textSurface: pygame.Surface = pygame.Surface(self.parentdrawRect.size)
        # loop control variable. Clears surfaces and other conditions on first run.
        self.first_run: bool = True
        # starting color of text overlay
        self.color: tuple = color
    def compute(self):
        """Perform the computation of one frame operation.  This method will
        will have only minor instructions in the parent class.  The inheriting
        classes will expect to modify this method significantly."""
        ## render the appropriate text in first run.

        if self.first_run == True:
            # breakpoint()
            test_font = pygame.font.SysFont(None,100)
            self.textSurface = test_font.render(self.text, 1, self.color) 
            self.textcopySurface = self.textSurface.copy()
            self.alphatextSurface = pygame.Surface(self.textSurface.get_size())
            self.alphatextSurface.fill((255,255,255,255))
            # a copy of the parent draw surface to use as a base for fading operations
            self.parentcopySurface: pygame.Surface = self.parentdrawSurface.copy() 
    def blit(self):
        """Blit the workingSurface to the parentdrawSurface with relative
        coordinates self.blit_position_x and self.blit_position_y with the parentdrawRect as the coordinate
        orgin. Default is at the origin.
        """
        # blit the working surface textSurface to the parent draw surface in a relative
        self.parentdrawSurface.blit(self.textSurface, \
                                    (self.parentdrawRect.x+self.blit_position_x,\
                                    self.parentdrawRect.y+self.blit_position_y))

        pass
    def reset(self):
        """ Resets the class to an initial state. Text will not be re-rendered
        until a computer method is called.  """
        self.counter = self.fps * s.TRANSITION_TIME
        self.first_run = True
        self.textSurface.fill(0,0,0)
        self.alphatextSurface.fill((255,255,255,255))

    def rebase(self):
        """ Reloads the base parentdrawSurface into the copy variable """
        pass
    def change_text(self, new_text: str):
        """ Change the text without reinitializing the object class.  Causes
        the object to reset. Text will not be rendered until a compute method
        is called."""
        self.text = new_text
        self.reset()

## Below for reference
# class SimpleFadeText(TextOverlay):
#     def __init__(self, parentdrawSurface, parentdrawRect, blit_position, text, fps, sequence, color):
#         TextOverlay.__init__(self,parentdrawSurface,parentdrawRect,blit_position, text, fps, sequence, color)
#     def compute(self):
#         super(SimpleFadeText, self).compute()
#     def blit(self):
#         super(SimpleFadeText, self).blit()
#     def reset(self):
#         super(SimpleFadeText, self).reset()
#     def change_text(self, new_text):
#         super(SimpleFadeText, self).change_text(new_text)

class SimpleFadeText(TextOverlay):
    """Class to fade text from opaque to transparent."""
    def __init__(self, parentdrawSurface, parentdrawRect, blit_position, text, fps, sequence, color):
        TextOverlay.__init__(self,parentdrawSurface,parentdrawRect,blit_position, text, fps, sequence, color)
    def compute(self):
        super(SimpleFadeText, self).compute()
        self.textSurface =  self.textcopySurface.copy()
        self.textSurface.blit(self.alphatextSurface,(0,0),self.textSurface.get_rect(),pygame.BLEND_RGBA_MULT)
        # breakpoint()
        self.alphatextSurface.fill((255,255,255,self.counter * 255 // s.TRANSITION_TIME // self.fps))
        if(self.counter > 0):
            self.counter -= 1
    def blit(self):
        super(SimpleFadeText, self).blit()
        self.parentdrawSurface.blit(self.parentcopySurface,(0,0))
        self.parentdrawSurface.blit(self.textSurface, 
                                    (self.parentdrawRect.x+self.blit_position_x,
                                    self.parentdrawRect.y+self.blit_position_y),
                                    self.parentdrawRect, pygame.BLEND_RGBA_MULT)
    def reset(self):
        super(SimpleFadeText, self).reset()
    def change_text(self, new_text):
        super(SimpleFadeText, self).change_text(new_text)

# class A(object):     # deriving from 'object' declares A as a 'new-style-class'
#     def foo(self):
#         print "foo"

# class B(A):
#     def foo(self):
#         super(B, self).foo()   # calls 'A.foo()'

# myB = B()
# myB.foo()

def main():
    """This is Executed only if file is run directly.  Intended for testing
    only. Some examples of what to import and define for implementation are
    below.  """
    pygame.init()
    pygame.mixer.quit()  # immediately disabling sound to save processor
    # using a rectangular screen for testing to reveal any centering issues
    screen = pygame.display.set_mode((800, 700))
    pygame.display.set_caption('Text application and fading test')
    # manually defining the center of the screen for the Rect object.
    screen_rect = pygame.Rect(50, 0, 700, 700)
    pygame.event.set_blocked(pygame.MOUSEMOTION)
    done = False
    text_one =SimpleFadeText(screen, screen_rect, (20,20), "This is text One", FRAME_RATE, 0, (180,180,255,255))
    text_two =SimpleFadeText(screen, screen_rect, (100,100), "This is text TWO", FRAME_RATE, 0, (128,128,128,255,))
    text_three =SimpleFadeText(screen, screen_rect, (200,200), "This is text ThreeThreeThree", FRAME_RATE, 0, (255,0,0,255))
    # variable that is assigned in the loop but should persist between loops.
    global now
    print("\nStarting text overlays test with a frame rate of", FRAME_RATE,
          "\nStandby, background drawing will take some time.\
           \nPress q or ESC to quit.")

    while not done:
        now = datetime.now()
        text_one.compute()
        text_one.blit()
        #### insert the ops here
        # not the most efficient screen drawing but sufficient for these
        # purposes.
        pygame.display.flip()
        clock.tick(FRAME_RATE)

        for event in pygame.event.get():
            if (event.type == QUIT or (event.type == KEYDOWN and (
                    event.key == K_ESCAPE or event.key == K_q))):
                done = True
            elif (event.type == KEYDOWN and event.key == K_b):
                # print("blitted: ", blitted)
                breakpoint()
#    size = sys.getsizeof(analog_timepiece.secondLayerSurfaceDict)
#    print("size of dict of surfaces :", size )
    pygame.quit()

if __name__ == "__main__":
    """ This is executed when run from the command line """
    import sys
    from datetime import datetime

    from pygame.locals import *
    clock = pygame.time.Clock()
    FRAME_RATE = 30
    main()
