# This programm was slightly changed to run on a NVIDIA Jetson Nano
# by Ingmar Stapel
# Homepage: www.custom-build-robots.com
# Date: 20191201
#  
# Copyright (c) 2017 Adafruit Industries
# Author: Tony DiCola & James DeVito
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import time
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from jtop import jtop

import subprocess
import Jetson.GPIO as GPIO

# Pin Definitions
input_pin = 18      # BCM pin 18, BOARD pin 12
mode      = 0

def get_network_interface_state(interface):
    return subprocess.check_output('cat /sys/class/net/%s/operstate' % interface, shell=True).decode('ascii')[:-1]


def get_ip_address(interface):
    if get_network_interface_state(interface) == 'down':
        return None
    cmd = "ifconfig %s | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'" % interface
    return subprocess.check_output(cmd, shell=True).decode('ascii')[:-1]

if __name__ == "__main__":
    # 128x32 display with hardware I2C:
    disp = Adafruit_SSD1306.SSD1306_128_32(rst=None, i2c_bus=1, gpio=1) # setting gpio to 1 is hack to avoid platform detection

    disp.begin()        # Initialize library.
    disp.clear()        # Clear display.
    disp.display()

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    width   = disp.width
    height  = disp.height
    image   = Image.new('1', (width, height))

    # Get drawing object to draw on image.
    draw    = ImageDraw.Draw(image)

    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # Draw some shapes.
    # First define some constants to allow easy resizing of shapes.
    padding = -2
    top     = padding
    bottom  = height-padding
    # Move left to right keeping track of the current x position for drawing shapes.
    x = 0

    prev_value = None

    # Pin Setup:
    GPIO.setmode(GPIO.BCM)  # BCM pin-numbering scheme from Raspberry Pi
    GPIO.setup(input_pin, GPIO.IN)  # set pin as an input pin

    # Load default font.
    font   = ImageFont.load_default()

    # print("Start Display")
    cmd = "hostname -I | cut -d\' \' -f1"
    IP  = subprocess.check_output(cmd, shell = True )
    print(IP)

    cmd = "free -m | awk 'NR==2{printf \"Mem:  %.0f%% %s/%s M\", $3*100/$2, $3,$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True)
    print(MemUsage)

    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
    Disk = subprocess.check_output(cmd, shell=True)
    print(Disk)
    
    with jtop() as jetson:
        data = jetson.stats
        print(data)
        
        print('CPU1: ' + str(data['CPU1']))
        print('CPU2: ' + str(data['CPU2']))
        print('CPU3: ' + str(data['CPU3']))
        print('CPU4: ' + str(data['CPU4']))
        print('CPU : ' + str( (data['CPU1']+data['CPU2']+data['CPU3']+data['CPU4'])/4) )

        print('GPU : ' + str(data['GPU']))
        print('Temp: ' + str(data['Temp AO']))
      #  print('Power cur:' + str(data['power cur']))
      #  print('Power avg:' + str(data['power avg']))


        while jetson.ok():

            value = GPIO.input(input_pin)
            if value == GPIO.HIGH:
                mode = mode+1
                if mode >3:
                    mode = 0
                print(mode)    

            data = jetson.stats

            if mode == 0:
                # Draw a black filled box to clear the image.
                draw.rectangle((0,0,width,height), outline=0, fill=0)

                # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
                cmd = "hostname -I | cut -d\' \' -f1"
                IP  = subprocess.check_output(cmd, shell = True )

                CPU = int((data['CPU1']+data['CPU2']+data['CPU3']+data['CPU4'])/4)
                GPU = data['GPU']
                Temp = data['Temp AO']

                # Write two lines of text.
                draw.text((x, top),   "IP "  + str(IP.decode('utf-8')), font=font, fill=255)
                draw.text((x, top+8),"CPU " + str(CPU)  +" %", font=font, fill=255)
                draw.text((x, top+16),"GPU " + str(GPU)  +" %", font=font, fill=255)
                draw.text((x, top+24),"Temp "+ str(Temp) +" ºC", font=font, fill=255)

            if mode == 1:
                # Draw a black filled box to clear the image.
                draw.rectangle((0,0,width,height), outline=0, fill=0)

                cmd = "nmcli d wifi | awk 'NR==2{printf \"%s\", $2 }'"
                wifi = subprocess.check_output(cmd, shell=True)

                cmd = "nmcli d wifi | awk 'NR==2{printf \"%d\", $7}'"
                level = subprocess.check_output(cmd, shell=True)

                draw.text((x, top),   "WiFi " + str(get_ip_address('wlan0')), font=font, fill=255)
                draw.text((x, top+8),"SSID " + str(wifi.decode('utf-8')),  font=font, fill=255)
                draw.text((x, top+16),"Signal " + str(level.decode('utf-8'))+" %",  font=font, fill=255)   

            
            if mode == 2:    
                # Draw a black filled box to clear the image.
                draw.rectangle((0,0,width,height), outline=0, fill=0)

                cmd = "free -m | awk 'NR==2{printf \"Ram %.0f%% \", $3*100/$2 }'"
                RAM = subprocess.check_output(cmd, shell=True)

                cmd = "free -m | awk 'NR==2{printf \"%s/%s MB.\", $3,$2 }'"
                MemUsage = subprocess.check_output(cmd, shell=True)

                # cmd = "free -m | awk 'NR==3{printf \"Swap: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
                # SwapUsage = subprocess.check_output(cmd, shell = True )

                cmd = "df -h | awk '$NF==\"/\"{printf \"Disk %s\", $5}'"
                Disk = subprocess.check_output(cmd, shell=True)

                cmd = "df -h | awk '$NF==\"/\"{printf \"%d/%d GB.\", $3,$2}'"
                Disk1 = subprocess.check_output(cmd, shell=True)

                #print(Disk)
                draw.text((x, top),   str(RAM.decode('utf-8')),  font=font, fill=255)
                draw.text((x, top+8),str(MemUsage.decode('utf-8')),  font=font, fill=255)
                #draw.text((x, top+32),    str(SwapUsage.decode('utf-8')),  font=font, fill=255)
                draw.text((x, top+16),str(Disk.decode('utf-8')),  font=font, fill=255)
                draw.text((x, top+24),str(Disk1.decode('utf-8')), font=font, fill=255)

            if mode == 3:
                # Draw a black filled box to clear the image.
                draw.rectangle((0,0,width,height), outline=0, fill=0)

          #      cur = data['power cur']/1000
#                avg = data['power avg']/1000

                # Write two lines of text.
                draw.text((x, top),   "POWER "  , font=font, fill=255)
           #     draw.text((x, top+8),"Current  " + str(cur)  +" W.", font=font, fill=255)
 #               draw.text((x, top+16),"Average " + str(avg)  +" W.", font=font, fill=255)
 #               draw.text((x, top+24),"Temp "    + str(Temp) +" ºC", font=font, fill=255)
    
            disp.image(image)
            disp.display()
            time.sleep(0.3)

            #break
