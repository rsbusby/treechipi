#!/usr/bin/env python3

import RPi.GPIO as GPIO

import asyncio
import os
from touch_play import TouchPlay

import pydub

GPIO.setmode(GPIO.BCM)

# Set up GPIO pins
# 4 inputs
#pins = [5, 6, 13, 19, 26, 2, 3, 4, 17]

pins = [5, 6, 2, 3]

for pin in pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

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

touchSensors.append(p1)
touchSensors.append(t2)



async def seconds():
    while 1:
        for i in range(8):
            await asyncio.sleep(1)
            print("sev")


async def slower():
    while 1:
        for i in range():
            await asyncio.sleep(2.2)
            print("slow")


async def touch_check():
    for s in touchSensors:
        s.check()


async def play():
    print('Subprocess playing')
    proc = await asyncio.create_subprocess_exec('sleep', '5')
    returncode = await proc.wait()
    print('Subprocess done sleeping.  Return code = %d' % returncode)


async def play(sound_file):
    proc = await asyncio.create_subprocess_shell(
        "omxplayer {}".format(sound_file),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{sound_file!r} exited with {proc.returncode}]')
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')

#asyncio.run(run('ls /zzz'))


async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')


async def do_subprocess():
    print('Subprocess sleeping')
    proc = await asyncio.create_subprocess_exec('sleep', '5')
    returncode = await proc.wait()
    print('Subprocess done sleeping.  Return code = %d' % returncode)




async def sleep_report(number):
    for i in range(number + 1):
        print('Slept for %d seconds' % i)
        await asyncio.sleep(1)


# Main program logic follows:
if __name__ == '__main__':

    #asyncio.run(run('ls /zzz'))

    sound_file = touchSensors[0].fileList[0]

    #asyncio.run(play(sound_file))

    while True:

        for s in touchSensors:
            s.check_new()

    # subprocess.Popen('omxplayer /home/pi/media/p1/23Secs_RainScapeWInsects.aif',
    #                   stderr=subprocess.STDOUT, shell=True)

    #loop = asyncio.get_event_loop()



    # try:
    #     print('task creation started')
    #     loop.create_task(seconds())
    #     loop.create_task(slower())
    #     loop.create_task(do_subprocess())
    #     loop.create_task(sleep_report(5))
    #     #loop.create_task(touch_check)
    #     loop.run_forever()
    # finally:
    #     loop.close()
