"""
Renders the availablilty message in a specified box
"""
import pygame
from availability import PersonAvailabilityChecker
from graphics.objects import Image, Ballout, TextBox, ACCENT

class AvailabliltyMessage:
    """
    Composes the texts to be displayed
    """
    def __init__(self, availablilty_provider: PersonAvailabilityChecker,
                 location: tuple, offset: int, avatar: str):
        big_font = pygame.font.Font("assets/FreeSansbold.ttf", 20)
        small_font = pygame.font.Font("assets/FreeSansbold.ttf", 15)

        self.availablilty_provider = availablilty_provider
        self.location = location
        self.text_header = TextBox(availablilty_provider.name,
                                   big_font,
                                   ACCENT)
        self.text_summary = TextBox("",
                                    small_font,
                                    (20, 20, 20))
        self.text_location = TextBox("",
                                     small_font,
                                     (20, 20, 20))
        self.text_duration = TextBox("",
                                     small_font,
                                     (20, 20, 20))
        self.image = Image(avatar)

        self.ballout = Ballout(100, 50, location, offset)


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

    def get_content_size(self):
        """Calculate the max width of the current text"""
        width = 100
        height = 10
        for text_provider in (self.text_summary,
                              self.text_location,
                              self.text_duration):
            width = max(text_provider.rect.width, width)
            height += text_provider.rect.height + 5
        width += self.image.rect.width + 10 # Add some padding after the image
        height = max(height, self.image.rect.height)
        return (width + 10, height) # Add some padding after the text

    def render(self, surface):
        """render at the specified display position"""
        self.update_text()
        self.ballout.set_size(self.get_content_size())
        self.ballout.render(surface)
        # Render with 5px margin after the image
        text_left = self.image.rect.width + 10
        self.__render_sprite_at_pos(surface, self.image, (0, 0))
        self.__render_sprite_at_pos(surface, self.text_header, (text_left, 0))
        self.__render_sprite_at_pos(surface, self.text_summary, (text_left, 30))
        self.__render_sprite_at_pos(surface, self.text_location, (text_left, 50))
        self.__render_sprite_at_pos(surface, self.text_duration, (text_left, 70))

    def __render_sprite_at_pos(self, surface, text_box, pos):
        """ Render at a specific pos """
        base_pos = self.ballout.get_pos()
        text_box.rect.left = base_pos[0] + pos[0]
        text_box.rect.top = base_pos[1] + pos[1]
        text_box.render(surface)
