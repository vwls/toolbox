# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# -*- coding: utf-8 -*-

import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
import pynmea2
import sys
from subprocess import Popen, PIPE
import serial
import io

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# COLORS
ORGANGE = "#ffa600"
WHITE = "#FFFFFF"

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf", 24)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

while True:
   

    iterator = 0

    # Get output from std
    with Popen(["gpspipe", "/dev/ttyACM0", "-r"], stdout=PIPE, bufsize=1,
            universal_newlines=True) as p:
                for line in p.stdout:
                
                    iterator = iterator + 1
                    
                    # counting up to 4 lines ignores the headers that would otherwise be unfit for parsing
                    if(iterator >= 4):
                        
                        gpsmsg = pynmea2.parse(line)
                            
                        # handling errors is critical - program will fail without this step
                        try:
                            latitude = gpsmsg.lat
                            longitude = gpsmsg.lon
                            #altitude = gpsmsg.alt
                            
                            y = top
                            
                            if(latitude != 0 and latitude != "null" and latitude != "NULL" and latitude != "" and latitude != " "):
                                #print(latitude)
                                draw.rectangle((0, 0, width, height), outline=0, fill=0)
                    
                                #Write GPS data to screen
                                #y = top
                                draw.text((x, y), "LAT: " + latitude, font=font, fill=WHITE)
                                y += font.getsize("LAT")[1]
                                
                            if(longitude != 0 and longitude != "null" and longitude != "NULL" and longitude != "" and longitude != " "):
                                
                                draw.text((x, y), "LON: " + longitude, font=font, fill=WHITE)
                                y += font.getsize("LON")[1]
                                
                            #if(altitude != 0 and altitude != "null" and altitude != "NULL" and altitude != "" and altitude != " "):
                                
                                #draw.text((x, y), "ALT: " + altitude, font=font, fill=WHITE)
                                #y += font.getsize("ALT")[1]
                        except:
                            print("cannot parse that")
                            #pass
 
                        disp.image(image, rotation)

    time.sleep(0.1)

