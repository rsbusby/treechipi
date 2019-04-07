
import RPi.GPIO as GPIO
import asyncio

from time import sleep 
import os
from random import randint

import subprocess
import pydub
from pydub import AudioSegment
from pydub.playback import play
from datetime import datetime
import random

from treechipi.tree_colors import *
from treechipi.tree_strip import TreeStrip


sdir = '/home/pi/media'


def files_from_dir(d, wd=None):
    if not wd:
        wd = sdir
    #print wd
    return [wd + '/' + d+'/'+ f for f in os.listdir(wd + '/' + d)]


def create_from_box(b):
    """ Use python-box dict to set up an object
    :param
    :return:
    """


    touch_play = TouchPlay(b.pin, files_from_dir(b.dir), timeout=b.timeout, sustain=b.sustain)
    touch_play.minimum_interval = b.minimum_interval
    touch_play.relay_output_pin = b.relay_output_pin
    touch_play.relay_output_duration = b.relay_output_duration

    touch_play.led_enabled = b.led_enabled

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

    print(f'Setting up input sensor for pin {b.pin}, directory {b.dir}')
    print(f'relay: {touch_play.relay_output_pin}')
    print(f'led: {touch_play.led_enabled}')
    return touch_play


class TouchPlay(object):

    def __init__(self, pin, fileList, duration = None, timeout=20, sustain=False, vol=0):

        self.verbosity = 1
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
            self.fileDict[f] = self.get_length(f)
        self.wavFile = self.get_file()
        print(self.wavFile)
        self.set_length()
        self.iter = 0
        self.pos = 0        
        self.playing = False
        self.startTime = None
        self.lastTime = datetime.now()
        self.length = None

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

        self.event_loop = None

    def get_length(self, soundFile):
        sound1 = AudioSegment.from_file(soundFile, format="wav")
        length = sound1.duration_seconds
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
        choice = random.choice(list(self.fileDict.keys()))
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

    async def trigger_led(self):
        """
        Trigger LED strip for a bit
        """
        self.led_on()
        await asyncio.sleep(self.relay_output_duration)
        self.led_off()

    def led_on(self):
        """
        Trigger LED strip on
        """
        print(f'{self.pin} LED is active! color to {self.active_color}')
        self.led_strip.target_base_color = self.active_color
        self.led_strip.target_pixel = self.led_strip.num_pix - 2
        self.led_active = True
        self.led_strip.is_active = True

    def led_off(self):
        """
        Trigger LED strip off
        """
        self.led_active = False
        self.led_strip.target_base_color = self.base_color
        self.led_strip.target_pixel = 2
        self.led_strip.is_active = False


        print(f'{self.pin} LED is inactive, color to {self.base_color}')

    async def trigger_relay(self):
        """
        Trigger relay for a bit
        """
        self.relay_active = True
        GPIO.output(self.relay_output_pin, True)
        if self.verbosity:
            print(f'{self.pin} starting relay on output pin {self.relay_output_pin}')

        await asyncio.sleep(self.relay_output_duration)

        GPIO.output(self.relay_output_pin, False)
        self.relay_active = False
        if self.verbosity:
            print(f'{self.pin} stopping relay on output pin {self.relay_output_pin}')

    def check_new(self, event_loop):
        """ signal of zero is active """

        if self.minimum_interval:
            now = datetime.now()
            interval = now - self.lastTime
            interval_seconds = interval.seconds

            if not (interval_seconds > self.minimum_interval):
                if self.verbosity:
                    print(f"{self.pin} pin waiting {self.minimum_interval - interval_seconds}")
                return
            else:
                if self.verbosity:
                    #print(f"{self.pin} processing, {interval_seconds} {self.minimum_interval}")
                    pass

        if self.mock:
            sense_val = randint(0, self.mock_period)
        else:
            #sense_val = 1
            pass
            sense_val = GPIO.input(self.pin)
            if self.verbosity:
                print(f" Checking {self.pin}  val {sense_val} ")

        # optionally turn off LED color when input is not active
        # if self.led_off_when_signal_off
        #     if sense_val and self.led_enabled and self.led_active:
        #         self.led_off()

        if not sense_val:
            # sensor is active
            if self.verbosity:
                print(f'{self.pin} is active')

            if self.relay_output_pin and not self.relay_active:
                event_loop.create_task(self.trigger_relay())
            if self.led_enabled and not self.led_active and not self.led_strip.is_active:
                self.led_active = True
                self.led_strip.is_active = True
                event_loop.create_task(self.trigger_led())

        self.process_audio_signal(sense_val)

    def start_sound(self, start_time):

        if self.pos <= 0 or self.pos >= self.length:
            self.wavFile = self.get_file()
            self.set_length()
        if self.wavFile:
            if self.pos <= 0 and not self.sustain:
                #cmd = f'omxplayer --vol -1000 -o alsa:hw:1,0 {self.wavFile} &'
                cmd = f'aplay -D sysdefault:CARD=1 {self.wavFile} &'

                os.system(cmd)

                if self.verbosity:
                    print(cmd)
                    print(f"{self.pin} starting sound {self.wavFile}")  # + str(self.iter))
            else:
                posOpt = ''
                if self.pos:
                    posOpt = f" --pos {self.pos}"
                outStr = " > /dev/null 2>&1 "
                #cmd_omx = "omxplayer --no-osd " + self.wavFile + " " + posOpt + self.volOpt + outStr + " &"
                cmd_aplay = f'aplay -D sysdefault:CARD=1 {self.wavFile} &'
                os.system(cmd_aplay)
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
            #print("on")
            if not self.playing:
                self.start_sound(start_time=now)
                # if self.pos <= 0 or self.pos >= self.length:
                #     self.wavFile = self.get_file()
                #     self.set_length()
                # if self.wavFile:
                #     if self.pos <= 0 and not self.sustain:
                #         os.system("omxplayer " + self.wavFile + " &")
                #         print(f"{self.pin} starting aplay {self.wavFile}")  # + str(self.iter))
                #     else:
                #         posOpt = ''
                #         if self.pos:
                #             posOpt = f" --pos {self.pos}"
                #         outStr = " > /dev/null 2>&1 "
                #         os.system("omxplayer --no-osd " + self.wavFile + " " + posOpt + self.volOpt + outStr + " &")
                #         print(f"{self.pin} starting {self.wavFile} with omx, for {self.length} seconds")  # + str(self.iter)
                #         # adjust pos because omxplayer takes a while to start
                #         self.pos = self.pos - 1.5
                #     # now = datetime.now()
                #     self.lastTime = now
                #     self.playing = True
                #     self.startTime = now

            else:  # self.playing == True
                # already playing, keep going
                # update the sustain if needed
                if self.sustain:
                    self.lastTime = now

                if self.verbosity:
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
