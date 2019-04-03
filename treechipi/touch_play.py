

import RPi.GPIO as GPIO

import asyncio

from time import sleep 
import os

#import commands
import subprocess
import pydub
from pydub import AudioSegment
from pydub.playback import play
from datetime import datetime
import random
from math import floor


class TouchPlay(object):

    def __init__(self, pin, fileList, duration = None, timeout=20, sustain=False, vol=0):
        self.fileList = fileList
        self.pin = pin
        self.timeout = timeout
        self.sustain = sustain
        self.vol = vol
        if self.vol:
            self.volOpt = " --vol " + str(vol)
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


    def get_length(self, soundFile):
        sound1 = AudioSegment.from_file(soundFile, format="aiff")
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
        print("Picking " + choice)
        return choice

    def append_pos(self, delta):
        sec = float(str(delta).split(':')[-1].lstrip('0'))
        self.pos = float(self.pos) + float(sec)
        #print str(self.pos) + "  "  + str(self.length)
        if self.pos > self.length:
            self.pos = 0
            
    def kill_sound(self):
        ''' stop playing '''
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

    def check_new(self):
        """
        :return: Check GPIO and play sounds
        """
        #print(str(self.pin) + " " + str(GPIO.input(self.pin))   + "  pos: " + str(self.pos)  + " " + str(self.iter))
        #self.iter += 1
        sleep(0.4)
        from random import randint

        sense_val = randint(0, 20) #GPIO.input(self.pin)

        # get time
        now = datetime.now()
        if self.playing:
            delta = now - self.startTime
            if delta.total_seconds() > self.length:
                self.playing = False
                self.pos = 0
                self.startTime = None

        # if signal present

        if sense_val == 0:
            print("on")
            if not self.playing:
                if self.pos <= 0 or self.pos >= self.length:
                    self.wavFile = self.get_file()
                    self.set_length()
                if self.wavFile:
                    if self.pos <= 0 and not self.sustain:
                        os.system("omxplayer " + self.wavFile + " &")
                        print("starting " + self.wavFile + " ")  # + str(self.iter))
                    else:
                        posOpt = ''
                        if self.pos:
                            posOpt = " --pos " + str(self.pos)
                        outStr = " > /dev/null 2>&1 "
                        os.system("omxplayer --no-osd " + self.wavFile + " " + posOpt + self.volOpt + outStr + " &")
                        print(f"starting {self.wavFile} with omx, for {self.length} seconds")  # + str(self.iter)
                        # adjust pos because omxplayer takes a while to start
                        self.pos = self.pos - 1.5
                    # now = datetime.now()
                    self.lastTime = now
                    self.playing = True
                    self.startTime = now

            else:
                print(f"{self.wavFile} still playing")

            if self.playing and self.sustain:
                self.lastTime = now

        else:  # senseVal == 1:
            # If sustaining, but no recent trigger, then stop sound.
            if self.sustain and self.playing:
                # now = datetime.now()
                delta = now - self.lastTime
                # print str(self.pin) + " " + str(self.timeout - delta.total_seconds())
                if delta.total_seconds() > self.timeout:
                    self.append_pos(delta)
                    self.kill_sound()
                    print(str(self.pin) + " killed at " + str(self.pos))
                    self.lastTime = now


    def check(self):

        #print str(self.pin) + " " + str(GPIO.input(self.pin))   + "  pos: " + str(self.pos)  + " " + str(self.iter)
        #self.iter += 1

        senseVal = GPIO.input(self.pin)
     	# if signal present
        now = datetime.now()
        if self.playing:
            delta = now - self.startTime
            if delta.total_seconds() > self.length:
                self.playing = False
                self.pos = 0
                self.startTime = None


        if senseVal == 0:
            #print "on"
            if not self.playing:
                if self.pos <= 0 or self.pos >= self.length:
                    self.wavFile = self.get_file()
                    self.set_length()
                if self.wavFile:
                    if self.pos <= 0 and not self.sustain:
                        os.system("aplay " + self.wavFile + " &")
                        print("starting " + self.wavFile + " ") #+ str(self.iter))
                    else:
                        posOpt = ''
                        if self.pos:
                            posOpt = " --pos " + str(self.pos)
                        outStr = " > /dev/null 2>&1 "
                        os.system("omxplayer --no-osd " + self.wavFile + " " + posOpt + self.volOpt + outStr + " &")
                        print("starting " + self.wavFile + " with omx ") #+ str(self.iter)
                        # adjust pos because omxplayer takes a while to start
                        self.pos = self.pos - 1.5
                    #now = datetime.now()
                    self.lastTime = now
                    self.playing = True
                    self.startTime = now

            if self.playing and self.sustain:
                self.lastTime = now

        else: # senseVal == 1:
            # If sustaining, but no recent trigger, then stop sound.
            if self.sustain and self.playing:
                #now = datetime.now()
                delta = now - self.lastTime
                #print str(self.pin) + " " + str(self.timeout - delta.total_seconds())
                if delta.total_seconds() > self.timeout:
                    self.append_pos(delta)
                    self.kill_sound()
                    print(str(self.pin) + " killed at " + str(self.pos))
                    self.lastTime = now


