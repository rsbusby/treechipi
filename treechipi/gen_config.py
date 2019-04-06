
from box import Box
import json
from copy import deepcopy

# Set up input GPIO pins
touch_input_pins = [23, 12, 20, 27, 7, 14]
prox_input_pins = [24, 16, 21, 22, 8, 15]
relay_output_pins = [5, 6, 13, 19, 10, 9]

shared_base_color_rgb = (0, 40, 12)

touch_config_list = []

tc = Box()

# touch

for pin_index in range(0, 1):
    index = pin_index + 1
    tc.pin = touch_input_pins[pin_index]
    tc.dir = f't{index}'
    tc.timeout = 5
    tc.sustain = False
    tc.minimum_interval = 10
    tc.relay_output_pin = relay_output_pins[pin_index]
    tc.relay_output_duration = 6
    tc.led_enabled = False
    tc.base_color = shared_base_color_rgb
    tc.active_color_rgb = (0, 0, 77)
    tc.mock = False
    tc.mock_period = 20
    touch_config_list.append(tc)

t1 = touch_config_list[0]
t1.led_enabled = True
t1.active_color_string = 'purple'

try:
    t2 = touch_config_list[1]
    t2.led_enabled = True
    t2.active_color_rgb = (0, 40, 40)
except:
    pass


# touch_config_list.append(t1b)
#
#
# # t1b
# t1b.pin = touch_input_pins[0]
# t1b.dir = 't1'
# t1b.timeout = 5
# t1b.sustain = False
# t1b.minimum_interval = 10
# t1b.relay_output_pin = relay_output_pins[0]
# t1b.relay_output_duration = 6
# t1b.led_enabled = True
# t1b.base_color = shared_base_color_rgb
# t1b.active_color_rgb = (0, 0, 77)
# t1b.mock = True
# t1b.mock_period = 20
#
# touch_config_list.append(t1b)
#
# #print(json.dumps(t1b.to_dict(), indent=True))
#
# # t2
# index = 2
# pin_index = index - 1
# t2b = deepcopy(t1b)
# t2b.dir = f't{index}'
# t2b.pin = touch_input_pins[pin_index]
# t2b.relay_output_pin = relay_output_pins[pin_index]
# t2b.led_enabled = True
# t2b.active_color_rgb = (0, 0, 77)
# touch_config_list.append(t2b)
#
# # t3
# index = 3
# pin_index = index - 1
# t3b = deepcopy(t1b)
# t3b.dir = f't{index}'
# t3b.pin = touch_input_pins[pin_index]
# t3b.relay_output_pin = relay_output_pins[pin_index]
# t3b.led_enabled = False
# t3b.active_color_rgb = (0, 99, 0)
#
# touch_config_list.append(t3b)
#
# # t4
# index = 4
# pin_index = index - 1
# t4b = deepcopy(t1b)
# t4b.dir = 't2' #f't{index}'
# t4b.pin = touch_input_pins[pin_index]
# t4b.relay_output_pin = relay_output_pins[pin_index]
#
# touch_config_list.append(t4b)

json_string = json.dumps([b.to_dict() for b in touch_config_list], indent=True)

with open('/home/pi/treechipi/treechipi/config_04.json', 'w') as myfile:
    myfile.write(json_string)