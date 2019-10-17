#!/usr/bin/env python3
import RPi.GPIO as GPIO
import asyncio
import os
import sys
import json
from random import randint

from box import Box



# local imports
#sys.path.insert(0, "../treechipi")
#sys.path.insert(0, "../fancy")


from neopixel import *
from treechipi.touch_play import TouchPlay, create_from_box, assign_led_strips, configure_sensor_objects
from treechipi.tree_strip import get_default_tree_strip, TreeStrip

debug = True


# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Disable Warnings

# Set up input GPIO pins
#from treechipi.constants import touch_input_pins, prox_input_pins, relay_output_pins

# Set up relay output GPIO pins and set them to off
#relay_output_pins = [22, 23, 24]
# for i in relay_output_pins:
#     GPIO.setup(i, GPIO.OUT)
#     GPIO.output(i, False)


# Set up input GPIO pins
#touch_input_pins = [5, 7, 9, 11]
# for pin in touch_input_pins:
#     GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#prox_input_pins = [6, 8, 10, 12]
# for pin in prox_input_pins:
#     GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

home_dir = '/home/pi/'
#home_dir = './'
sdir = '{}media'.format(home_dir)
config_stub = 'config_hue_01'
config_file = f'./{config_stub}.json'.format(config_stub)

def files_from_dir(d, wd=None):
    if not wd:
        wd = sdir
    #print wd
    return [wd + '/' + d+'/'+ f for f in os.listdir(wd + '/' + d)]


touchSensors = []

touch_check_interval = 0.3
led_update_interval = 0.02


async def touch_check(event_loop, touch_sensor_list):
    while True:
        await asyncio.sleep(touch_check_interval)

        for s in touch_sensor_list:
            s.check_new(event_loop)


async def ongoing_update(strips):
    while True:
        await asyncio.sleep(strips[0].update_interval)
        for current_strip in strips:
            for substrip in getattr(current_strip, 'substrips'):
                substrip.update()
            current_strip.update()


# Main program logic follows:
if __name__ == '__main__':

    # # get configuration, read file
    # with open('/home/pi/treechipi/treechipi/config_07.json', 'r') as myfile:
    #     data = myfile.read()


    # strip 1 on PWM0
    strip = get_default_tree_strip(data_pin=18, num_pixels=200)
    strip.index = 0
    strip.begin()
    strip.update_interval = led_update_interval
    print("LED strip initialized...\n")

    # strip 2 on PWM1
    strip2 = get_default_tree_strip(data_pin=19, num_pixels=100, channel=1)
    strip2.index = 1
    strip2.begin()
    strip2.update_interval = led_update_interval
    print("LED strip 2 initialized...\n")

    #strips = [strip, strip2]
    strips = [strip]

    # # configure sensor objects
    # config_dict_list = json.loads(data)
    # config_box_list = [Box(d) for d in config_dict_list]
    # touchSensors = [create_from_box(b) for b in config_box_list]
    #
    # assign_led_strips(touch_sensor_list=touchSensors, strip_list=strips)

    touch_sensors = configure_sensor_objects(config_file_path=config_file, strip_list=strips)

    loop = asyncio.get_event_loop()
    try:
        print('task creation started...')
        loop.create_task(ongoing_update(strips))
        loop.create_task(touch_check(loop, touch_sensor_list=touch_sensors))
        loop.run_forever()
    finally:
        loop.close()
