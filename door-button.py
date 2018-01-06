# encoding=utf8
import pygame as pg
from time import sleep
import RPi.GPIO as GPIO
from sys import exit
import random
from availability import PersonAvailabilityChecker
from ttsplay import play_file, play_text
import yaml

def buttonPressedAction(channel):
    """
    Execute actions on button presses
    """
    global pressedTimes
    
    # Dont listen to presses while sound is played
    GPIO.remove_event_detect(channel)
    
    if len(fileList) > 0: 
        play_file(random.choice(fileList))
    
    for am in calendars:
        play_text(am.getAvailabliltyMessage())
    
    pressedTimes += 1
    play_text("Knappen har tryckts {} gånger under dagen".format(pressedTimes))
    
    # Start listening again
    GPIO.add_event_detect(channel, GPIO.RISING, callback=buttonPressedAction, bouncetime=300)

# Load config 
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

if cfg['gpio'] is None or cfg['gpio']['pin'] is None:
    print "GPIO pin needs to be set in config.yaml"
    exit 1

pin = cfg['gpio']['pin']

pressedTimes = 0
calendars = []
fileList = []

# Setup messages
if cfg['messages'] is not None:
    print "Generating soundfiles"
    fileList = generateSoundFiles(cfg['messages'])

# Setup calendars
if cfg['ical'] is not None:
    for person in cfg['ical']:
        calendars += PersonAvailabilityChecker(person['name'], person['url'])


# set up the mixer
pg.mixer.init(cfg['freq'], cfg['bitsize'], cfg['channels'])

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(cfg['gpio']['pin'], GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.add_event_detect(pin, GPIO.RISING, callback=buttonPressedAction, bouncetime=300)

print "Door Button Control Ready."

while True:
    try:
        sleep(2)
    except KeyboardInterrupt:
        exit()

GPIO.cleanup()