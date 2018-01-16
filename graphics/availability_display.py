"""
Renders the availablilty message in a specified box
"""
import pygame
from availability import AvialabilitySchduler, Meeting
from graphics.objects import Image, Ballout, TextBox, ACCENT, BorderedRect

class AvailabliltyMessage:
    """
    Composes the texts to be displayed
    """
    def __init__(self, name: str, availablilty_provider: AvialabilitySchduler,
                 location: tuple, offset: int, avatar: str):
        self.availablilty_provider = availablilty_provider
        self._text = MeetingText(name, None)
        self._upcomming_meeting = None
        self._upcomming_meeting_sprite = None
        self._image = Image(avatar)
        self._ballout = Ballout(100, 50, location, offset)

    def update(self):
        """updates the meeting information"""
        self._text.set_meeting(
            self.availablilty_provider.get_current_meeting())

        upcomming_meeting = self.availablilty_provider.get_next_meeting()
        print(upcomming_meeting)
        if upcomming_meeting != self._upcomming_meeting:
            self._upcomming_meeting = upcomming_meeting
            if upcomming_meeting is not None:
                self._upcomming_meeting_sprite = UpcommingMeeting(upcomming_meeting)
            else:
                self._upcomming_meeting_sprite = None

    def _get_content_size(self):
        """returns the size of the content"""
        return (self._text.rect.width + self._image.rect.width + 21,
                max(self._text.rect.height, self._image.rect.height) + 2)

    def render(self, surface):
        """render at the specified display position"""
        self.update()
        self._ballout.set_size(self._get_content_size())
        self._ballout.render(surface)

        base_pos = self._ballout.get_pos()
        # Render with 5px margin after the image
        text_left = self._image.rect.width + 10
        render_sprite_at_pos(surface, self._image, base_pos)
        render_sprite_at_pos(surface, self._text, (base_pos[0] + text_left, base_pos[1]))

        if self._upcomming_meeting_sprite is not None:
            if self._ballout.offset < 0:
                pos = (base_pos[0] - 10, base_pos[1])
            else:
                pos = (base_pos[0] + self._ballout.width + 10, base_pos[1])
            self._upcomming_meeting_sprite.rect.topleft = pos
            self._upcomming_meeting_sprite.render(surface)

class MeetingText:
    """
    Composes the texts to be displayed
    """
    def __init__(self, title: str, meeting: Meeting):
        big_font = pygame.font.Font("assets/FreeSansBold.ttf", 20)
        small_font = pygame.font.Font("assets/FreeSansBold.ttf", 12)
        self._text_header = TextBox(title,
                                    big_font,
                                    ACCENT)
        self._text_summary = TextBox("Laddar...",
                                     small_font,
                                     (20, 20, 20))
        self._text_location = TextBox("",
                                      small_font,
                                      (20, 20, 20))
        self._text_duration = TextBox("",
                                      small_font,
                                      (20, 20, 20))
        self.current_meeting = None
        self.set_meeting(meeting)
        self._set_image_prop()

    def set_meeting(self, meeting):
        """Reload the dynamic text parts"""
        if self.current_meeting != meeting:
            self.current_meeting = meeting
            if not meeting.is_available():
                self._text_summary.set_text(meeting.get_summary())
                self._text_location.set_text("Plats: {}".format(meeting.get_location()))
                self._text_duration.set_text("Åter: {}".format(meeting.get_end_time()))
            else:
                self._text_summary.set_text("Tillgänglig")
                self._text_location.set_text("")
                self._text_duration.set_text("")
            self._set_image_prop()

    def _set_image_prop(self):
        """Create surface and rect roperties"""
        size = self.get_content_size()
        self.image = pygame.surface.Surface(size)
        self.image.fill((255, 255, 255))
        self.rect = pygame.rect.Rect(0, 0, size[0], size[1])
        self._render_text()

    def get_content_size(self):
        """Calculate the max width of the current text"""
        width = 100
        height = 0
        for text_provider in (self._text_header,
                              self._text_summary,
                              self._text_location,
                              self._text_duration):
            width = max(text_provider.rect.width, width)
            height += (text_provider.rect.height)
        return (width, height) # Add some padding after the text

    def _render_text(self):
        render_sprite_at_pos(self.image, self._text_header, (0, 0))
        render_sprite_at_pos(self.image, self._text_summary, (0, 30))
        render_sprite_at_pos(self.image, self._text_location, (0, 50))
        render_sprite_at_pos(self.image, self._text_duration, (0, 70))

    def render(self, surface):
        """render at the specified display position"""
        surface.blit(self.image, self.rect)

class UpcommingMeeting:
    """
    Composes the texts to be displayed
    """
    def __init__(self, meeting: Meeting):
        big_font = pygame.font.Font("assets/FreeSansBold.ttf", 20)
        medium_font = pygame.font.Font("assets/FreeSansBold.ttf", 15)
        small_font = pygame.font.Font("assets/FreeSansBold.ttf", 10)

        self._text_summary = TextBox(meeting.get_summary(),
                                     medium_font,
                                     (20, 20, 20))
        self._text_location = TextBox(meeting.get_location(),
                                      small_font,
                                      (20, 20, 20))
        self._text_duration = TextBox(meeting.get_start_time(),
                                      big_font,
                                      ACCENT)

        size = self.get_content_size()

        background = BorderedRect(pygame.rect.Rect(0, 0, size[0], size[1]))
        self.image = background.image
        self.rect = background.rect
        self._render_text()

    def get_content_size(self):
        """Calculate the max width of the current text"""
        width = 100
        height = 10
        for text_provider in (self._text_summary,
                              self._text_location,
                              self._text_duration):
            width = max(text_provider.rect.width, width)
            height += text_provider.rect.height + 5
        return (width + 10, height) # Add some padding after the text

    def _render_text(self):
        render_sprite_at_pos(self.image, self._text_summary, (5, 10))
        render_sprite_at_pos(self.image, self._text_location, (5, 35))
        render_sprite_at_pos(self.image, self._text_duration, (5, 55))

    def render(self, surface):
        """render at the specified display position"""
        surface.blit(self.image, self.rect)

def render_sprite_at_pos(surface, sprite, pos):
    """ Render at a specific pos """
    sprite.rect.topleft = pos
    sprite.render(surface)
