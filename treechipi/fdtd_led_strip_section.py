
import numpy as np
from copy import deepcopy

from collections import deque
import webcolors
import sys
import random

from .led_strip_section import SubStrip
from fdtd.fdtd import FDTD1D
from colorsys import hsv_to_rgb


class FDTDSubStrip(SubStrip):

    FDTD = 'fdtd'

    def __init__(self, **kwargs):
        """ strip, start_pixel, end_pixel"""
        super(FDTDSubStrip, self).__init__(**kwargs)
        self.fdtd_speed = kwargs.get('fdtd_speed', 0.25)
        self.fdtd = FDTD1D(ke=self.num_pixels, cc=self.fdtd_speed)
        self.fdtd.threshold = 0.2
        self.e0 = 0.0

    def set_pixels_from_ex_slow(self):

        for pix in self.get_pixel_range():

            if self.direction == SubStrip.FORWARD:
                ind = pix - self.start_pixel
            else:
                ind = self.end_pixel - pix

            ex_val = self.fdtd.ex[ind]
            if ex_val > 0:
                pix_val = ex_val
            else:
                pix_val = 0
            rgb_norm = hsv_to_rgb(self.hue, self.sat, pix_val)
            rgb = [int(el * 255) for el in rgb_norm]
            self.strip.setPixelColorRGB(pix, *rgb)

    def activate(self):
        print("FDTD activated")
        random_hue = self.pick_hue()
        self.hue = random_hue
        self.brightness = self.activation_brightness

    def update_fdtd(self, e0, threshold=0.01):
        self.fdtd.step_slow(e0=e0)
        self.set_pixels_from_ex_slow()

    def update(self):

        if self.update_type == FDTDSubStrip.FDTD:
            e0 = self.brightness
            self.brightness *= self.fade_factor
            self.update_fdtd(e0)

        else:
            super(FDTDSubStrip, self).update()

