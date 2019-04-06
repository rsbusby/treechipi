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
from treechipi.touch_play import TouchPlay, create_from_box
from treechipi.tree_strip import get_default_tree_strip, TreeStrip

debug = True


# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Disable Warnings

# Set up  GPIO pins
touch_input_pins = [23, 12, 20, 27, 7, 14]
prox_input_pins = [24, 16, 21, 22, 8, 15]
relay_output_pins = [5, 6, 13, 19, 10, 9]


# Set up relay output GPIO pins and set them to off
#relay_output_pins = [22, 23, 24]
for i in relay_output_pins:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, False)


# Set up input GPIO pins
#touch_input_pins = [5, 7, 9, 11]
for pin in touch_input_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#prox_input_pins = [6, 8, 10, 12]
for pin in prox_input_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

sdir = '/home/pi/media'


def files_from_dir(d, wd=None):
    if not wd:
        wd = sdir
    #print wd
    return [wd + '/' + d+'/'+ f for f in os.listdir(wd + '/' + d)]


touchSensors = []
#p1 = TouchPlay(prox_input_pins[0], files_from_dir('p1'), timeout=999, sustain=True)
#p2 = TouchPlay(16, filesFromDir('p2'), timeout=20, sustain=True)

shared_base_color = Color(55, 0, 0)

# b = Box()
# b.pin = touch_input_pins[0]
# b.dir = 't1'
# b.timeout=5
# b.sustain=False
# b.minimum_interval = 10
# b.relay_output_pin = relay_output_pins[0]
# b.relay_output_duration = 6
#
# b.led_enabled = False
# #b.base_color =
# #b.active_color =
#
# b.mock = True
# t1 = create_from_box(b=b)
#
# #
# #
# # # touch 1
# # t1 = TouchPlay(touch_input_pins[0], files_from_dir('t1'), timeout=5, sustain=False)
# # t1.minimum_interval = 2
# # t1.relay_output_pin = relay_output_pins[0]
# # t1.relay_output_duration = 5
# #
# # t1.led_enabled = False
# # t1.base_color = shared_base_color #Color(99, 0, 99)
# # t1.active_color = Color(92, 22, 0)
# #
# # if debug:
# #     t1.mock = True
# #     t1.mock_period = 20
#
# # touch 2
# t2 = TouchPlay(touch_input_pins[1], files_from_dir('t2'), timeout=5, sustain=False)
# t2.minimum_interval = 10
# t2.relay_output_pin = relay_output_pins[0]
# t2.relay_output_duration = 5
#
# t2.led_enabled = True
# t2.base_color = shared_base_color #Color(99, 0, 99)
# t2.active_color = Color(0, 0, 77)
#
# if debug:
#     t2.mock = True
#     t2.mock_period = 20
#
#
# # touch 3
# t3 = TouchPlay(touch_input_pins[2], files_from_dir('t3'), timeout=6, sustain=False)
# t3.minimum_interval = 10
# t3.relay_output_pin = relay_output_pins[2]
# t3.relay_output_duration = 5
#
# t3.led_enabled = True
# t3.base_color = shared_base_color #Color(99, 0, 0)
# t3.active_color = Color(0, 55, 0)
#
# if debug:
#     t3.mock = True
#     t3.mock_period = 20
#
# # touch 4
# t4 = TouchPlay(touch_input_pins[3], files_from_dir('t3'), timeout=6, sustain=False)
# t4.minimum_interval = 10
# t4.relay_output_pin = relay_output_pins[2]
# t4.relay_output_duration = 5
#
# t4.led_enabled = False
# #t4.base_color = shared_base_color #Color(99, 0, 0)
# #t4.active_color = Color(0, 55, 0)
#
# if debug:
#     t4.mock = True
#     t4.mock_period = 20

# touchSensors.append(p2)
# touchSensors.append(p3)
# touchSensors.append(p4)


#from treechipi.config_test import touch_config_list

#touchSensors = [create_from_box(b) for b in touch_config_list]

#touchSensors.append(p1)


# touchSensors.append(t1)
# touchSensors.append(t2)
# touchSensors.append(t3)
# touchSensors.append(t4)


touch_check_interval = 0.3333
led_update_interval = 0.01


async def touch_check(event_loop, touch_sensor_list):
    while True:
        await asyncio.sleep(touch_check_interval)

        for s in touch_sensor_list:
            s.check_new(event_loop)


async def ongoing_update(strip):
    while True:
        await asyncio.sleep(led_update_interval)
        #print(f"Updating strip {strip.base_color}")
        strip.update()


# Main program logic follows:
if __name__ == '__main__':


    # get configuration
    # read file
    with open('/home/pi/treechipi/treechipi/config_05.json', 'r') as myfile:
        data = myfile.read()

    # parse file
    config_dict_list = json.loads(data)
    config_box_list = [Box(d) for d in config_dict_list]
    touchSensors = [create_from_box(b) for b in config_box_list]
    #touchSensors.append(p1)
    print(len(touchSensors))


    # rand_rgb = (randint(0, 66), randint(0, 5), randint(0, 100))
    # print(f'\n\nrandom base: {rand_rgb}')
    # rand_base_color = TreeStrip.rgb_to_color(rand_rgb)
    # for tp in touchSensors:
    #     tp.base_color = rand_base_color

    strip = get_default_tree_strip(data_pin=18, num_pixels=200)
    strip.begin()
    print("LED strip initialized...\n")
    strip.base_color = touchSensors[0].base_color
    strip.all_to_base(skip_active=False, show=True)

    for tp in touchSensors:
        tp.led_strip = strip

    loop = asyncio.get_event_loop()

    try:
        print('task creation started...')
        loop.create_task(ongoing_update(strip))
        loop.create_task(touch_check(loop, touch_sensor_list=touchSensors))
        loop.run_forever()
    finally:
        loop.close()
        strip.base_color = Color(0, 0, 22)
        strip.all_to_base()