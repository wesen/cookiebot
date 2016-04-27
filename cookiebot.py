#!/usr/bin/env python

__author__ = 'manuel'

import sys
from twython import Twython
import datetime
import RPi.GPIO as GPIO
import time
import random
import re
from Queue import Queue, Empty

def read_file(filename):
    with open(filename) as g:
        return [s.rstrip() for s in g.readlines() if not re.match('^\s*$', s)]

leds = [12, 16, 20, 21]
buttons = [4, 5, 6, 13]
debounces = [0, 0, 0, 0]
idxs = {}
cookies = read_file("/home/pi/cookies.txt")

msg_idx = 0
msgs = read_file("/home/pi/msgs.txt")
random.shuffle(msgs)

tokens = read_file("/home/pi/tokens.txt")

q = Queue()

def cookie_status(idx):
    global cookies, msgs, msg_idx
    msg = msgs[msg_idx]
    msg_idx = (msg_idx + 1) % len(msgs)
    msg = msg.replace("@@PLACEHOLDER@@", cookies[idx])
    msg += " " * random.randint(0, 10)
    return msg[:139]

def main():
    global debounces, buttons, leds, idxs, api, tokens, q

    ACCESS_TOKEN = tokens[0]
    ACCESS_SECRET = tokens[1]
    CONSUMER_KEY = tokens[2]
    CONSUMER_SECRET = tokens[3]

    api = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buttons, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(leds, GPIO.OUT, initial=GPIO.LOW)

    for i in range(4):
        idxs[buttons[i]] = i
        GPIO.add_event_detect(buttons[i], GPIO.FALLING, callback=button_callback)
        debounces[i] = time.time()
    
    while True:
        try:
            i = q.get(True, 2)
            status = "%s" % (cookie_status(i))
            print "Updating status: %s" % (status,)
            
            try:
                api.update_status(status=status)
                GPIO.output(leds[i], GPIO.HIGH)
                time.sleep(1)
                GPIO.output(leds[i], GPIO.LOW)
            except Exception as e:
                print e
        except Empty:
            pass

    GPIO.cleanup()

def button_callback(channel):
    global debounces, idxs, buttons, leds, q
    
    i = idxs[channel]
    time_now = time.time()
    if (time_now - debounces[i]) >= 0.3:
        timestamp = datetime.datetime.now().strftime("%H:%M")
        debounces[i] = time_now
        q.put(i)
    
main()
