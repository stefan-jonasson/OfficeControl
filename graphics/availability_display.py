"""
Renders the availablilty message in a specified box
"""
from availability import PersonAvailabilityChecker
from graphics.text import SMALL_FONT, BIG_FONT, TextDisplay

class AvailabliltyMessage:
    """
    Composes the texts to be displayed
    """
    def __init__(self, availablilty_provider: PersonAvailabilityChecker, location: tuple):
        self.availablilty_provider = availablilty_provider
        self.location = location
        self.text_header = TextDisplay(availablilty_provider.name,
                                       SMALL_FONT,
                                       (44, 44, 44),
                                       (0, 0))
        self.text_message = TextDisplay(availablilty_provider.get_availablilty_message(),
                                        BIG_FONT,
                                        (20, 20, 20),
                                        (0, 30))

    def render(self, display):
        """render at the specified display position"""
        self.text_header.render(display)
        self.text_message.set_text(self.availablilty_provider.get_availablilty_message())
        self.text_message.render(display)
