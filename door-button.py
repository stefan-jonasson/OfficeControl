# encoding=utf8
import pygame as pg
from time import sleep
from gtts import gTTS
import RPi.GPIO as GPIO
from sys import exit
import random
from tempfile import NamedTemporaryFile

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
    tfile = NamedTemporaryFile()
    tfile.close()
    messageTTS = gTTS(text=string.decode('utf8'), lang='sv')
    messageTTS.save(tfile.name)
    return tfile.name

def generateSoundFiles(strings):
    '''
    generate mp3 files for all the strings in supplied in the strings argument
    '''
    result = []
    for string in strings:
        result.append(generateSoundFile(string))
    return result


messages = ["Kontorsunderhållningen är stängd. Välkommen tillbaka vid nästa högtid!", "Det stod TRYCK INTE PÅ KNAPPEN", "Tomten har ledigt", "Välkommen till BRSE", "Grattis du har vunnit högstavinsten, ett paket med inget alls!", "Vi är tyvärr inte här för tillfället", "Kan du inte läsa på skylten?"]

fileList = generateSoundFiles(messages);

# set up the mixer
freq = 24000     # audio CD quality
bitsize = -16    # unsigned 16 bit
channels = 1     # 1 is mono, 2 is stereo

pg.mixer.init(freq, bitsize, channels)

pressedTimes = 0

def playSound(channel):
    global pressedTimes
    play_file(random.choice(fileList))
    pressedTimes += 1
    play_text("Knappen har tryckts {} gånger under dagen".format(pressedTimes))
    
GPIO.add_event_detect(24, GPIO.FALLING, callback=playSound, bouncetime=6000)

print "Door Button Control Ready."

while True:
    try:
        sleep(2)
    except KeyboardInterrupt:
        exit()

GPIO.cleanup()
