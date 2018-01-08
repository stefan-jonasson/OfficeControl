
# encoding=utf8
"""Handles text to voice conversion"""
from hashlib import md5
import os.path
import pygame as pg
from gtts import gTTS


def play_text(text):
    '''Play the text as sound'''
    print("Playing: {}".format(text))
    file_name = generate_sound_file(text)
    play_file(file_name)

def play_file(file_name):
    '''Stream file with mixer. Non blocking'''
    try:
        pg.mixer.music.load(file_name)
        print("Music file {} loaded!".format(file_name))
    except pg.error:
        print("File {} not found! ({})".format(file_name, pg.get_error()))
        return
    pg.mixer.music.play()

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

class TextMessagePlayer():
    '''
    Class for queuing and playing messages
    '''
    def __init__(self):
        self.queue = []

    def queue_text(self, text):
        '''add a text to the queue'''
        self.queue.append(generate_sound_file(text))

    def play_queue_item(self):
        '''play the next item in the queue'''
        if self.queue:
            item = self.queue.pop(0)
            play_file(item)

    def update(self):
        '''play the next item if the mixer is available'''
        if self.queue and not pg.mixer.music.get_busy():
            self.play_queue_item()
