# encoding=utf-8
"""Various actions for our office door button"""
import random
import pygame as pg
import yaml
from availability import PersonAvailabilityChecker
from key_press_counter import KeyPressCounter
from ttsplay import play_file, play_text, generate_sound_files


def display_centered_message(display, text, pos_height, size):
    """Display a text at the specified height (percent)"""
    large_text_font = pg.font.Font('assets/FreeSansBold.ttf', size)
    text_surface = large_text_font.render(text, True, (200, 200, 200))
    text_rect = text_surface.get_rect()
    text_rect.center = ((pg.display.Info().current_w/2),
                        (pg.display.Info().current_h * (pos_height / 100)))
    display.blit(text_surface, text_rect)

def render_count_screen(display, num):
    display.fill((0, 0, 0))
    display_centered_message(display, "Antal knapptryckningar:", 30, 30)
    display_centered_message(display, "{}".format(num), 50, 100)
    pg.display.update()

def main():
    key_press_counter = KeyPressCounter()
    calendars = []
    file_list = []

    # Load config
    with open("config.yaml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

    # Setup messages
    if cfg['messages'] is not None:
        print("Generating soundfiles")
        file_list = generate_sound_files(cfg['messages'])

    # Setup calendars
    if cfg['ical'] is not None:
        for person in cfg['ical']:
            calendars.append(PersonAvailabilityChecker(person['name'], person['url']))

    # Only initilize GPIO of configured in yaml
    if cfg.get('gpio', False):
        import RPi.GPIO as GPIO
        pin = cfg['gpio']['pin']

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(cfg['gpio']['pin'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        def gpio_pin_pressed(channel):
            """Handle button press events"""
            # Dont listen to presses while sound is played
            GPIO.remove_event_detect(channel)
            # Do the acitions
            button_pressed_action()
            # Start listening again
            GPIO.add_event_detect(channel, GPIO.RISING, callback=gpio_pin_pressed, bouncetime=300)

        # Add event detection
        GPIO.add_event_detect(pin, GPIO.RISING, callback=gpio_pin_pressed, bouncetime=300)

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

    def button_pressed_action():
        """
        Execute actions on button presses
        """
        key_press_counter.increment()

        render_count_screen(game_display, key_press_counter.get_count())

        if file_list:
            play_file(random.choice(file_list))

        for calendar in calendars:
            play_text(calendar.get_availablilty_message())

        play_text("Knappen har tryckts {} gånger under dagen".format(key_press_counter.get_count()))

    print("Door Button Control Ready.")

    render_count_screen(game_display, key_press_counter.get_count())

    running = True

    while running:
        try:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    pg.quit()
                    quit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        button_pressed_action()
                    if event.key == pg.K_ESCAPE:
                        pg.quit()
                        quit()

            clock.tick(600)
            key_press_counter.update()

        except KeyboardInterrupt:
            pg.quit()
            quit()

    # Only initilize GPIO of configured in yaml
    if cfg['gpio'] is not None:
        GPIO.cleanup()

main()
