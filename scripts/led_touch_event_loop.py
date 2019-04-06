#!/usr/bin/env python3
import os
import RPi.GPIO as GPIO
import asyncio

# local imports
import sys
#sys.path.insert(0, "../treechipi")
#sys.path.insert(0, "../fancy")


from neopixel import *
from treechipi.touch_play import TouchPlay
from treechipi.tree_strip import TreeStrip, get_default_tree_strip

debug = True


# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Disable Warnings


# Set up relay output GPIO pins and set them to off
relay_output_pins = [22, 23]
for i in relay_output_pins:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, False)


# Set up input GPIO pins
input_pins = [5, 6, 2, 3]
for pin in input_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


sdir = '/home/pi/media'


def filesFromDir(d, wd=None):
    if not wd:
        wd = sdir
    #print wd
    return [wd + '/' + d+'/'+ f for f in os.listdir(wd + '/' + d)]


touchSensors = []
p1 = TouchPlay(5, filesFromDir('p1'), timeout=9, sustain=True)
#p2 = TouchPlay(16, filesFromDir('p2'), timeout=20, sustain=True)

t2 = TouchPlay(17, filesFromDir('t2'), timeout=5, sustain=False)
t2.minimum_interval = 6
t2.relay_output_pin = relay_output_pins[0]
t2.relay_output_duration = 4

t2.led_enabled = True
t2.base_color = Color(99, 22, 22)
t2.active_color = Color(9, 92, 92)

if debug:
    t2.mock = True
    t2.mock_period = 5

touchSensors.append(p1)
touchSensors.append(t2)


async def touch_check(event_loop):
    while True:
        await asyncio.sleep(0.6)
        print("Checking touch pins")
        for s in touchSensors:
            s.check_new(event_loop)


led_update_period = 0.2


async def ongoing_update(strip):
    while True:
        await asyncio.sleep(led_update_period)
        #print(f"Updating strip {strip.base_color}")
        strip.update()


# Main program logic follows:
if __name__ == '__main__':

    strip = get_default_tree_strip(data_pin=18, num_pixels=100)
    strip.begin()
    print("OK")

    t2.led_strip = strip

    loop = asyncio.get_event_loop()

    try:
        print('task creation started...')
        loop.create_task(ongoing_update(strip))
        loop.create_task(touch_check(loop))
        loop.run_forever()
    finally:
        loop.close()
