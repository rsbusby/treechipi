
from box import Box
import json
from copy import deepcopy

# # Set up input GPIO pins
#from treechipi.constants import touch_input_pins, prox_input_pins, relay_output_pins

#touch_input_pins = [23, 26, 27, 20, 14, 2]


shared_base_color_rgb = (25, 0, 32)
shared_base_color_string = None

proximity_enabled = False

config_dir = '/home/pi/treechipi/treechipi'
#config_dir = '.'
config_stub = 'config_hue_01'

# Main program logic follows:
if __name__ == '__main__':

    touch_config_list = []
    prox_config_list = []

    mock_val = False
    verbosity = 1

    tc = Box()

    num_touch_sensors = 7

    # Create basic parameters for each touch sensor
    for pin_index in range(0, num_touch_sensors):
        index = pin_index + 1

        tc = deepcopy(tc)
        tc.verbosity = verbosity
        tc.vol = -2000
        #tc.pin = touch_input_pins[pin_index]
        tc.dir = f't{index}'
        tc.name = tc.dir
        tc.timeout = 16
        tc.sustain = False
        tc.minimum_interval = 0
        tc.relay_output_pin = None
        tc.relay_output_duration = 3
        tc.led_enabled = False
        #tc.base_color_rgb = shared_base_color_rgb
        #tc.active_color_rgb = (38, 30, 0)
        tc.mock = mock_val
        tc.mock_period = 12
        touch_config_list.append(tc)

    try:
        t1 = touch_config_list[0]
        t1.pin = 23
        t1.relay_output_pin = None
        t1.led_enabled = True
        t1.active_color_hue = 0.3
        tc.mock_period = 8


        # Configure LED strip(s)
        strip_config = Box()
        strip_config.strip_index = 0
        strip_config.start_pixel = 0
        strip_config.end_pixel = 50
        strip_config.update_type = 'static'
        strip_config.hue_list = [0.33, 0.39]
        t1.strip_config = [strip_config]
    except:
        pass

    try:
        t2 = touch_config_list[1]
        t2.pin = 26
        t2.led_enabled = True
        t2.relay_output_pin = None

        # Configure LED strip(s)
        strip_config = Box()
        strip_config.strip_index = 0
        strip_config.start_pixel = 51
        strip_config.end_pixel = 100
        t2.strip_config = [strip_config]
    except:
        pass

    try:
        t3 = touch_config_list[2]
        t3.pin = 27
        t3.led_enabled = True
        t3.relay_output_pin = None

        # Configure LED strip(s)
        strip_config = Box()
        strip_config.strip_index = 0
        strip_config.start_pixel = 101
        strip_config.end_pixel = 150
        t3.strip_config = [strip_config]

    except:
        pass

    try:
        t4 = touch_config_list[3]
        t4.pin = 20
        t4.led_enabled = True
        t4.relay_output_pin = None

        # Configure LED strip(s)
        strip_config = Box()
        strip_config.strip_index = 1
        strip_config.start_pixel = 0
        strip_config.end_pixel = 50
        t4.strip_config = [strip_config]
    except:
        pass

    try:
        t5 = touch_config_list[4]
        t5.pin = 22
        t5.led_enabled = True
        t5.relay_output_pin = None

        # Configure LED strip(s)
        strip_config = Box()
        strip_config.strip_index = 1
        strip_config.start_pixel = 50
        strip_config.end_pixel = 100
        t5.strip_config = [strip_config]
    except:
        pass

    try:
        t6 = touch_config_list[5]
        t6.pin = 2
        t6.led_enabled = True

        t6.minimum_interval = 0
        t6.mock_period = 7

        t6.active_color_hue = 0.6
        t6.relay_output_pin = None

        # Configure LED strip(s)
        strip_config = Box()
        strip_config.strip_index = 1
        strip_config.start_pixel = 101
        strip_config.end_pixel = 150
        t6.strip_config = [strip_config]
    except:
        pass

    try:
        t7 = touch_config_list[6]
        t7.pin = 24
        t7.led_enabled = False

        t7.minimum_interval = 3
        t7.mock_period = 17

        t7.relay_output_pin = 16

    except:
        pass


    # proximity
    for pin_index in range(0, 6):

        tc = deepcopy(tc)

        index = pin_index + 1

        tc.vol = -2000
        #tc.pin = prox_input_pins[pin_index]
        tc.dir = f'p{index}'
        tc.name = tc.dir
        tc.timeout = 120
        tc.sustain = True
        tc.minimum_interval = 289
        tc.relay_output_pin = None
        tc.relay_output_duration = 18
        tc.led_enabled = False
        tc.base_color = shared_base_color_rgb
        tc.active_color_rgb = (0, 0, 77)
        tc.mock = mock_val
        tc.mock_period = 1400
        prox_config_list.append(tc)

    try:
        p1 = prox_config_list[0]
        p1.minimum_interval = 67
    except Exception as e:
        pass

    try:
        p2 = prox_config_list[1]
        p2.minimum_interval = 51
    except Exception as e:
        pass

    try:
        p3 = prox_config_list[2]
        p3.minimum_interval = 41
    except Exception as e:
        pass

    try:
        p4 = prox_config_list[3]
        p4.minimum_interval = 243
    except Exception as e:
        pass

    try:
        p5 = prox_config_list[4]
        p5.minimum_interval = 393
    except Exception as e:
        pass

    try:
        p6 = prox_config_list[5]
        p6.minimum_interval = 31
    except Exception as e:
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

    if proximity_enabled:
        touch_config_list += prox_config_list

    json_string = json.dumps([b.to_dict() for b in touch_config_list], indent=True)



    with open('{}/{}.json'.format(config_dir, config_stub), 'w+') as myfile:
        myfile.write(json_string)


