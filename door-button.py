# encoding=utf8
import pygame as pg
from time import sleep
from gtts import gTTS
import RPi.GPIO as GPIO
from sys import exit
import random
from availability import PersonAvailabilityChecker
from hashlib import md5
import os.path

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

def play_text(text):
    fileName = generateSoundFile(text)
    play_file(fileName)

def play_file(file_file):
    '''
    stream file with mixer.music module in a blocking manner
    this will stream the sound from disk while playing
    '''
    
    # volume value 0.0 to 1.0
    clock = pg.time.Clock()
    
    try:
        pg.mixer.music.load(file_file)
        print("Music file {} loaded!".format(file_file))
    except pg.error:
        print("File {} not found! ({})".format(file_file, pg.get_error()))
        return

    pg.mixer.music.play()
    while pg.mixer.music.get_busy():
        # check if playback has finished
        clock.tick(30)


def generateSoundFile(string):
    fileName = "./cache/{}.mp3".format(md5(string).hexdigest())
    # Only generate the file if it does not exist
    if (not os.path.isfile(fileName)): 
        messageTTS = gTTS(text=string.decode('utf8'), lang='sv')
        messageTTS.save(fileName)
    return fileName

def generateSoundFiles(strings):
    '''
    generate mp3 files for all the strings in supplied in the strings argument
    '''
    result = []
    for string in strings:
        result.append(generateSoundFile(string))
    return result

pressedTimes = 0

p1 = PersonAvailabilityChecker("Stefan", 'todo-load-from-config/calendar.ics')
p2 = PersonAvailabilityChecker("Nalle", 'todo-load-from-config/calendar.ics')

def playSound(channel):
    global pressedTimes
    play_file(random.choice(fileList))
    play_text(p1.getAvailabliltyMessage())
    play_text(p2.getAvailabliltyMessage())
    pressedTimes += 1
    play_text("Knappen har tryckts {} gånger under dagen".format(pressedTimes))
    

messages = ["Kontorsunderhållningen är stängd. Välkommen tillbaka vid nästa högtid!", "Det stod TRYCK INTE PÅ KNAPPEN", "Tomten har tagit ledigt", "Välkommen till BRSE", "Grattis du har vunnit högstavinsten, ett paket med inget alls!", "Vi är tyvärr inte här för tillfället", "Kan du inte läsa på skylten?"]

print "Generating soundfiles"
fileList = generateSoundFiles(messages);

# set up the mixer
freq = 24000     # audio CD quality
bitsize = -16    # unsigned 16 bit
channels = 1     # 1 is mono, 2 is stereo

print "Starting sound mixer"

pg.mixer.init(freq, bitsize, channels)
GPIO.add_event_detect(24, GPIO.RISING, callback=playSound, bouncetime=10000)

print "Door Button Control Ready."

while True:
    try:
        sleep(2)
    except KeyboardInterrupt:
        exit()

GPIO.cleanup()
