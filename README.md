

#####set up Raspberry Pi volume

>alsaconfig

Adjust the volume sliders with the arrow keys  


#####GPIO pin numbers:  
see `led_touch_event_loop.py` for the latest 

```
touch_input_pins = [23, 12, 20, 27, 2, 14]
prox_input_pins = [24, 16, 21, 22, 3, 15]
relay_output_pins = [5, 6, 13, 19, 10, 9]
```
or, by touch and proximity:
```
t1: 23
p1: 24

t2: 12
p2: 16

t3: 20
p3: 21

t4: 27
p4: 22

t5: 2
p5: 3

t6: 14
p6: 15
```
relay pins are set in the configuration

##### run program
`sudo PYTHONPATH="$PYTHONPATH:/home/pi/rpi_ws281x/python/build/lib.linux-armv7l-3.7:/home/pi/rpi_ws281x/python" python3 scripts/led_touch_event_loop.py`
 
 
#####run automatically after boot of Raspberry Pi
Add the following to /etc/rc.local

>sudo nano /etc/rc.local

```
(sleep 12;cd /home/pi/treechipi;sudo PATH="$PATH:/home/pi/.local/bin" PYTHONPATH="$PYTHONPATH:/home/pi/.local/lib/python3.7:/home/pi/rpi_ws281x/python/build/lib.linux-armv7l-3.7:/home/pi/rpi_ws281x/python" /home/pi/.local/bin/python3 sc
ripts/led_touch_event_loop.py > /dev/null 2>&1 &)
```


