
import asyncio

import time
from neopixel import *

import numpy as np

update_period = 0.0004

from collections import deque
import webcolors
import sys
import random

from .tree_colors import *


def get_default_tree_strip(data_pin, num_pixels):
    # LED strip configuration:
    LED_COUNT = num_pixels  # Number of LED pixels.
    LED_PIN = data_pin  # GPIO pin connected to the pixels (18 uses PWM!).
    # LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
    LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA = 10  # DMA channel to use for generating signal (try 10)
    LED_BRIGHTNESS = 100  # Set to 0 for darkest and 255 for brightest
    LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53

    strip = TreeStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
                      LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,
                      strip_type=ws.WS2811_STRIP_GRB)
    return strip


class TreeStrip(Adafruit_NeoPixel):

    def __init__(self, *args, **kwargs):
        super(TreeStrip, self).__init__(*args, **kwargs)

        self.verbosity = 0

        self.base_color = Color(4, 0, 32) #dark_orange  # Color(22, 0, 3)
        self.active_color = orange
        self.num_pix = self.numPixels()

        self.pulse_width = 10
        self.boost_factor = int(50.0 / self.pulse_width)

        self.previous_index = 0
        self.target_pixel = 0
        self.active_pixel = 0

        self.fade_base = False
        self.target_base_color = self.base_color
        self.base_target_approach_rate = 0.1

        self.old_pixel_stack = deque()
        self.explode_thresh = int(0.75 * self.num_pix)
        self.explode_color = name_to_color('aqua')
        self.next_explode_color = Color(0 ,0 ,5)
        self.exploding = False

        self.is_active = False

    @staticmethod
    def rgb_components(color):
        red = (color & 0xFF0000) >> 16
        green =  (color & 0x00FF00) >> 8
        blue = (color & 0x0000FF)
        return (red, green, blue)

    @staticmethod
    def rgb_to_color(rgb_tuple):
        return Color(int(rgb_tuple[0]), int(rgb_tuple[1]), int(rgb_tuple[2]))

    @staticmethod
    def fade_into_color_from_24bit(c1, c2, fade_rate):

        rgb_1 = np.array(TreeStrip.rgb_components(c1))
        rgb_2 = np.array(TreeStrip.rgb_components(c2))

        rgb_tuple = abs(((rgb_2 - rgb_1) * fade_rate) + rgb_1).astype('int')


        new_color = Color(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
        #print(f'{rgb_1}  {rgb_2}')
        #print(f"Setting base color to {rgb_tuple}   {new_color}")

        return rgb_tuple

    @staticmethod
    def split_into_color_from_24bit(c1, c2):

        rgb_tuple = abs(np.array(TreeStrip.rgb_components(c2)) - np.array(TreeStrip.rgb_components(c1)) / 2.0).astype(
            'int')

        new_color = Color(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
        return

    @staticmethod
    def limit_brightness_int(el):

        if el > 255:
            el = 255
        elif el < 0:
            el = 0
        return el

    @staticmethod
    def limit_brightness(rgb_array):
        return [TreeStrip.limit_brightness_int(el) for el in rgb_array]

    @staticmethod
    def boost_brightness(base_rgb, boost, boost_fac=30):
        new_rgb = np.array(base_rgb) + int(boost * boost_fac)

        new_rgb = TreeStrip.limit_brightness(new_rgb)


        #print(f'old: {base_rgb}\nnew: {new_rgb}\n\n')

        return new_rgb

    def set_pixel_color(self, pixel, color, reverse=False):
        if reverse:
            i = self.num_pix - pixel
        else:
            i = pixel
        self.setPixelColor(i, color)

    def set_pixel_color_rgb(self, pixel, color_rgb, reverse=False):
        if reverse:
            i = self.num_pix - pixel
        else:
            i = pixel
        self.setPixelColorRGB(i, color_rgb[0], color_rgb[1], color_rgb[2])

    # def update_base_color(self):
    #
    #     if self.base_color != self.target_base_color:
    #         # split into parts, go part way
    #         base_in_parts =
    #         target_in_parts =
    #
    #         diff_in_parts
    #
    #         if
    #
    #         new_base_RGB
    #         self.base_color =

    def all_to_base(self, skip_active=False, show=True):

        for i in range(self.num_pix):
            if skip_active and i == self.active_pixel:
                pass
            else:
                self.set_pixel_color(i, self.base_color)
        if show:
            self.show()

    def maybe_change_base_color(self, color, chance=0.001):
        if random.random() < chance:
            self.base_color = color

    def get_pixel_from_normalized_float(self, nfloat):

        pix = int(nfloat * self.num_pix)
        if pix > self.num_pix:
            return self.num_pix
        elif pix < 0:
            return 0
        return pix

    def update_single_pixel(self, si):
        if si != self.previous_index:
            self.set_pixel_color(si, self.active_color)
            self.set_pixel_color(self.previous_index, self.base_color)
            self.previous_index = si
        else:
            self.set_pixel_color(si, self.active_color)
        self.show()

    def dim_pixel(self, pixel):
        #pixel_color = Color(22, 0, 0)
        pixel_color =self.base_color
        self.set_pixel_color(pixel, pixel_color)

    def dim_old_pixels(self):
        if len(self.old_pixel_stack) > 8:
            pixel = self.old_pixel_stack.pop()

        # self.setPixelColor(pixel, self.base_color)
        # pixel_color = Color(22, 0, 0)
        for pixel in self.old_pixel_stack:
            if pixel != self.active_pixel:
                # print("changing {} pixel to dim".format(pixel))
                # self.setPixelColor(pixel, pixel_color)
                self.dim_pixel(pixel)

    async def explode(self):
        while True:
            await asyncio.sleep(0.0005)

            if self.exploding:
                temp_color = self.explode_color
                self.explode_color = self.next_explode_color
                self.next_explode_color = temp_color
                for i in range(self.explode_thresh, self.num_pix):
                    self.set_pixel_color(i, self.explode_color)
                self.show()

    def explode_pixels(self, color):
        for i in range(self.explode_thresh, self.num_pix):
            self.set_pixel_color(i, color)

    def update_base(self):
        self.update_base_color()
        #self.all_to_base(skip_active=True, show=False)

    def update_base_color(self):
        if self.target_base_color != self.base_color:
            print("Base color changed!")
            if self.fade_base:
                rgb_tuple = TreeStrip.fade_into_color_from_24bit(self.base_color,
                                                                 self.target_base_color,
                                                                 fade_rate=self.base_target_approach_rate)
                self.base_color = Color(int(rgb_tuple[0]), int(rgb_tuple[1]), int(rgb_tuple[2]))
            else:
                print(f'changin to {self.target_base_color} from {self.base_color}')
                self.base_color = self.target_base_color
            return True
        else:
            return False

    def update_old(self):

        if self.active_pixel != self.target_pixel:
            #print(f"traget {self.target_pixel}   {self.active_pixel}")
            # move one
            self.previous_index =self.active_pixel
            self.old_pixel_stack.appendleft(self.active_pixel)

            pdiff = self.target_pixel - self.active_pixel

            if pdiff > 0:
                self.active_pixel = self.active_pixel + 1
            else:
                self.active_pixel = self.active_pixel - 1

            # print("target {} ,   active {} ".format(self.target_pixel, self.active_pixel))
            # print(self.old_pixel_stack)

        # if self.active_pixel > self.explode_thresh:
        #     if not self.exploding:
        #         print("explode!")
        #         # self.explode(color=self.explode_color)
        #         self.exploding = True
        # else:
        #     if self.exploding:
        #         # self.explode(self.base_color)
        #         self.exploding = False
        #         self.explode_pixels(Color(0, 0, 0))
        #     self.set_pixel_color(self.active_pixel, self.active_color)

        # self.dim_old_pixels()
        self.dim_pixel(self.previous_index)

        self.update_base()

        self.show()

    def update(self):

        """
        mimic Arduino code from TreeChi.
        Loop through all pixels.
        Around the active pixel, bump up the brightness.


        """


        #print("update new!")
        needs_update = self.update_base_color()

        #self.all_to_base()

        if self.active_pixel != self.target_pixel:
            # print(f"traget {self.target_pixel}   {self.active_pixel}")
            # move one
            self.previous_index = self.active_pixel
            self.old_pixel_stack.appendleft(self.active_pixel)

            pdiff = self.target_pixel - self.active_pixel

            if pdiff > 0:
                self.active_pixel = self.active_pixel + 1
            else:
                self.active_pixel = self.active_pixel - 1
            needs_update = True

        if needs_update:
            base_rgb = TreeStrip.rgb_components(self.base_color)
            for i in range(self.num_pix):

                pulse_width = self.pulse_width
                active_diff = np.abs(i - self.active_pixel)
                if active_diff < pulse_width:
                    boost = pulse_width - active_diff
                    rgb_color = TreeStrip.boost_brightness(base_rgb, boost, self.boost_factor)
                    color = TreeStrip.rgb_to_color(rgb_color)
                else:
                    color = self.base_color

                self.set_pixel_color(pixel=i, color=color)

            if self.verbosity:
                print(f"done update, {self.active_pixel}")

            self.show()