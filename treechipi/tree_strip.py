
import asyncio

import time
from neopixel import *

import numpy as np
from copy import deepcopy

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

        self.pulse_width = 16
        self.boost_factor = int(50.0 / self.pulse_width)

        self.previous_index = 0
        self.target_pixel = 0
        self.active_pixel = 0

        self.fade_base = False
        self.target_base_color = self.base_color
        self.base_target_approach_rate = 0.1

        self.explode_thresh = int(0.75 * self.num_pix)
        self.explode_color = name_to_color('aqua')
        self.next_explode_color = Color(0 ,0 ,5)
        self.exploding = False

        self.random_signal_when_inactive = False
        self.random_signal_when_active = False

        self.is_active = False
        self.updating = False
        self.update_interval = 0.01

        self.pixel_change = 1

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

    def update_base(self):
        self.update_base_color()
        #self.all_to_base(skip_active=True, show=False)

    def update_base_color(self):
        if self.target_base_color != self.base_color:
            if self.verbosity:
                print("Base color changed!")
            if self.fade_base:
                rgb_tuple = TreeStrip.fade_into_color_from_24bit(self.base_color,
                                                                 self.target_base_color,
                                                                 fade_rate=self.base_target_approach_rate)
                self.base_color = Color(int(rgb_tuple[0]), int(rgb_tuple[1]), int(rgb_tuple[2]))
            else:
                if self.verbosity:
                    print(f'changin to {self.target_base_color} from {self.base_color}')
                self.base_color = self.target_base_color
            return True
        else:
            return False

    def update(self):

        """
        mimic Arduino code from TreeChi.
        Loop through all pixels.
        Around the active pixel, bump up the brightness.


        """
        needs_update = self.update_base_color()


        pdiff = self.target_pixel - self.active_pixel
        abs_pdiff = abs(pdiff)
        if abs_pdiff > 1:
            # move pixel
            if abs_pdiff < 10:
                self.pixel_change = max(0.5, abs_pdiff * abs_pdiff / 100.0)
            else:
                self.pixel_change = min(1.0, self.pixel_change + 0.1)


            if pdiff > 0:
                self.active_pixel = self.active_pixel + self.pixel_change
            else:
                self.active_pixel = self.active_pixel - self.pixel_change
            needs_update = True

        else:
            if not self.is_active and self.random_signal_when_inactive:
                self.target_pixel = random.randint(0, 30)
            elif self.is_active and self.random_signal_when_active:
                self.target_pixel = random.randint(int(self.num_pix / 5 * 3), int(self.num_pix))


        if needs_update:
            # set this to avoid it changing in the loop!
            active_temp = deepcopy(self.active_pixel)
            base_temp = deepcopy(self.base_color)
            base_rgb = TreeStrip.rgb_components(self.base_color)
            pulse_width = self.pulse_width
            for i in range(self.num_pix):
                active_diff = np.abs(i - active_temp)
                if active_diff < pulse_width:
                    boost = pulse_width - active_diff
                    rgb_color = TreeStrip.boost_brightness(base_rgb, boost, self.boost_factor)
                    color = TreeStrip.rgb_to_color(rgb_color)
                else:
                    color = base_temp

                self.set_pixel_color(pixel=i, color=color)

            if self.verbosity:
                print(f"done update, {self.target_pixel}  {self.active_pixel:0.1f} {self.pixel_change:0.1f}")

            self.show()
