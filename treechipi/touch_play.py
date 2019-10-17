
import RPi.GPIO as GPIO
import asyncio

from time import sleep 
import os
from random import randint
import json

import subprocess
import pydub
from pydub import AudioSegment
from pydub.playback import play
from datetime import datetime
import random
from box import Box

import collections
import itertools


from treechipi.tree_colors import *
from treechipi.tree_strip import TreeStrip
from treechipi.led_strip_section import SubStrip
from treechipi.fdtd_led_strip_section import FDTDSubStrip


sdir = '/home/pi/media'


def files_from_dir(d, wd=None):
    if not wd:
        wd = sdir
    #print wd
    return [wd + '/' + d+'/'+ f for f in os.listdir(wd + '/' + d)]


def files_from_dir_recursive(d, wd=None):
    if not wd:
        wd = sdir
    base_dir = f'{wd}/{d}'
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(base_dir):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]

    return listOfFiles


def create_from_box(b, verbosity=1):
    """ Use python-box dict to set up an object
    :param
    :return:
    """

    if verbosity > 2:
        print(b.to_json(indent=True))

    touch_play = TouchPlay(b.pin, files_from_dir_recursive(b.dir), timeout=b.timeout, sustain=b.sustain)

    GPIO.setup(touch_play.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    try:
        touch_play.strip_config = b.strip_config
    except:
        print(f'No LED strip configuration for {b.dir}')

    touch_play.minimum_interval = b.minimum_interval
    touch_play.relay_output_pin = b.relay_output_pin
    if touch_play.relay_output_pin:
        GPIO.setup(touch_play.relay_output_pin, GPIO.OUT)
        GPIO.output(touch_play.relay_output_pin, False)

    touch_play.relay_output_duration = b.relay_output_duration

    touch_play.name = b.get('name', 'noname')

    touch_play.led_enabled = b.led_enabled

    touch_play.verbosity = b.get('verbosity', 0)
    if touch_play.verbosity > 1:
        touch_play.out_string = " &"

    br = None
    bcs = b.get('base_color_string', None)
    if bcs:
        try:
            br = webcolors.name_to_rgb(bcs)
        except:
            print(f"color {bcs} not found")
            br = None
    if not br:
        br = b.get('base_color_rgb', None)
    if br:
        touch_play.base_color = TreeStrip.rgb_to_color(br)

    ar = None
    acs = b.get('active_color_string', None)
    if acs:
        try:
            ar = webcolors.name_to_rgb(acs)
        except:
            print(f"color {acs} not found")
            ar = None
    if not ar:
        ar = b.get('active_color_rgb', None)
    if ar:
        touch_play.active_color = TreeStrip.rgb_to_color(ar)

    touch_play.mock = b.get('mock', True)
    touch_play.mock_period = b.get('mock_period', 20)

    if touch_play.mock:
        print(f"*** mocking {touch_play.pin}, period {touch_play.mock_period} ***")

    touch_play.led_off_when_signal_off = not touch_play.mock

    print(f'Setting up input sensor for pin {b.pin}, directory {b.dir}, name {touch_play.name}')
    print(f'relay: {touch_play.relay_output_pin}')
    print(f'led: {touch_play.led_enabled}')

    return touch_play


def assign_led_strips(touch_sensor_list, strip_list):
    """ Given JSON configuration, set up one or more sub-strips to be associated with sensor activation"""
    STRIP_INDEX_KEY = 'strip_index'

    for touch_sensor in touch_sensor_list:
        try:
            touch_sensor.substrips = []
            strip_config_dict_list = touch_sensor.strip_config
            for substrip_config in strip_config_dict_list:
                strip_index = substrip_config[STRIP_INDEX_KEY]
                strip = strip_list[strip_index]
                start_pixel = substrip_config['start_pixel']
                end_pixel = substrip_config['end_pixel']
                direction = substrip_config['direction']
                update_type = substrip_config.get('update_type', SubStrip.FADE)
                if update_type == FDTDSubStrip.FDTD:
                    substrip = FDTDSubStrip(strip=strip, **substrip_config.to_dict())
                else:
                    substrip = SubStrip(strip=strip, **substrip_config.to_dict())
                try:
                    substrip.update_type = update_type
                except:
                    pass

                touch_sensor.substrips.append(substrip)
                strip.substrips.append(substrip)
                print(f"Added substrip of type {update_type} to touch sensor {touch_sensor.name}, "
                      f"strip {substrip_config[STRIP_INDEX_KEY]}, "
                      f"start {start_pixel}, end {end_pixel}, direction {direction}")
        except (AttributeError, KeyError) as e:
            print(e)
            print("Error configuring LED sub-strip for touch sensor {}".format(touch_sensor.name))
            continue


def configure_sensor_objects(strip_list, config_file_path):
    # configure sensor objects

    # get configuration, read file
    with open(config_file_path, 'r') as myfile:
        data = myfile.read()

    config_dict_list = json.loads(data)
    config_box_list = [Box(d) for d in config_dict_list]
    touch_sensors = [create_from_box(b) for b in config_box_list]

    assign_led_strips(touch_sensor_list=touch_sensors, strip_list=strip_list)
    return touch_sensors

class TouchPlay(object):

    def __init__(self, pin, fileList, duration = None, timeout=20, sustain=False, vol=0, name='unnamed'):

        self.verbosity = 0
        self.name = name
        self.fileList = fileList

        self.pin = pin

        self.timeout = timeout
        self.sustain = sustain
        self.minimum_interval = None
        self.vol = vol
        if self.vol:
            self.volOpt = f" --vol {self.vol}"
        else:
            self.volOpt = ''

        self.fileDict = {}
        for f in self.fileList:
            length = self.get_length(f)
            self.fileDict[f] = length

        self.file_generator = itertools.cycle(self.fileList)

        self.wavFile = self.get_file()
        print(self.wavFile)

        self.out_string = "> /dev/null 2>&1 &"

        self.set_length()
        self.iter = 0
        self.pos = 0        
        self.playing = False
        self.startTime = None
        self.lastTime = datetime.now()
        self.length = None
        self.is_active = False

        # relay output
        self.relay_enabled = True
        self.relay_output_pin = None
        self.relay_output_duration = 2
        self.relay_active = False

        # LED output
        self.led_enabled = False
        self.led_strip = None
        self.base_color = red
        self.active_color = purple
        self.led_active = False

        # testing
        self.mock = False
        self.mock_period = 20

        self.led_off_when_signal_off = not self.mock
        self.event_loop = None

    def get_length_pydub(self, soundFile):
        sound1 = AudioSegment.from_file(soundFile, format="wav")
        length = sound1.duration_seconds
        print(f"Length of {soundFile} in seconds is {length:.2f}")
        return length

    def get_length(self, soundFile):
        cmd = f'omxplayer {soundFile} --info > temp_length.txt'
        info = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode('utf-8')
        #print(info)
        suffix = info.split("Duration:")[-1]
        precomma = ''.join(suffix).split(',')[0]
        tt = ''.join(precomma).split(":")
        sec = float(tt[-1].lstrip('0'))
        minute_string = tt[-2].lstrip('0')
        if minute_string:
            minute_val = int(minute_string)
        else:
            minute_val = 0
        length = sec + minute_val * 60  # + tt[-3]*3600
        print(f"Length of {soundFile} in seconds is {length:.1f}")
        return length

    def set_length(self):
        if self.wavFile:
            self.length = self.fileDict[self.wavFile]
            return True
        return False

    def get_file(self):
        if not len(self.fileList):
            return None
        if len(self.fileList) == 1:
            return self.fileList[0]
        #choice = random.choice(list(self.fileDict.keys()))

        choice = next(self.file_generator)

        if self.verbosity:
            print("Picking " + choice)
        return choice

    def append_pos(self, delta):
        sec = float(str(delta).split(':')[-1].lstrip('0'))
        self.pos = float(self.pos) + float(sec)
        #print str(self.pos) + "  "  + str(self.length)
        if self.pos > self.length:
            self.pos = 0
            
    def kill_sound(self):
        """ stop playing """
        if self.verbosity:
            print(f"Killing {self.wavFile}")
        #psOut = subprocess.check_output('ps -ax | grep ' + self.wavFile, stderr=subprocess.STDOUT, shell=True)
        p = subprocess.Popen(f'ps -ax | grep {self.wavFile}', shell=True, stdout=subprocess.PIPE)
        print(f'{self.pin} killing')
        out, err = p.communicate()
        lines = out.decode("utf-8").split('\n')
        for line in lines:
            print(line)
            if not line:
                continue
            pid = line.split()[0].strip()
            if 'aplay' in line or 'omxplay' in line:
                print(f"Killing process {pid}")
                p = subprocess.Popen(f'kill -9 {pid}', shell=True, stdout=subprocess.PIPE)
        self.playing = False
        self.startTime = None

        if self.length - self.pos < float(self.length) / 4.0:
            self.pos = 0

    # async def play(sound_file):
    #     proc = await asyncio.create_subprocess_shell(
    #         "omxplayer {}".format(sound_file),
    #         stdout=asyncio.subprocess.PIPE,
    #         stderr=asyncio.subprocess.PIPE)
    #
    #     stdout, stderr = await proc.communicate()
    #
    #     print(f'[{sound_file!r} exited with {proc.returncode}]')
    #     if stdout:
    #         print(f'[stdout]\n{stdout.decode()}')
    #     if stderr:
    #         print(f'[stderr]\n{stderr.decode()}')

    # async def trigger_led(self):
    #     """
    #     Trigger LED strip for a bit
    #     """
    #     self.led_on()
    #     await asyncio.sleep(self.relay_output_duration)
    #     self.led_off()
    #
    # def led_on(self):
    #     """
    #     Trigger LED strip on
    #     """
    #     if self.verbosity:
    #         print(f'{self.pin} LED is active! color to {self.active_color}')
    #     self.led_strip.target_base_color = self.active_color
    #     self.led_strip.target_pixel = self.led_strip.num_pix - randint(2, 20)
    #     self.led_active = True
    #     self.led_strip.is_active = True
    #     self.led_strip.update_interval = 0.5
    #
    # def led_off(self):
    #     """
    #     Trigger LED strip off
    #     """
    #     self.led_active = False
    #     self.led_strip.target_base_color = self.base_color
    #     self.led_strip.target_pixel = randint(0, 10)
    #     self.led_strip.is_active = False
    #     self.led_strip.update_interval = 0.9
    #
    #     if self.verbosity:
    #         print(f'{self.pin} LED is inactive, color to {self.base_color}')

    async def trigger_led_substrip(self):
        """
        Trigger LED sub-strips for a bit
        """

        for substrip in self.substrips:
            print(f'sensor {self.pin} LED activated, strip {substrip.strip.index}, '
                  f'pixels {substrip.start_pixel} to {substrip.end_pixel}')
            substrip.activate()
        self.led_active = True

        #await asyncio.sleep(self.relay_output_duration)

        self.led_active = False
        #for substrip in self.substrips:
        #    substrip.deactivate()

    async def trigger_relay(self):
        """
        Trigger relay for a bit
        """
        self.relay_active = True
        GPIO.output(self.relay_output_pin, True)
        if self.verbosity > 1:
            print(f'{self.pin} starting relay on output pin {self.relay_output_pin}')

        await asyncio.sleep(self.relay_output_duration)

        GPIO.output(self.relay_output_pin, False)
        self.relay_active = False
        if self.verbosity > 1:
            print(f'{self.pin} stopping relay on output pin {self.relay_output_pin}')

    def check_new(self, event_loop):
        """ signal of zero is active """

        if self.minimum_interval:
            now = datetime.now()
            interval = now - self.lastTime
            interval_seconds = interval.seconds

            if not (interval_seconds > self.minimum_interval):
                if self.verbosity > 2:
                    print(f"{self.pin} pin waiting {self.minimum_interval - interval_seconds}")
                return
            else:
                if self.verbosity > 3:
                    print(f"{self.pin} processing, {interval_seconds} {self.minimum_interval}")
                    pass

        if self.mock:
            sense_val = randint(0, self.mock_period)
        else:
            sense_val = GPIO.input(self.pin)
            if self.verbosity > 3:
                print(f" Reading {self.pin} {self.name}  val: {sense_val} ")

        # optionally turn off LED color when input is not active
        if sense_val and self.led_enabled and self.led_active and self.led_off_when_signal_off:
            pass
            #self.led_off()

        if not sense_val and not self.is_active:
            # sensor is active
            if self.verbosity > 1:
                print(f'{self.pin} is active')

            if self.relay_output_pin and not self.relay_active:
                event_loop.create_task(self.trigger_relay())
            if self.led_enabled and not self.led_active:
                self.led_active = True
                #self.led_strip.is_active = True
                event_loop.create_task(self.trigger_led_substrip())

        self.process_audio_signal(sense_val)

        if sense_val:
            # avoid repetition
            self.is_active = False
        else:
            self.is_active = True

    def start_sound(self, start_time):

        if self.pos <= 0 or self.pos >= self.length:
            self.wavFile = self.get_file()
            self.set_length()
        if self.wavFile:
            if self.pos <= 0 and not self.sustain:
                #cmd = f'omxplayer --vol -1000 -o alsa:hw:1,0 {self.wavFile} &'
                cmd = f'aplay -D sysdefault:CARD=1 {self.wavFile} {self.out_string}'

                os.system(cmd)

                if self.verbosity > 1:
                    print(cmd)
                    print(f"{self.pin} starting sound {self.wavFile}")  # + str(self.iter))
            else:
                posOpt = ''
                if self.pos:
                    posOpt = f" --pos {self.pos}"
                outStr = " > /dev/null 2>&1 "
                #cmd_omx = "omxplayer --no-osd " + self.wavFile + " " + posOpt + self.volOpt + outStr + " &"
                cmd_aplay = f'aplay -D sysdefault:CARD=1 {self.wavFile} {self.out_string}'
                os.system(cmd_aplay)
                if self.verbosity > 2:
                    print(f"{self.pin} starting {self.wavFile} , for {self.length} seconds")  # + str(self.iter)
                # adjust pos because omxplayer takes a while to start
                self.pos = self.pos - 1.5
            # now = datetime.now()
            self.lastTime = start_time
            self.playing = True
            self.startTime = start_time

    def process_audio_signal(self, sense_val):
        """ Check GPIO and play sounds, signal of 0 is active """

        # get time
        now = datetime.now()

        # set state to not playing, if sound is done
        if self.playing:
            delta = now - self.startTime
            if delta.total_seconds() > self.length:
                self.playing = False
                self.pos = 0
                self.startTime = None

        # process input
        if sense_val == 0:
            # input is active

            if not self.playing:
                if not self.is_active:
                    self.start_sound(start_time=now)

            else:  # self.playing == True
                # already playing, keep going
                # update the sustain if needed
                if self.sustain:
                    self.lastTime = now

                if self.verbosity > 1:
                    print(f"{self.pin} {self.wavFile} still playing")

        else:  # senseVal == 1:
            # input is not active
            # If sustaining, but no recent trigger, then stop sound.
            if self.sustain and self.playing:
                # now = datetime.now()
                delta = now - self.lastTime
                # print str(self.pin) + " " + str(self.timeout - delta.total_seconds())
                if delta.total_seconds() > self.timeout:
                    self.append_pos(delta)
                    self.kill_sound()
                    print(f"{self.pin} killed at {self.pos}")
                    self.lastTime = now
