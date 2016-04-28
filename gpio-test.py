import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

leds = [12, 16, 20, 21]
buttons = [4, 5, 6, 13]
debounces = [0, 0, 0, 0]
idxs = {}

GPIO.setup(buttons, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(leds, GPIO.OUT, initial=GPIO.LOW)

def button_callback(channel):
    global debounces, idxs, buttons, leds
    i = idxs[channel]
    time_now = time.time()
    if (time_now - debounces[i]) >= 0.3:
        print "falling on %d" % (idxs[channel],)
    debounces[i] = time_now

def main():
    global debounces, buttons, leds, idxs
            
    for i in range(4):
        idxs[buttons[i]] = i
        GPIO.add_event_detect(buttons[i], GPIO.FALLING, callback=button_callback)
        debounces[i] = time.time()
    
    while True:
        time.sleep(1)
        GPIO.output(12, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(12, GPIO.LOW)

    GPIO.cleanup()

main()
