import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(6,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(19,GPIO.OUT)
GPIO.setup(26,GPIO.OUT)

print "Turn on voltage"
GPIO.output(6,GPIO.HIGH)

print "Turn LEDs on"
GPIO.output(13,GPIO.HIGH)
time.sleep(2)
GPIO.output(19,GPIO.HIGH)
time.sleep(2)
GPIO.output(26,GPIO.HIGH)
time.sleep(4)

print "Go to initial state"
GPIO.output(13,GPIO.LOW)
time.sleep(2)
GPIO.output(19,GPIO.LOW)

print "Done with initialization"

