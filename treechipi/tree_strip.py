
import asyncio

import time
from neopixel import *

update_period = 0.0004

from collections import deque
import webcolors
import sys
import random

from .tree_colors import *


class TreeStrip(Adafruit_NeoPixel):

    def __init__(self, *args, **kwargs):
        super(TreeStrip, self).__init__(*args, **kwargs)
        self.base_color = dark_orange  # Color(22, 0, 3)
        self.active_color = orange
        self.num_pix = self.numPixels()

        self.previous_index = 0
        self.target_pixel = 0
        self.active_pixel = 0
        self.old_pixel_stack = deque()
        self.explode_thresh = int(0.75 * self.num_pix)
        self.explode_color = name_to_color('aqua')
        self.next_explode_color = Color(0 ,0 ,5)
        self.exploding = False

    def set_pixel_color(self, pixel, color):
        i = self.num_pix - pixel
        self.setPixelColor(i, color)

    def all_to_base(self):
        for i in range(self.num_pix):
            self.set_pixel_color(i, self.base_color)

        # self.show()

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
        pixel_color = Color(22, 0, 0)
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

    def update(self):

        if self.active_pixel == self.target_pixel:
            return

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

        if self.active_pixel > self.explode_thresh:
            if not self.exploding:
                print("explode!")
                # self.explode(color=self.explode_color)
                self.exploding = True
        else:
            if self.exploding:
                # self.explode(self.base_color)
                self.exploding = False
                self.explode_pixels(Color(0, 0, 0))
            self.set_pixel_color(self.active_pixel, self.active_color)

        # self.dim_old_pixels()
        self.dim_pixel(self.previous_index)
        self.show()