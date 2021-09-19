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
Analog Timepiece. Displays an analog clock that is similar to a German railroad clock.

USE:
Import class AnalogTimepiece as part of a pygame loop.
execute methods to caluclate timepiece and blit timepiece

simple example:
def main()
    analog_time_object = AnalogTimepiece(screen, screen_rect, FRAME_RATE)
    while pygame_game_loop_running:
        now = datetime.now()
        analog_time_object.compute_timepiece(now)
        blitted = analog_time_object.blit_changes('list')

This file will also execute directly and display a clock.

TEST:
just run this python file to display.  Adjust the frame rate at the end of the file. 30
fps works well for most applications.

TODO:
To do list as of 13 Sep 2021:
    * Write some minute hand physics.
    * Reduce the number of blits of hour and minute hand surface.
    * Improve rendering of second hand with arcs instead of circles to reduce
    artifacts overlapping drawing.
    * Find a gradient for the white background to look less fake.
    * See if some sub-pixel coordinate definitions are possible to deal with
    changing size of second hand.
"""
__author__ = "RustyPyGuy"
__license__ = "GPL v3.0 or more recent"


# from random import random
# required imports for the AnalogTimepiece class
import math
import platform
import pygame
from pygame.locals import *
import pygame.gfxdraw
import settings as s

class AnalogTimepiece():
    def __init__(
            self,
            parentdrawSurface: pygame.Surface,
            parentdrawRect: pygame.Rect,
            fps: int):
        """
        The AnalogTimepiece is pygame drawing object that appears like a
        railroad clock found in Germany.  The object has several methods to
        compute and draw the timepiece to a surface (parentdrawSurface).  The
        clock runs automatically based on system time. Internally, it
        pre-renders the second hand movement onto a series of surfaces, then
        draws or loads the background surface, hour and minute surface, and
        second hand surface on to the parentdrawSurface.  The design is to
        reduce the size and number of blitting operations.  It is suitable to
        blit directly to a screen surface.


        parentdrawSurface: The surface to draw on, most likely the screen.
        parentdrawRect: The rectangle defined in reference to the parentdrawSurface in which to draw the clock.
        fps: frames per second of the pygame loop.
        """
        if parentdrawRect.width != parentdrawRect.height:
            raise Exception(
                "parentdrawRect must be a square. Height and width of passed \
                rectangle are not equal. passed dimensions:",
                parentdrawRect.size)
        self.parentdrawSurface = parentdrawSurface
        self.parentdrawRect = parentdrawRect
        self.fps = fps
        #### Surface and Rect definitions ####
        # Background Surface that is only the size of the Rect
        # The background surface changes only once per day.
        self.backgroundSurface = pygame.Surface(self.parentdrawRect.size)
        # Rect that is referenced to backgroundSurface for orgin coordinates
        self.backgroundRect = self.backgroundSurface.get_rect()
        # first layer Surface and Rect
        # The first layer Surface contains infrequently changing elements like
        # hour minutes
        self.firstLayerSurface = self.backgroundSurface.copy()
        self.firstLayerRect = self.backgroundRect.copy()
        # second layer Surface and Rect
        # The second layer Surface contains frequently changing elements like the second hand
        # also contains top elements like the center hub
        self.secondLayerSurface = pygame.Surface(
            self.backgroundRect.size, flags=pygame.SRCALPHA)
        self.secondLayerRect = self.backgroundRect.copy()
        # Dictionary of surfaces for pre-rendering, Dictionary of Rects for
        # blitting placement they keys are SSFFF - 2 digits for minut (0 to
        # 59), 3 digits for frame (0 to fps-1)
        self.secondLayerSurfaceDict = {
            00000: pygame.Surface(
                self.backgroundRect.size,
                flags=pygame.SRCALPHA)}
        self.secondLayerRectDict = {00000: pygame.Rect(0, 0, 0, 0)}
        # Rect that defines where the changes have occured and should be blitted
        # with lcoal coordinates
        self.localBlitRect = self.backgroundRect.copy()
        # Rect that defines the changes that should be blitted with coordinates
        # referenced to the parent Surface. This Rect may be passed back to the
        # caller of the method that it may return.
        self.parentDrawBlitRect = pygame.Rect(0, 0, 0, 0)
        # lists of surfaces and corresponding rectanges that need to be
        # blitted.
        self.finalBlitSurfaces: list[pygame.Surface] = []
        self.finalBlitRects: list[pygame.Rect] = []
        # source area of Rects, usually the same as above
        self.finalBlitSourceSurfaceRects: list[pygame.Rect] = []
        # list of background rects covers the background of changed surface
        self.backgroundBlitRects: list[pygame.Rect] = []
        """
        variables for clock design. These effectively operate like constants
        """
        self.BLACK = (1, 1, 1)
        self.WHITE = (240, 240, 240)
        self.DGREY = (100, 100, 100)
        self.RED = (250, 0, 0)
        self.COLOR_KEY = (230, 230, 230)  # color key for largely B&W layers
        self.RED2 = (255, 102, 102)
        self.CLOCK_H = self.backgroundRect.height  # analog clock height
        self.MARGIN_H = self.MARGIN_W = s.ANALOG_CLOCK_MARGIN  # margin of analog clock from rectangle border
        self.CLOCK_R = (
            self.backgroundRect.height - self.MARGIN_W) // 2  # clock radius
        # all further variables should be proportional to clock Radius.
        self.HOUR_R = self.CLOCK_R * 5 // 8  # hour hand length
        self.MINUTE_R = self.CLOCK_R * 9 // 10  # minute hand length
        self.SECOND_R = self.CLOCK_R * 9.5 // 10  # second hand length
        self.TEXT_R = self.CLOCK_R * 9 // 10  # distance of hour markings from center
        self.TICK_R = self.CLOCK_R // 45  # stroke width of minute markings
        self.TICK_R_H = self. TICK_R * 2.5  # stroke width of hour markings
        self.TICK_LENGTH = self.CLOCK_R * 2 // 35  # stroke length of minute markings
        self.TICK_LENGTH_H = self.TICK_LENGTH * 3
        self.TICK_LENGTH_QH = int(self.TICK_LENGTH_H * 1.4)
        self.TICK_MARGIN = self.CLOCK_R // 64
        self.LOGO_R = self.CLOCK_R * 9 // 16  # position of the logo
        # hand geometry
        self.HOUR_STROKE = self.CLOCK_R // 14  # hour hand stroke width
        self.MINUTE_STROKE = self.CLOCK_R * 2 // 35  # minute hand stroke width
        self.SECOND_STROKE = int(
            self.CLOCK_R //
            55)  # second hand stroke width
        # size of the circle mounted on the second hand
        self.SECOND_CIRCLE_RAD = int(self.CLOCK_R) // 10
        self.SECOND_TICK_MODE = 5  # sets the behavior of the second hand
        # distance from center to second hand circle
        self.SECOND_CIRCLE_CENTER = 2 * self.SECOND_R // 3
        self.CLOCK_STROKE = self.CLOCK_R // 72  # clock circle stroke width

        """ Loop tracking and internal variable definitions """
        self.first_run = 1                      # flag for first run of compute timepiece method
        self.currentSecondHandIndex = 00000     # reference index for second hand images
        self.previousSecondHandIndex = 00000
        self.frame_minute = 0   # current minute tracked by frame
        self.frame_date = 0
        self.hour_theta = 0.0   # current hour angle (radians)
        self.minute_theta = 0.0  # current minute angle (radians)
        self.current_minute_Rect = pygame.Rect(0, 0, 0, 0)
        self.current_hour_Rect = pygame.Rect(0, 0, 0, 0)
        self.previous_minute_Rect = pygame.Rect(0, 0, 0, 0)
        self.previous_hour_Rect = pygame.Rect(0, 0, 0, 0)
        self.previous_second_Rect = pygame.Rect(0, 0, 0, 0)
        self.current_second = 0
        self.frame_tracker = 0
        self.frame_second_index = 0
        self.previous_frame_second_index = 0

    @staticmethod
    def circle_point(center, radius, theta):
        """Calculates the location of a point of a circle given the circle's
           center and radius as well as the point's angle from the x axis"""
        return (int(center[0] + radius * math.cos(theta)),
                int(center[1] + radius * math.sin(theta)))

    @staticmethod
    def get_angle(unit, total):
        """Calculates the angle, in radians, corresponding to a portion of the clock
           counting using the given units up to a given total and starting from 12
           o'clock and moving clock-wise."""
        return 2.0 * math.pi * unit / total - math.pi / 2.0

    @staticmethod
    def buffer_rect(rect: pygame.Rect, buf=2):
        """ adds pixels in every direction of a Rect to provide a buffer """
        x = max(0, rect.x - buf)  # prevent going less than 0
        y = max(0, rect.y - buf)
        w = rect.w + buf
        h = rect.h + buf
        return pygame.Rect(x, y, w, h)
        # Rect(left, top, width, height)

    @staticmethod
    def re_reference_rect(
            destination_rect: pygame.Rect,
            source_rect: pygame.Rect):
        """ realigns coordinates of source rect to destination rect
        the assumption is that destination_rect is larger than source_rect"""
        x = destination_rect.x + source_rect.x
        y = destination_rect.y + source_rect.y
        size = source_rect.size
        return pygame.Rect((x, y), (size))

    def aa_tapered_line_at_angle( self, drawSurface, center, radius, theta, color, width, flags='draw'):
        """Draws a tapered antialiased line of a defined thickeness from the
        center torwards the given angle in radians with squared edges.  Same
        args as func line_at_angle returns a Rect referenced to drawSurface """
        skew = 2
        point1 = self.circle_point(
            center, radius, theta)  # used for calculation only
        point2 = self.circle_point(
            point1, (width - skew) / 2, theta - math.pi / 2)
        point3 = self.circle_point(
            point1, (width - skew) / 2, theta + math.pi / 2)
        point4 = self.circle_point(
            center, (width + skew) / 2, theta + math.pi / 2)
        point5 = self.circle_point(
            center, (width + skew) / 2, theta - math.pi / 2)
        # EDIT THIS conditional not to draw if only point calculations are
        # needed.
        if True:
            pygame.gfxdraw.aapolygon(
                drawSurface, [
                    point2, point3, point4, point5, point2], color)
            pygame.gfxdraw.filled_polygon(
                drawSurface, [
                    point2, point3, point4, point5, point2], color)
        min_x = min(point2[0], point3[0], point4[0], point5[0])
        min_y = min(point2[1], point3[1], point4[1], point5[1])
        max_x = max(point2[0], point3[0], point4[0], point5[0])
        max_y = max(point2[1], point3[1], point4[1], point5[1])
        return pygame.Rect(min_x, min_y, 1 + max_x - min_x, 1 + max_y - min_y)

    def aa_line_at_angle( self, drawSurface, center, radius, theta, color, width, flags='draw'):
        """Draws an antialiased line of a defined thickeness from the center torwards
        the given angle in radians with squared edges.  Same args as func line_at_angle
        returns a Rect referenced to drawSurface """
        point1 = self.circle_point(
            center, radius, theta)  # used for calculation only
        point2 = self.circle_point(point1, width / 2, theta - math.pi / 2)
        point3 = self.circle_point(point1, width / 2, theta + math.pi / 2)
        point4 = self.circle_point(center, width / 2, theta + math.pi / 2)
        point5 = self.circle_point(center, width / 2, theta - math.pi / 2)
        # EDIT THIS conditional not to draw if only point calculations are
        # needed.
        if True:
            pygame.gfxdraw.aapolygon(
                drawSurface, [
                    point2, point3, point4, point5, point2], color)
            pygame.gfxdraw.filled_polygon(
                drawSurface, [
                    point2, point3, point4, point5, point2], color)
        min_x = min(point2[0], point3[0], point4[0], point5[0])
        min_y = min(point2[1], point3[1], point4[1], point5[1])
        max_x = max(point2[0], point3[0], point4[0], point5[0])
        max_y = max(point2[1], point3[1], point4[1], point5[1])
        return pygame.Rect(min_x, min_y, 1 + max_x - min_x, 1 + max_y - min_y)

    def aa_second_hand2(
            self,
            drawSurface,
            current_second,
            increment,
            clock_style='DE'):
        """
        Draws a sweeping second hand with the position identified by the
        current second and sub-second increment.  Draws the hub on top of the
        second hand. This is designed to be used as part of a pre-render loop
        and emphasizes the drawing quality over processor efficiency.

        frames or dynamically draw frames. returns a Rect of the area modified
        (return value currently broken).

        ref:
        aa_line_at_angle(laaSurface, center, radius, theta, color, width):
        """
        # reference coordinates are based on the passed Surface
        self.drawSurface = drawSurface
        self.drawRect = self.drawSurface.get_rect()
        second_theta = self.get_angle(float(current_second) + increment, 60.0)
        temp_second_circle_center = self.circle_point(
            self.drawRect.center, self.SECOND_CIRCLE_CENTER, second_theta)
        drawSurface.fill((255, 255, 255, 0))
        self.aa_tapered_line_at_angle(self.drawSurface, self.drawRect.center,
                                      self.SECOND_R, second_theta, self.RED,
                                      self.SECOND_STROKE)
        ## Draw circle with a bit thicker circle as is often observed.
        # draw antiailiased outer edge
        pygame.gfxdraw.aacircle(self.drawSurface, temp_second_circle_center[0],
                                temp_second_circle_center[1],
                                self.SECOND_CIRCLE_RAD, self.RED)
        # draw antiailiased inner edge
        pygame.gfxdraw.aacircle(self.drawSurface, temp_second_circle_center[0],
                                temp_second_circle_center[1],
                                self.SECOND_CIRCLE_RAD-(self.SECOND_STROKE*10//8), self.RED)
        # draw filled circle to match with anti-alias.
        pygame.gfxdraw.filled_circle(
            self.drawSurface, temp_second_circle_center[0],
            temp_second_circle_center[1],
            self.SECOND_CIRCLE_RAD, self.RED)
        # draw filled circle with a zero alpha to cut-out the red circle like a donut.
        pygame.gfxdraw.filled_circle(
            self.drawSurface, temp_second_circle_center[0],
            temp_second_circle_center[1],
            self.SECOND_CIRCLE_RAD - (self.SECOND_STROKE*10//8), (255, 255, 255, 0))
        # NOTE: No anti-aliased center draw here.  Maybe an AA circle then a regular one?
        # add center hub
        pygame.gfxdraw.aacircle(
            self.drawSurface,
            self.drawRect.centerx,
            self.drawRect.centery,
            self.MINUTE_STROKE + 4,
            self.BLACK)
        pygame.gfxdraw.aacircle(
            self.drawSurface,
            self.drawRect.centerx,
            self.drawRect.centery,
            self.MINUTE_STROKE + 4,
            self.DGREY)
        pygame.gfxdraw.filled_circle(
            self.drawSurface,
            self.drawRect.centerx,
            self.drawRect.centery,
            self.MINUTE_STROKE + 4,
            self.BLACK)
        # NOTE: Return NOT PRECISE, but currently not important beacause the
        # return value is not used anywhere.
        return self.drawRect

    def draw_rect(self, drawSurface, inputRect):
        """Draws a filled rectangle."""
        rectangle_corners = [
            inputRect.topleft,
            inputRect.topright,
            inputRect.bottomright,
            inputRect.bottomleft,
            inputRect.topleft]
        pygame.gfxdraw.aapolygon(
            drawSurface, rectangle_corners, self.RED2)
        pygame.gfxdraw.filled_polygon(
            drawSurface, rectangle_corners, self.RED2)
        return True

    def draw_beveled_rect(self, drawSurface: pygame.Surface,
                          inputRect: pygame.Rect,
                          bevel_radius: int):
        """Draws a rectangle with bevels. The radius of the bevels is defined
        by the bevel_radius """
        drawRect = drawSurface.get_rect()
        # Draw two overlapping Rectangles.
        rectTemp=pygame.Rect(drawRect.x+inputRect.x+bevel_radius,drawRect.y+inputRect.y,inputRect.w-2*bevel_radius,inputRect.h)
        self.draw_rect(drawSurface,rectTemp)
        rectTemp=pygame.Rect(drawRect.x+inputRect.x,drawRect.y+inputRect.y+bevel_radius,inputRect.w,inputRect.h-2*bevel_radius)
        self.draw_rect(drawSurface,rectTemp)
        # define the centers of the the beveled circles.
        circle_center_list = [
                            (drawRect.x+inputRect.x+bevel_radius, drawRect.y+inputRect.y+bevel_radius),
                            (drawRect.x+inputRect.x+inputRect.w-bevel_radius, drawRect.y+inputRect.y+bevel_radius),
                            (drawRect.x+inputRect.x+bevel_radius, drawRect.y+inputRect.y+inputRect.h-bevel_radius),
                            (drawRect.x+inputRect.x+inputRect.w-bevel_radius, drawRect.y+inputRect.y+inputRect.h-bevel_radius)]
        # Draw the four circles that make the corners.
        for x in range(0,4):
            circle_center=circle_center_list[x]
            pygame.gfxdraw.aacircle(
                drawSurface,
                circle_center[0],circle_center[1],bevel_radius,
                self.RED2)
            pygame.gfxdraw.filled_circle(
                drawSurface,
                circle_center[0],circle_center[1],bevel_radius,
                self.RED2)


    @staticmethod
    def ramp_tick(frame_rate, mode=0):
        """ Returns a list the same length frame_rate of floats from 0 to 1
        that would typically be multiplied by an angle to calculate the
        sub-second movement of the second hand to emulate a form of sweeping
        movement. Arguments: frame_rate - anticipated frame rate and list
        length mode - calculation algorithm used for partial sweep and
        resulting visual effect """
        ramp_list = []
        i = 0
        if mode == 0:  # Continuous sweep: never stops
            for i in range(0, int(frame_rate - 1)):
                ramp_list[i] = (i + 1) / frame_rate
            return ramp_list

        if mode == 1:  # Linear Advance: Advances linearly and pauses. Looks fake.
            for i in range(0, int(frame_rate)):
                x = i / frame_rate
                if x <= .35:
                    ramp_list.append(2.86 * x)
                else:
                    ramp_list.append(1.0)
            return ramp_list

        if mode == 2:  # Sinusoidal: Pure sinusoidal movement. Looks less fake.
            for i in range(0, int(frame_rate)):
                x = i / frame_rate
                if x <= .68:
                    # the math function below creates sinusoidal movement that
                    # stops at one.  The constant "9" may be adjusted for
                    # faster or slower movement. the if statement will also
                    # have to be adjusted for when the math function is equal
                    # to 1.
                    answer = (math.sin(9 * x + math.pi)
                              + (9 * x)) \
                        / (2 * math.pi)
                    ramp_list.append(round(answer, 4))
                else:
                    ramp_list.append(1.0)
            return ramp_list

        # Modified sinusoial: The sum of two phase-shifted sinusoidals for a
        # smooth but less fake looking movement. Getting better.
        if mode == 3:
            for i in range(0, int(frame_rate)):
                x = i / frame_rate
                if x <= .721:
                    # Similar to mode 2, but two sinusoids are added with a
                    # phase difference and correcting constants
                    answer = (math.sin(9 * x + math.pi)
                              + .7 * math.sin(9 * x + .85 * math.pi)
                              + 17 * x - .316) \
                        / (3.79 * math.pi)
                    answer = round(answer, 4)
                    ramp_list.append(answer)
                else:
                    ramp_list.append(1.0)
            return ramp_list

        if mode == 4:
            # Acceleration Estimate: This calculation is meant to smiulate
            # motor physics and the unequal accelerate and decelerate.  There
            # are 4 parts, linear acceleration, constant velocity, linear
            # deccelertion, and rest.
            for i in range(0, int(frame_rate)):
                x = i / frame_rate
                if x <= .300:
                    answer = 3.5 * x**2
                    answer = round(answer, 4)
                    ramp_list.append(answer)
                elif x <= .600:
                    answer = 1.700 * x - .195
                    answer = round(answer, 4)
                    ramp_list.append(answer)
                elif x <= .800:
                    answer = 1.7 * x - .625 * x**2
                    answer = round(answer, 4)
                    ramp_list.append(answer)
                else:
                    ramp_list.append(1.0)
            return ramp_list

        if mode == 5:
            # Acceleration Estimate number 2: This calculation is meant to
            # smiulate motor physics and the unequal accelerate and decelerate.
            # This version has a longer linear velocity method than above. The
            # overall physics are the same.  There are 4 parts, linear
            # acceleration, constant velocity, linear deccelertion, and rest.
            for i in range(0, int(frame_rate)):
                x = i / frame_rate
                if x <= .300:
                    answer = 3.5 * x**2
                    answer = round(answer, 4)
                    ramp_list.append(answer)
                elif x <= .622:
                    answer = 1.700 * x - .195
                    answer = round(answer, 4)
                    ramp_list.append(answer)
                elif x <= .793:
                    answer = 1.7 * x - .625 * x**2 + .0453
                    answer = round(answer, 4)
                    ramp_list.append(answer)
                else:
                    ramp_list.append(1.0)
            return ramp_list

##### Below are Methods intended to be called externally from game/program loop

    def compute_timepiece(self, now_var):
        """
        This method to perform all of the graphics calculations and prepare the
        intermediate surfaces for blitting. It should be run every game loop.
        It does not blit anything to the parent surface.  It may be usefult to
        place this in a specific position in the game loop due to it's possible
        computational load.
        """
        self.now_var = now_var
        if self.first_run == 1:
            # This portion is only run once and builds the background imagery
            # and creates the dictionary of second hand surfaces and reference
            # rectangles Set background to black and all others to color key
            # transparency
            self.backgroundSurface.fill(self.BLACK)
            self.firstLayerSurface.fill(self.COLOR_KEY)
            self.secondLayerSurface.fill(self.COLOR_KEY)
            self.firstLayerSurface.set_colorkey(self.COLOR_KEY)
            self.secondLayerSurface.set_colorkey(self.COLOR_KEY)
            # Draw the white clockface
            pygame.gfxdraw.aacircle(
                self.backgroundSurface,
                self.backgroundRect.centerx,
                self.backgroundRect.centery,
                (self.backgroundRect.width // 2 - self.MARGIN_W // 2),
                self.WHITE)
            pygame.gfxdraw.filled_circle(
                self.backgroundSurface,
                self.backgroundRect.centerx,
                self.backgroundRect.centery,
                (self.backgroundRect.width // 2 - self.MARGIN_W // 2),
                self.WHITE)
            for hour in range(0, 13):
                theta = self.get_angle(hour, 12)
                p1 = self.circle_point(
                    self.backgroundRect.center,
                    self.CLOCK_R -
                    self.TICK_LENGTH_H -
                    self.TICK_MARGIN,
                    theta)
                p2 = self.circle_point(
                    self.backgroundRect.center,
                    self.CLOCK_R -
                    self.TICK_LENGTH_QH -
                    self.TICK_MARGIN,
                    theta)
                if hour in [0, 3, 6, 9]:
                    self.aa_line_at_angle(
                        self.backgroundSurface,
                        p2,
                        self.TICK_LENGTH_QH,
                        theta,
                        self.BLACK,
                        self.TICK_R_H)
                else:
                    self.aa_line_at_angle(
                        self.backgroundSurface,
                        p1,
                        self.TICK_LENGTH_H,
                        theta,
                        self.BLACK,
                        self.TICK_R_H)
                # Draw the minute markings (smaller narrower lines)
                for minute in range(0, 61):
                    theta = self.get_angle(minute, 60)
                    point1 = self.circle_point(
                        self.backgroundRect.center,
                        self.CLOCK_R -
                        self.TICK_LENGTH -
                        self.TICK_MARGIN,
                        theta)
                    self.aa_line_at_angle(
                        self.backgroundSurface,
                        point1,
                        self.TICK_LENGTH,
                        theta,
                        self.BLACK,
                        self.TICK_R)
            # draw the rectangular logo
            if platform.system() == 'Linux':
                FONTPATH = "/var/lib/image-clock/fonts/PlatNomor/PlatNomor-eZ2dm.otf"
            elif platform.system() == 'Windows':
                FONTPATH = "C:/ProgramData/image-clock/fonts/PlatNomor/PlatNomor-eZ2dm.otf"
            else:
                raise Exception(
                    "File storage location not defined for OS type:",
                    platform.system())
            ### Calculate and prepare the date box.
            # calculate the maximum size of the date font box with the max character size.
            self.dateTextFont = pygame.font.Font(FONTPATH, 3 * self.CLOCK_R // 25)
            dateBoxSurface = self.dateTextFont.render("88 . 88", 1, self.RED)
            self.dateBoxRect = dateBoxSurface.get_rect()
            self.dateBoxRect.center = self.circle_point(
                self.backgroundRect.center, self.LOGO_R, -math.pi / 2)
            self.dateBoxRect.inflate_ip(
                self.dateBoxRect.w // 20,
                11 * self.dateBoxRect.h // 16)

            self.draw_beveled_rect(self.backgroundSurface, self.dateBoxRect,self.dateBoxRect.h//3)
            dateText = self.now_var.strftime("%m.%d")
            dateTextSurface = self.dateTextFont.render(dateText, 1, self.WHITE)
            dateTextRect = dateTextSurface.get_rect()
            dateTextRect.center = self.dateBoxRect.center
            dateTextRect.centery = dateTextRect.centery + self.CLOCK_R // 66
            self.backgroundSurface.blit(dateTextSurface, dateTextRect.topleft)
            self.frame_date = self.now_var.day

            self.finalBlitRects.append(self.backgroundRect)
            self.finalBlitSourceSurfaceRects.append(self.backgroundRect)
            self.finalBlitSurfaces.append(self.backgroundSurface)

            # Pre-render the second hand Surfaces.
            # This portion is processor and memory intensive
            second = 0
            frame = 0
            # calculate the movement of the second hand between seconds
            sub_second = self.ramp_tick(self.fps, self.SECOND_TICK_MODE)
            # Create the temporary surfaces.  Theses are the only surface that has per-pixel alpha
            tempSurface_1 = pygame.Surface(
                self.backgroundRect.size, flags=SRCALPHA)
            for second in range(0, 60):  # seconds
                for frame in range(0, self.fps):  # frames in second
                    tempSurface_1.fill((255, 255, 255, 0))
                    # Draw the second hand on a normal size surface, get the
                    # size
                    self.aa_second_hand2(
                        tempSurface_1, second, sub_second[frame])
                    tempImageRect = tempSurface_1.get_bounding_rect()
                    # create a Surface of minimal size
                    tempSurface_2 = pygame.Surface(
                        tempImageRect.size, flags=SRCALPHA)
                    tempSurface_2.fill((255, 255, 255, 0))
                    # TEMP
                    # tempSurface_2.fill((0,250,0,128))
                    tempSurface_2.blit(
                        tempSurface_1, (0, 0),
                        area=tempImageRect)
                    temp_key = int(second * 1000 + frame)
                    self.secondLayerSurfaceDict[temp_key] = tempSurface_2.copy()
                    self.secondLayerRectDict[temp_key] = tempImageRect.copy()
            self.first_run = 0
            # End of first run code block
        # Continue with computations run on every loop
        # Add background surfaces and rects to lists
        ### Hour and Minute
        # draw hour and minute hands once per minute and track the previous
        # draw to clear before blitting
        if self.frame_minute != self.now_var.minute:
            if self.frame_date != self.now_var.day:
                self.backgroundSurface.fill(self.WHITE,self.dateBoxRect)
                self.draw_beveled_rect(self.backgroundSurface, self.dateBoxRect,self.dateBoxRect.h//3)
                dateText = self.now_var.strftime("%m.%d")
                dateTextSurface = self.dateTextFont.render(dateText, 1, self.WHITE)
                dateTextRect = dateTextSurface.get_rect()
                dateTextRect.center = self.dateBoxRect.center
                dateTextRect.centery = dateTextRect.centery + self.CLOCK_R // 66
                self.backgroundSurface.blit(dateTextSurface, dateTextRect.topleft)
                self.backgroundBlitRects.append(self.dateBoxRect)
            # set copy Rects to previous minute Rect before they are changed
            self.previous_minute_Rect = self.current_minute_Rect.copy()
            self.previous_hour_Rect = self.current_hour_Rect.copy()
            # get draw angles
            self.hour_theta = self.get_angle(
                self.now_var.hour + 1.0 * self.now_var.minute / 60, 12)
            self.minute_theta = self.get_angle(self.now_var.minute, 60)
            # clear previous hour and minute hand surfaces with limited fill
            self.firstLayerSurface.fill(
                self.COLOR_KEY, self.previous_hour_Rect)
            self.firstLayerSurface.fill(
                self.COLOR_KEY, self.previous_minute_Rect)
            # draw hour and minute hands and save positions to Rects
            self.current_hour_Rect = self.aa_line_at_angle(
                self.firstLayerSurface,
                self.firstLayerRect.center,
                self.HOUR_R,
                self.hour_theta,
                self.BLACK,
                self.HOUR_STROKE)
            self.current_minute_Rect = self.aa_line_at_angle(
                self.firstLayerSurface,
                self.firstLayerRect.center,
                self.MINUTE_R,
                self.minute_theta,
                self.BLACK,
                self.MINUTE_STROKE)
            # reassign the frame_minute to not redraw the minute and hour hands again.
            self.frame_minute = self.now_var.minute
        # NOTE: Currently blits hour and minute hands every frame.  Needs correction.
        # add rectangles and surfaces to blit lists for hours and minutes
        self.finalBlitRects.append(self.current_hour_Rect)
        self.finalBlitSourceSurfaceRects.append(self.current_hour_Rect)
        self.finalBlitSurfaces.append(self.firstLayerSurface)
        self.backgroundBlitRects.append(self.current_hour_Rect.union(self.previous_hour_Rect))

        self.finalBlitRects.append(self.current_minute_Rect)
        self.finalBlitSourceSurfaceRects.append(self.current_minute_Rect)
        self.finalBlitSurfaces.append(self.firstLayerSurface)
        self.backgroundBlitRects.append(self.current_minute_Rect.union(self.previous_minute_Rect))

        # Apply the second hand from the dictionary of Surfaces and Rects
        if self.current_second == self.now_var.second:
            self.frame_tracker += 1
            # safety to prevent going out of range if time and frame rates do
            # not align
            self.frame_tracker = min(self.frame_tracker, self.fps - 1)
        else:
            self.frame_tracker = 0
            self.current_second = self.now_var.second
        self.previous_frame_second_index = self.frame_second_index
        self.previous_second_Rect = self.secondLayerRect
        self.frame_second_index = int(
            self.current_second * 1000 + self.frame_tracker)
        self.secondLayerSurface = self.secondLayerSurfaceDict[self.frame_second_index]
        self.secondLayerRect = self.secondLayerRectDict[self.frame_second_index]
        self.finalBlitRects.append(self.secondLayerRect)
        self.backgroundBlitRects.append(self.secondLayerRect.union(self.previous_second_Rect))
        # the arguments here are different thatn the other layers because the
        # dictionary of surfaces have different origin reference points and
        # sizes.
        self.finalBlitSourceSurfaceRects.append(
            Rect((0, 0), (self.secondLayerRect.w, self.secondLayerRect.h)))
        self.finalBlitSurfaces.append(self.secondLayerSurface)
        # Add the background surface recetangles to the start of the blit list.
        # Use the current list of destination rects but not necessarily the source rects
        # This avoids blitting the entire background surface.
# NOTE: Is there a better way to insert the background list ahead of the blit list?
        for count in range(0, len(self.backgroundBlitRects)):
            self.finalBlitRects.insert(0,self.backgroundBlitRects[count])
            self.finalBlitSourceSurfaceRects.insert(0,self.backgroundBlitRects[count])
            self.finalBlitSurfaces.insert(0,self.backgroundSurface)

    def blit_changes(self, return_type='none'):
        """
        blits the timepiece to the parentdrawSurface method is designed to blit
        directly to a final display surface to reduce the number of
        intermediate blits.  the compute_timepiece method is normally executed
        prior to executing this method.  If not, there will likely be timing
        and display errors.
        """
        # loop through the list of Surfaces and blit them.
        final_blit_dest_rects = []
        # breakpoint()
        for count in range(0, len(self.finalBlitRects)):
            # for each surface: correct destination coordinates to parent Rect
            dest_rectangle = self.re_reference_rect(
                self.parentdrawRect, self.finalBlitRects[count])
            # blit source rect and source surface
            blitted_rect = self.parentdrawSurface.blit(
                self.finalBlitSurfaces[count],
                dest_rectangle, self.finalBlitSourceSurfaceRects[count])
            final_blit_dest_rects.append(blitted_rect)
        # clear the lists of rectangles and surfaces.
        self.finalBlitRects.clear()
        self.finalBlitSourceSurfaceRects.clear()
        self.finalBlitSurfaces.clear()
        self.backgroundBlitRects.clear()
        if return_type == 'none':
            return None
        elif return_type == 'rect':
            return True  # needs correction
        elif return_type == 'list':
            return final_blit_dest_rects
        else:
            return True

    def blit_request(self, re_rect: pygame.Rect):
        """
        Blits the current computed timepiece defined by the requested Rect.
        This should only be used after a blit_changes method, as it will not
        automatically include those Rects.  This method is useful for changes
        in overlays to the AnalogTimepiece in a game loop.  This blits all
        component Surfaces including the background that rarely changes.
        """
        # adj_src_rect = self.re_reference_rect(self.parentdrawRect, rect)
        # adjusted_source_rect = self.re_reference_rect(rect,self.parentdrawRect )
        adj_src_rect = pygame.Rect((re_rect.x-self.parentdrawRect.x, re_rect.y-self.parentdrawRect.y), re_rect.size)
        self.parentdrawSurface.blit(self.backgroundSurface, re_rect, adj_src_rect)
        self.parentdrawSurface.blit(self.firstLayerSurface, re_rect, adj_src_rect)
        # Determine second layer blit area by a clipping of the offset rect beause the second surfaces are often smaller.
        # Determine the correct portion of the source rect to blit because the reference orgin is different per frame.
        second_rect_to_screen = pygame.Rect((self.parentdrawRect.x+self.secondLayerRect.x,\
                                             self.parentdrawRect.y+self.secondLayerRect.y),self.secondLayerRect.size)
        clipped_re_rect = re_rect.clip(second_rect_to_screen)
        blit_source_rect = pygame.Rect((clipped_re_rect.x-self.secondLayerRect.x-self.parentdrawRect.x,\
                                        clipped_re_rect.y-self.secondLayerRect.y-self.parentdrawRect.y),clipped_re_rect.size)
        self.parentdrawSurface.blit(self.secondLayerSurface, clipped_re_rect, blit_source_rect)

"""
End of AnalogTimepiece class definition
Code below is for testing and running from this file alone.
"""


def main():
    """This is Executed only if file is run directly.  Intended for testing
    only. Some examples of what to import and define for implementation are
    below.  """
    from datetime import datetime
    import sys
    pygame.init()
    pygame.mixer.quit()  # immediately disabling sound to save processor
    # using a rectangular screen for testing to reveal any centering issues
    screen = pygame.display.set_mode((800, 700))
    pygame.display.set_caption('Analog Timepiece Test')
    # manually defining the center of the screen for the Rect object.
    screen_rect = pygame.Rect(50, 0, 700, 700)
    pygame.event.set_blocked(pygame.MOUSEMOTION)
    done = False
    atime = AnalogTimepiece(screen, screen_rect, FRAME_RATE)
    # variable that is assigned in the loop but should persist between loops.
    global now
    print("\nStarting Analog Timepiece with a frame rate of", FRAME_RATE,
          "\nStandby, background drawing will take some time.")
    while not done:
        now = datetime.now()
        atime.compute_timepiece(now)
        blitted = atime.blit_changes('list')
        # add some arbitrary rectangles to blit to test the blit_request method
        atime.blit_request(pygame.Rect((150,200),(350,50)))
        atime.blit_request(pygame.Rect((500,250),(50,350)))
        atime.blit_request(pygame.Rect((150,500),(300,50)))
        atime.blit_request(pygame.Rect((150,200),(50,350)))
        # not the most efficient screen drawing but sufficient for these
        # purposes.
        pygame.display.flip()
        clock.tick(FRAME_RATE)
        for event in pygame.event.get():
            if (event.type == QUIT or (event.type == KEYDOWN and (
                    event.key == K_ESCAPE or event.key == K_q))):
                done = True
            elif (event.type == KEYDOWN and event.key == K_b):
                print("blitted: ", blitted)
                breakpoint()
#    size = sys.getsizeof(analog_timepiece.secondLayerSurfaceDict)
#    print("size of dict of surfaces :", size )
    pygame.quit()


if __name__ == "__main__":
    """ This is executed when run from the command line """
    clock = pygame.time.Clock()
    FRAME_RATE = 30
    main()
