"""
Renders the availablilty message in a specified box
"""
import pygame
from availability import PersonAvailabilityChecker
from graphics.text import TextDisplay

class AvailabliltyMessage:
    """
    Composes the texts to be displayed
    """
    def __init__(self, availablilty_provider: PersonAvailabilityChecker, location: tuple):
        x, y = location
        big_font = pygame.font.Font("assets/FreeSansbold.ttf", 20)
        small_font = pygame.font.Font("assets/FreeSansbold.ttf", 15)

        self.availablilty_provider = availablilty_provider
        self.location = location
        self.text_header = TextDisplay(availablilty_provider.name,
                                       big_font,
                                       (44, 44, 44),
                                       location)
        self.text_summary = TextDisplay("",
                                        small_font,
                                        (20, 20, 20),
                                        (x, y + 30))
        self.text_location = TextDisplay("",
                                         small_font,
                                         (20, 20, 20),
                                         (x, y + 50))
        self.text_duration = TextDisplay("",
                                         small_font,
                                         (20, 20, 20),
                                         (x, y + 70))

    def update_text(self):
        """Reload the dynamic text parts"""
        meeting = self.availablilty_provider.get_current_meeting()
        if not meeting.is_available():
            self.text_summary.set_text(meeting.get_summary())
            self.text_location.set_text("Plats: {}".format(meeting.get_location()))
            self.text_duration.set_text("Åter: {}".format(meeting.get_duration()))
        else:
            self.text_summary.set_text("Tillgänglig")
            self.text_location.set_text("")
            self.text_duration.set_text("")


    def render(self, display):
        """render at the specified display position"""
        self.update_text()
        self.text_header.render(display)
        self.text_summary.render(display)
        self.text_location.render(display)
        self.text_duration.render(display)