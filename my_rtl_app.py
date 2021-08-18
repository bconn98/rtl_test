#!/usr/bin/env python

"""
Description: Custom data handling example for rtl_433.
Author: Bryan Conn
Date: 8/18/2021
"""

from __future__ import print_function
import socket
import json
import RPi.GPIO as GPIO
import subprocess

UDP_IP = "127.0.0.1"          # Localhost
UDP_PORT = 1433               # Port to use
button_lst = [3, 12, 48, 192] # Button command values [A, B, C, D]
light_lst = [18, 23, 24, 25]  # Raspberry Pi GPIO pins to utilize


def parse_syslog(line):
    """
    Description: Try to extract the payload from a syslog line.
    Parameters:
        - line [str]: Syslog text to parse
    Return: Dictionary of text output
    """
    line = line.decode("ascii")  # also UTF-8 if BOM
    if line.startswith("<"):
        # fields should be "<PRI>VER", timestamp, hostname, command, pid, mid, sdata, payload
        fields = line.split(None, 7)
        line = fields[-1]

    data = json.loads(line)
    return data


def lights_off():
    """
    Description: Power off all GPIO lights
    Parameters: None
    Return: None
    """
    for gpio_in in light_lst:
        GPIO.output(gpio_in, GPIO.LOW)


def light_btn(button):
    """
    Description: Light an led when a button is pressed using GPIO
    Parameters:
        - button [int]: The button to light
    Return: None
    """
    idx = button_lst.index(button)         # Find the index if the button to light
    GPIO.output(light_lst[idx], GPIO.HIGH) # Light the button that was pressed


def check_two_buttons(button):
    """
    Description: Check for 2 buttons being pressed
    Parameters:
        - button [int]: A number created when 2 buttons are pressed.
    Return: Bool of if the correct buttons where found.
    """
    for opt_btn in button_lst:
        button_diff = button - opt_btn
        if button_diff in button_lst:
            light_btn(button_diff)
            light_btn(opt_btn)
            return True


def rtl_433_listen():
    """
    Description: Try to extract the payload from a syslog 
                 line and light the corresponding led.
    Parameters: None
    Return: None
    """

    # Connect to the syslog socket created by rtl_433
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:                           # Run always
        line, addr = sock.recvfrom(1024)  # Read syslog output form

        try:
            data = parse_syslog(line)     # Parse JSON output from syslog text
            button = data['cmd']          # Get the button pressed value
            lights_off()                  # Reset the lights

            if button in button_lst:      # Check for a single button
                light_btn(button)         # Set the light if only 1 button
            else:
                check_two_buttons(button) # Check for 2 buttons pressed

        except KeyError:
            lights_off()                  # Reset lights on error
        
        except ValueError:
            lights_off()                  # Reset lights on error

def setup_GPIO():
    """
    Description: Setup the required GPIO pins
    Parameters: None
    Return: None
    """
    GPIO.setmode(GPIO.BCM)
    for gpio_in in light_lst:
        GPIO.setup(gpio_in, GPIO.OUT)


if __name__ == "__main__":
    # Start the rtl application
    syslog_str = "syslog:" + UDP_IP + ":" + str(UDP_PORT)
    rtl = subprocess.Popen(["rtl_433", "-F", syslog_str, "-f", "315M"])

    # Prep GPIO pins
    setup_GPIO()

    # Run the app
    try:
        rtl_433_listen()
    except Exception as e:
        print(e)
    finally:
        lights_off()
        GPIO.cleanup()
