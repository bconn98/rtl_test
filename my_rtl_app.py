#!/usr/bin/env python

"""Custom data handling example for rtl_433."""

# Start rtl_433 (rtl_433 -F syslog::1433), then this script

from __future__ import print_function

import socket
import json
import RPi.GPIO as GPIO

UDP_IP = "127.0.0.1"
UDP_PORT = 1433
button_lst = [3, 12, 48, 192]
light_lst = [18, 23, 24, 25]


def parse_syslog(line):
    """Try to extract the payload from a syslog line."""
    line = line.decode("ascii")  # also UTF-8 if BOM
    if line.startswith("<"):
        # fields should be "<PRI>VER", timestamp, hostname, command, pid, mid, sdata, payload
        fields = line.split(None, 7)
        line = fields[-1]

    data = json.loads(line)
    return data


def lights_off():
    """Power off all GPIO lights"""
    GPIO.output(18, GPIO.LOW)
    GPIO.output(23, GPIO.LOW)
    GPIO.output(24, GPIO.LOW)
    GPIO.output(25, GPIO.LOW)


def light_btn(button):
    """Light an led when a button is pressed using GPIO"""
    idx = button_lst.index(button)
    GPIO.output(light_lst[idx], GPIO.HIGH)


def check_two_buttons(button):
    """Check for 2 buttons being pressed"""
    for opt_btn in button_lst:
        button_diff = button - opt_btn
        if button_diff in button_lst:
            light_btn(button_diff)
            light_btn(opt_btn)
            return True


def rtl_433_listen():
    """Try to extract the payload from a syslog line and light the corresponding led."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        line, addr = sock.recvfrom(1024)

        try:
            data = parse_syslog(line)
            button = data['cmd']
            lights_off()

            if button in button_lst:
                light_btn(button)
            else:
                check_two_buttons(button)

        except KeyError:
            lights_off()
        
        except ValueError:
            lights_off()

def setup_GPIO():
    """Setup the required GPIO pins"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(23, GPIO.OUT)
    GPIO.setup(24, GPIO.OUT)
    GPIO.setup(25, GPIO.OUT)

if __name__ == "__main__":
    setup_GPIO()
    try:
        rtl_433_listen()
    except Exception as e:
        print(e)
    finally:
        lights_off()
        GPIO.cleanup()
