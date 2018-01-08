# encoding=utf-8
"""Various actions for our office door button"""
import os

import pygame as pg
import yaml

from availability import PersonAvailabilityChecker
from key_press_counter import KeyPressCounter
from ttsplay import TextMessagePlayer

#The file to persist data
DATA_FILE = 'data.yaml'

def display_centered_message(display, text, pos_height, size):
    """Display a text at the specified height (percent)"""
    large_text_font = pg.font.Font('assets/FreeSansBold.ttf', size)
    text_surface = large_text_font.render(text, True, (200, 200, 200))
    text_rect = text_surface.get_rect()
    text_rect.center = ((pg.display.Info().current_w/2),
                        (pg.display.Info().current_h * (pos_height / 100)))
    display.blit(text_surface, text_rect)

def render_count_screen(display, num):
    """Render the count screen"""
    display.fill((0, 0, 0))
    display_centered_message(display, "Antal knapptryckningar idag:", 25, 50)
    display_centered_message(display, "{}".format(num), 50, 200)
    pg.display.update()

def get_counter_instance():
    """Loads the counter"""
    # load persisted settings
    persisted_data = dict()
    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE, 'r') as persisted:
            persisted_data = yaml.load(persisted)
    return KeyPressCounter(persisted_data.get('count', 0), persisted_data.get('date', None))

def init_gpio(cfg, action):
    """Connects the gpio button events"""
    # Only initilize GPIO of configured in yaml
    if cfg.get('gpio', False):
        import RPi.GPIO as GPIO
        pin = cfg['gpio']['pin']

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(cfg['gpio']['pin'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Add event detection
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=action, bouncetime=300)

def main():
    """The main program loop"""
    # Load config
    with open("config.yaml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

    key_press_counter = get_counter_instance()
    message_player = TextMessagePlayer()
    calendars = []

    # Setup calendars
    if cfg.get('ical', None) is not None:
        for person in cfg['ical']:
            calendars.append(PersonAvailabilityChecker(person['name'], person['url']))

    def button_pressed_action():
        """
        Execute actions on button presses
        """
        key_press_counter.increment()
        render_count_screen(game_display, key_press_counter.get_count())
        # Only add new sound if there is nothing playing
        if not pg.mixer.music.get_busy():
            for calendar in calendars:
                message_player.queue_text(calendar.get_availablilty_message())

            message_player.queue_text("Knappen har tryckts {} gånger under dagen".format(key_press_counter.get_count()))

    # Setup GPIO
    init_gpio(cfg, button_pressed_action)

    # display settins
    displaycfg = cfg.get('display', {})
    game_display = pg.display.set_mode((displaycfg.get('width', 1024),
                                        displaycfg.get('height', 768)), pg.FULLSCREEN)

    pg.display.set_caption('Door Button Control')

    # Sound settings
    pg.mixer.pre_init(cfg.get('sound', {}).get('freq', 24000),
                      cfg.get('sound', {}).get('bitsize', -16),
                      cfg.get('sound', {}).get('channels', 1))
    pg.init()

    clock = pg.time.Clock()

    print("Door Button Control Ready.")

    render_count_screen(game_display, key_press_counter.get_count())

    running = True

    while running:
        try:
            key_press_counter.update()
            message_player.update()
            for calendar in calendars:
                calendar.update()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    pg.quit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        button_pressed_action()
                    if event.key == pg.K_ESCAPE:
                        running = False
                        pg.quit()

            clock.tick(60)

        except KeyboardInterrupt:
            pg.quit()

    # Persist current status
    with open(DATA_FILE, 'w') as outfile:
        yaml.dump(dict(count=key_press_counter.get_count(),
                       date=key_press_counter.get_stat_date()),
                  outfile,
                  default_flow_style=False)
    print("state stored ({}, {})!".format(key_press_counter.get_count(),
                                          key_press_counter.get_stat_date()))
    quit()

main()
