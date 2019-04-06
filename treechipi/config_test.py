
from neopixel import Color
from box import Box
import json
from copy import deepcopy

# Set up input GPIO pins
touch_input_pins = [5, 7, 9, 11]

prox_input_pins = [6, 8, 10, 12]

relay_output_pins = [22, 23, 24, 25]


shared_base_color_rgb = (55, 0, 0)

touch_config_list = []

t1b = Box()

t1b.pin = touch_input_pins[0]
t1b.dir = 't1'
t1b.timeout = 5
t1b.sustain = False
t1b.minimum_interval = 10
t1b.relay_output_pin = relay_output_pins[0]
t1b.relay_output_duration = 6
t1b.led_enabled = False
t1b.base_color = shared_base_color_rgb
t1b.active_color_rgb = (0, 0, 77)
t1b.mock = True
t1b.mock_period = 20

touch_config_list.append(t1b)

#print(json.dumps(t1b.to_dict(), indent=True))

index = 2
pin_index = index - 1
t2b = deepcopy(t1b)
t2b.dir = f't{index}'
t2b.pin = touch_input_pins[pin_index]
t2b.relay_output_pin = relay_output_pins[pin_index]
t2b.led_enabled = False
t2b.active_color_rgb = (0, 0, 77)

touch_config_list.append(t2b)

index = 3
pin_index = index - 1
t3b = deepcopy(t1b)
t3b.dir = f't{index}'
t3b.pin = touch_input_pins[pin_index]
t3b.relay_output_pin = relay_output_pins[pin_index]
t3b.led_enabled = False
t3b.active_color_rgb = (0, 99, 0)

touch_config_list.append(t3b)


index = 4
pin_index = index - 1
t4b = deepcopy(t1b)
t4b.dir = 't2' #f't{index}'
t4b.pin = touch_input_pins[pin_index]
t4b.relay_output_pin = relay_output_pins[pin_index]

touch_config_list.append(t4b)

#print(json.dumps([b.to_dict() for b in touch_config_list], indent=True))