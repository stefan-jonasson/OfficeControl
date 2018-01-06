# encoding=utf8
import pygame as pg
from gtts import gTTS
from hashlib import md5
import os.path

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
