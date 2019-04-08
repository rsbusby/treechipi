

##### Set Raspberry Pi volume 

>alsamixer

Adjust the volume sliders with the arrow keys  


##### GPIO pin numbers:  
see `led_touch_event_loop.py` for the latest 

```
touch_input_pins = [23, 26, 20, 27, 2, 14]
prox_input_pins = [24, 16, 21, 22, 3, 15]
relay_output_pins = [5, 6, 13, 19, 10, 9]
```
or, by touch and proximity:
```
t1: 23
p1: 24

t2: 26
p2: 16

t3: 27
p3: 22

t4: 20
p4: 21

t5: 14
p5: 15

t6: 2
p6: 3
```
relay pins are set in the configuration

##### Run program
`sudo PYTHONPATH="$PYTHONPATH:/home/pi/rpi_ws281x/python/build/lib.linux-armv7l-3.7:/home/pi/rpi_ws281x/python" python3 scripts/led_touch_event_loop.py`
 
 
##### Run automatically after boot of Raspberry Pi
Add the following to /etc/rc.local

>sudo nano /etc/rc.local

```
(sleep 12;cd /home/pi/treechipi;sudo PATH="$PATH:/home/pi/.local/bin" PYTHONPATH="$PYTHONPATH:/home/pi/.local/lib/python3.7:/home/pi/rpi_ws281x/python/build/lib.linux-armv7l-3.7:/home/pi/rpi_ws281x/python" /home/pi/.local/bin/python3 sc
ripts/led_touch_event_loop.py > /dev/null 2>&1 &)
```


