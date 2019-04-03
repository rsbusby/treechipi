
from neopixel import *
import webcolors


def name_to_color(color_name):
    try:
        wc = webcolors.name_to_rgb(color_name)
        print(wc)
        return Color(wc[0], wc[1], wc[2])
    except Exception as e:
        print(e)
        return Color(0, 60, 0)


yellow_orange = Color(255, 215, 0)
purple = Color(160, 32, 240)
red = Color(200, 0, 0)
blue = Color(0, 0, 200)
light_gold = Color(244, 232, 104)
green = name_to_color('green')  # Color(88, 4, 4),
orange = Color(255, 110, 0)
dark_orange = Color(12, 8, 0)

palette_1 = {
    0: name_to_color('violet'),
    1: purple,
    2: green,
    3: Color(99, 66, 66),
    4: Color(66, 66, 66),
    5: green  # yellow_orange
}

sonar_color_dict_orig = {
    '20': Color(88, 4, 4),
    '30': Color(99, 66, 66),
    '40': Color(66, 66, 66),
    '100': Color(0, 6, 66),
}

sonar_color_dict = palette_1
