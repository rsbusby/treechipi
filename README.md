

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


https://docs.google.com/document/d/1NlS4hL0Mb0uoLkr-EI-Y4GzoPQCwdnx7UXxgSGZLiow/edit



Install Python3.7  (30 minutes)


sudo apt-get update
sudo apt install -y libffi-dev libbz2-dev liblzma-dev \
    libsqlite3-dev libncurses5-dev libgdbm-dev zlib1g-dev \
    libreadline-dev libssl-dev tk-dev build-essential \
    libncursesw5-dev libc6-dev openssl git
    
wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tar.xz

tar xf Python-3.7.0.tar.xz

cd cpython-3.7.0

./configure --prefix=$HOME/.local
 
*** this command takes ~5 minutes

make -j 4 -l 4

  **** this command takes about 16 minutes

make install

#### Install LED strip control library
Will add this 
	
##Enable SSH 

https://www.raspberrypi.org/documentation/remote-access/ssh/
Launch Raspberry Pi Configuration from the Preferences menu
Navigate to the Interfaces tab
Select Enabled next to SSH
Click OK

Make sure the Pi and the Mac are on the same network 
Copy sound  files from Mac Terminal
Assuming there is a directory `media` with subdirectories t1, t2, t3, t4, t5, t6
Open Mac Terminal
Go to the directory
if you put on the Desktop, as directory "media"
cd ~/Desktop
scp -r media pi@raspberry.local:

Get code from github, on Pi
Open terminal on Pi
git clone https://github.com/rsbusby/treechipi.git 
Configure:
cd treechip
sudo sh config
Run
sudo sh run

Set up auto-start
(from treechipi directory)
sudo cp -f scripts/rc.local /etc/

