#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Disable Warnings

# Set up input GPIO pins
from treechipi.constants import touch_input_pins, prox_input_pins, relay_output_pins

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



# Main program logic follows:
if __name__ == '__main__':

    while True:
        for pin in touch_input_pins:
            sense_val = GPIO.input(pin)
            print("touch pin {}: {}".format(pin, sense_val))

        print()

        for pin in touch_input_pins:
            sense_val = GPIO.input(pin)
            print("prox pin {}: {}".format(pin, sense_val))

        print()

        time.sleep(1)