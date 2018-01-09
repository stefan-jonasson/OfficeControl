"""Objects for the counter"""
import pygame

from graphics.text import CenterTextDisplay
from key_press_counter import KeyPressCounter


class ButtonCount:
    """
    Composes the texts to be displayed
    """
    def __init__(self, count: KeyPressCounter, location: tuple):
        self.count = count
        x, y = location
        big_font = pygame.font.Font("assets/FreeSansbold.ttf", 40)
        small_font = pygame.font.Font("assets/FreeSansbold.ttf", 15)

        self.text_header = CenterTextDisplay("Antal tryckningar:",
                                             small_font,
                                             (44, 44, 44),
                                             location)
        self.text_count = CenterTextDisplay("{}".format(count.get_count()),
                                       big_font,
                                       (20, 20, 20),
                                       (x, y + 30))

    def render(self, display):
        """render at the specified display position"""
        self.text_header.render(display)
        self.text_count.set_text("{}".format(self.count.get_count()))
        self.text_count.render(display)
