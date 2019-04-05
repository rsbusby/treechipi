#!/usr/bin/env python3

import RPi.GPIO as GPIO

import asyncio
import os
from treechipi.touch_play import TouchPlay

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
t2.minimum_interval = 11
t2.relay_output_pin = relay_output_pins[0]
t2.relay_output_duration = 4
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


# Main program logic follows:
if __name__ == '__main__':


    #sound_file = touchSensors[0].fileList[0]

    #asyncio.run(play(sound_file))

    # subprocess.Popen('omxplayer /home/pi/media/p1/23Secs_RainScapeWInsects.aif',
    #                   stderr=subprocess.STDOUT, shell=True)

    loop = asyncio.get_event_loop()

    try:
         print('task creation started...')
         loop.create_task(touch_check(loop))
         loop.run_forever()
    finally:
         loop.close()
