
import asyncio

import time
from neopixel import *

import numpy as np
from copy import deepcopy

from collections import deque
import webcolors
import sys
import random

from .tree_colors import *
from colorsys import hsv_to_rgb


def create_led_strip(data_pin, num_pixels, channel=0):
    # LED strip configuration:
    LED_COUNT = num_pixels  # Number of LED pixels.
    LED_PIN = data_pin  # GPIO pin connected to the pixels (18 uses PWM!).
    # LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
    LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA = 10  # DMA channel to use for generating signal (try 10)
    LED_BRIGHTNESS = 250  # Set to 0 for darkest and 255 for brightest
    LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL = channel  # set to '1' for GPIOs 13, 19, 41, 45 or 53

    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
                              LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,
                              strip_type=ws.WS2811_STRIP_GRB)
    return strip


class SubStrip(object):

    FADE = 'fade'
    STATIC = 'static'
    WAVE = 'wave'

    FORWARD = 1
    BACKWARD = 0

    def __init__(self, **kwargs):
        """ strip, start_pixel, end_pixel"""
        self.start_pixel = kwargs.get('start_pixel')
        self.end_pixel = kwargs.get('end_pixel')  # inclusive
        self.num_pixels = self.end_pixel - self.start_pixel + 1
        self.strip = kwargs.get('strip')
        self.fade_factor = 0.8
        self.activation_brightness = 0.9
        self.brightness = 0.0
        self.hue = 0.5
        self.sat = kwargs.get('sat', 1.0)
        self.update_type = kwargs.get('update_type', SubStrip.FADE)
        self.hue_list = kwargs.get('hue_list', [])
        self.upper_hue = kwargs.get('upper_hue', None)
        self.lower_hue = kwargs.get('lower_hue', None)
        self.direction = SubStrip.FORWARD

    @staticmethod
    def get_directed_range(start, end, direction):
        """Inclusive range, with a direction"""
        if direction == SubStrip.BACKWARD:
            return range(end, start - 1, -1)
        else:
            return range(start, end + 1, 1)

    def get_pixel_range(self):
        return SubStrip.get_directed_range(start=self.start_pixel, end=self.end_pixel, direction=self.direction)

    def all_to_hsv(self, hue, sat, val):
        """Set all pixels in substrip to the same color"""
        rgb_norm = hsv_to_rgb(hue, sat, val)
        rgb = [int(el*255) for el in rgb_norm]
        for pix in self.get_pixel_range():
            self.strip.setPixelColorRGB(pix, *rgb)

    def pick_hue(self):
        if self.hue_list:
            hue = random.choice(self.hue_list)
        elif self.upper_hue and self.lower_hue:
            hue = random.uniform(self.lower_hue, self.upper_hue)
        else:
            hue = random.random()

        print(f"   hue: {hue:0.3f}     --- start: {self.start_pixel}, end: {self.end_pixel}")
        return hue

    def activate(self):
        # set to random hue at mid-brightness
        random_hue = self.pick_hue()
        self.hue = random_hue
        self.brightness = self.activation_brightness
        self.all_to_hsv(random_hue, self.sat, self.brightness)

    def deactivate(self):
        # set to dark
        self.brightness = 0.0
        self.all_to_hsv(self.hue, self.sat, self.brightness)

    def update(self):

        if self.update_type == SubStrip.FADE and self.brightness:
            self.brightness *= self.fade_factor
            self.all_to_hsv(self.hue, self.sat, self.brightness)
            #print(self.brightness)
