# encoding=utf-8
"""Various actions for our office door button"""
import os
import datetime
import pytz
import pygame as pg
import yaml
from availability import AvialabilitySchduler, get_availablilty_message
from key_press_counter import KeyPressCounter
from meeting_notifier import MeetingNotifier
from ttsplay import TextMessagePlayer
from graphics import bg, count
from graphics.availability_display import AvailabliltyMessage
from graphics.objects import Clock
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! This is probably because you need superuser privileges. You can achieve this by using 'sudo' to run your script")
except ImportError:
    pass

#The file to persist data
DATA_FILE = 'data.yaml'

def get_counter_instance():
    """Loads the counter"""
    # load persisted settings
    persisted_data = dict()
    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE, 'r') as persisted:
            persisted_data = yaml.load(persisted)
    return KeyPressCounter(persisted_data.get('count', 0), persisted_data.get('date', None))

def init_gpio(cfg):
    """Init GPIO"""
    # Only initilize GPIO of configured in yaml
    if cfg.get('gpio', False):
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(cfg['gpio']['pin'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(cfg['gpio']['pin'], GPIO.RISING)
        return True
    return False

def init_pygame(cfg):
    """ Initilize pygame related components"""
    # display settins
    displaycfg = cfg.get('display', {})
    flags = pg.DOUBLEBUF | pg.HWSURFACE
    if displaycfg.get('fullscreen', False):
        flags = flags | pg.FULLSCREEN

    game_display = pg.display.set_mode((displaycfg.get('width', 1024),
                                        displaycfg.get('height', 768)), flags)

    pg.display.set_caption('Door Button Control')
    pg.mouse.set_visible(False)

    # Sound settings
    pg.mixer.pre_init(cfg.get('sound', {}).get('freq', 24000),
                      cfg.get('sound', {}).get('bitsize', -16),
                      cfg.get('sound', {}).get('channels', 1))
    pg.init()
    return game_display

def get_greeting_message():
    """Play some greeting depending on the time of day"""
    now = datetime.datetime.now()
    if now.hour >= 7 and now.hour < 9:
        return "God morgon"
    elif now.hour >= 11 and now.hour <= 13:
        return "God middag"
    elif now.hour >= 15 and now.hour <= 16:
        return "God eftermiddag"
    elif now.hour >= 16 and now.hour < 21:
        return "God kväll"
    return None

def button_pressed_action(meeting_providers, key_press_counter, message_player):
    """
    Execute actions on button presses
    """
    key_press_counter.increment()
    # Only add new sound if there is nothing playing
    if not pg.mixer.music.get_busy():
        greet = get_greeting_message()
        if greet is not None:
            message_player.queue_text(greet)
        meeting_exists = False
        for (name, provider) in meeting_providers:
            meeting = provider.get_current_meeting()
            if meeting is not None:
                message_player.queue_text(get_availablilty_message(meeting, name))
                meeting_exists = True
        if meeting_exists:
            message_player.queue_text(
            "Grattis ingen person i rummet har möte bokat och finns kanske tillgänglig för dig")

        message_player.queue_text(
            "Knappen har tryckts {} gånger under dagen".format(key_press_counter.get_count()))



def main():
    """The main program loop"""
    # Load config
    with open("config.yaml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

    # Start pygame, get the display object
    game_display = init_pygame(cfg)

    key_press_counter = get_counter_instance()
    message_player = TextMessagePlayer()
    meeting_providers = []
    meeting_notifiers = []
    availability_text = []

    # Setup calendars
    if cfg.get('ical', None) is not None:
        for person in cfg['ical']:
            # schedule calendars for updates
            availibility = AvialabilitySchduler(person['url'])
            availibility.start()
            # keep a reference to the calendars to be played at button press
            meeting_providers.append((person['name'], availibility))
            # Setup system for notify when a meeting approaches
            meeting_notifiers.append(MeetingNotifier(
                person['name'],
                availibility,
                message_player
            ))
            # Add meeting graphics
            availability_text.append(AvailabliltyMessage(
                person['name'],
                availibility,
                (person.get('pos_x', 0), person.get('pos_y', 0)),
                (person.get('ballon_x', 70), person.get('ballon_y', -50)),
                "assets/{}".format(person.get('image', 'unknown.png'))
            ))


    # Setup GPIO
    gpio = init_gpio(cfg)

    clock = pg.time.Clock()
    background = bg.Background(
        "assets/{}".format(cfg.get("display", {}).get("background", "room.jpg")), (0, 0))
    count_text = count.ButtonCount(key_press_counter, (185, 206))
    clock_widget = Clock((1000, 20), pytz.timezone("CET"))
    print("Door Button Control Ready.")

    #render_count_screen(game_display, key_press_counter.get_count())

    running = True
    while running:
        try:
            if gpio and GPIO.event_detected(cfg['gpio']['pin']):
                button_pressed_action(meeting_providers,
                                      key_press_counter,
                                      message_player)

            key_press_counter.update()
            message_player.update()

            background.render(game_display)
            count_text.render(game_display)
            for message in availability_text:
                message.render(game_display)

            clock_widget.render(game_display)

            for meeting_notifier in meeting_notifiers:
                meeting_notifier.update()

            pg.display.update()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        button_pressed_action(meeting_providers, key_press_counter, message_player)
                    if event.key == pg.K_ESCAPE:
                        running = False

            clock.tick(20)
        except KeyboardInterrupt:
            pass
    if gpio:
        GPIO.cleanup()

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
