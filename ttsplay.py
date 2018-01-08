
# encoding=utf8
"""Handles text to voice conversion"""
from hashlib import md5
import os.path
import pygame as pg
from gtts import gTTS


def play_text(text):
    '''
    Play the text as sound
    '''
    print("Playing: {}".format(text))
    file_name = generate_sound_file(text)
    play_file(file_name)

def play_file(file_name):
    '''
    stream file with mixer.music module in a blocking manner
    this will stream the sound from disk while playing
    '''
    clock = pg.time.Clock()

    try:
        pg.mixer.music.load(file_name)
        print("Music file {} loaded!".format(file_name))
    except pg.error:
        print("File {} not found! ({})".format(file_name, pg.get_error()))
        return

    pg.mixer.music.play()
    while pg.mixer.music.get_busy():
        # check if playback has finished
        clock.tick(30)

def generate_sound_file(string):
    '''
    Generate a mp3 file from a string, caches the result
    '''
    file_name = "./cache/{}.mp3".format(md5(string.encode()).hexdigest())
    # Only generate the file if it does not exist
    if not os.path.isfile(file_name):
        message_tts = gTTS(text=string, lang='sv')
        message_tts.save(file_name)
        print("saving file: {}".format(file_name))
    return file_name

def generate_sound_files(strings):
    '''
    generate mp3 files for all the strings in supplied in the strings argument
    '''
    result = []
    for string in strings:
        result.append(generate_sound_file(string))
    return result
