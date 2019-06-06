
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

    def __init__(self, **kwargs):
        """ strip, start_pixel, end_pixel"""
        self.start_pixel = kwargs.get('start_pixel')
        self.end_pixel = kwargs.get('end_pixel')
        self.strip = kwargs.get('strip')
        self.brightness = 0.0
        self.hue = 0.5
        self.update_type = kwargs.get('update_type', SubStrip.FADE)
        self.hue_list = kwargs.get('hue_list', [])

    def all_to_hsv(self, hue, sat, val):
        """Set all pixels in substrip to the same color"""
        rgb_norm = hsv_to_rgb(hue, sat, val)
        rgb = [int(el*255) for el in rgb_norm]
        for pix in range(self.start_pixel, self.end_pixel):
            self.strip.setPixelColorRGB(pix, *rgb)

    def pick_hue(self):
        if self.hue_list:
            return random.choice(self.hue_list)
        else:
            return random.random()

    def activate(self):
        # set to random hue at mid-brightness
        random_hue = self.pick_hue()
        self.hue = random_hue
        self.brightness = 0.5
        self.all_to_hsv(random_hue, 1.0, self.brightness)

    def deactivate(self):
        # set to dark
        self.brightness = 0.0
        self.all_to_hsv(self.hue, 1.0, self.brightness)

    def update(self):

        if self.update_type == SubStrip.FADE and self.brightness:
            self.brightness *= 0.92
            self.all_to_hsv(self.hue, 1.0, self.brightness)
            #print(self.brightness)
