"""Objects for the counter"""
import pygame

from graphics.objects import Ballout, Image, TextBox
from key_press_counter import KeyPressCounter

class ButtonCount:
    """
    Composes the texts to be displayed
    """
    def __init__(self, count: KeyPressCounter, location: tuple):
        self.count = count
        big_font = pygame.font.Font("assets/FreeSansbold.ttf", 50)
        small_font = pygame.font.Font("assets/FreeSansbold.ttf", 18)

        self.text_header = TextBox("Antal tryckningar:",
                                   small_font,
                                   (44, 44, 44))
        self.text_count = TextBox("{}".format(count.get_count()),
                                  big_font,
                                  (20, 20, 20))

        self.ballout = Ballout(230, 95, location, -50)
        self.image = Image('assets/button.png')


    def render(self, surface):
        """render at the specified display position"""
        self.text_count.set_text("{}".format(self.count.get_count()))
        self.ballout.render(surface)
        pos = self.ballout.get_pos()

        # Render Image
        self.image.rect.left, self.image.rect.top = pos
        self.image.render(surface)

        # Render text header
        self.text_header.rect.left = pos[0] + self.image.rect.width + 10
        self.text_header.rect.top = pos[1]
        self.text_header.render(surface)

        # Render text count
        self.text_count.rect.left = pos[0] + self.image.rect.width + round((self.ballout.width - self.image.rect.width) / 2) - 20
        self.text_count.rect.top = pos[1] + 20
        self.text_count.render(surface)
