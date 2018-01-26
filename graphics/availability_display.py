"""
Renders the availablilty message in a specified box
"""
import pygame
from availability import AvialabilitySchduler, Meeting
from graphics.objects import Image, Ballout, TextBox, ACCENT, BorderedRect, TimeLine

#the background colors for available/busy
DEFAULT_BGCOLOR = (255, 255, 255)
AVAILABLE_BGCOLOR = (127, 147, 121)
BUSY_BGCOLOR = (171, 43, 51)

#The default textcolors
DEFAULT_FGCOLOR = (0, 0, 0)
AVAILABLE_FGCOLOR = (0, 0, 0)
BUSY_FGCOLOR = (255, 255, 255)

class AvailabliltyMessage:
    """
    Composes the texts to be displayed
    """
    def __init__(self, name: str, availablilty_provider: AvialabilitySchduler,
                 location: tuple, ballonloc: tuple, avatar: str):
        self.availablilty_provider = availablilty_provider
        self._text = MeetingText(name, None)
        self._upcomming_meeting = None
        self._upcomming_meeting_sprite = None
        self._image = Image(avatar)
        self._ballout = Ballout(100, 50, location, ballonloc)

    def update(self):
        """updates the meeting information"""
        self._text.set_meeting(
            self.availablilty_provider.get_current_meeting())

        self._ballout.set_color(self._text.get_bgcolor())

        upcomming_meeting = self.availablilty_provider.get_next_meeting()
        if upcomming_meeting != self._upcomming_meeting:
            self._upcomming_meeting = upcomming_meeting
            if upcomming_meeting is not None:
                size = self._get_content_size()
                self._upcomming_meeting_sprite = UpcommingMeetingWithTimeline(
                    upcomming_meeting, size[1])
            else:
                self._upcomming_meeting_sprite = None

    def _get_content_size(self):
        """returns the size of the content"""
        return (self._text.rect.width + self._image.rect.width + 4,
                max(self._text.rect.height, self._image.rect.height) + 4)

    def render(self, surface):
        """render at the specified display position"""
        self.update()
        self._ballout.set_size(self._get_content_size())
        self._ballout.render(surface)

        base_pos = self._ballout.get_pos()
        # Render with 5px margin after the image
        text_left = self._image.rect.width + 2
        render_sprite_at_pos(surface, self._image, (base_pos[0] + 2, base_pos[1] + 2))
        render_sprite_at_pos(surface, self._text, (base_pos[0] + text_left, base_pos[1] + 2))

        if self._upcomming_meeting_sprite is not None:
            self._upcomming_meeting_sprite.rect.topleft = (base_pos[0] + self._ballout.width + 10,
                                                           base_pos[1])
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
                                    DEFAULT_FGCOLOR)
        self._text_summary = TextBox("Laddar...",
                                     small_font,
                                     DEFAULT_FGCOLOR)
        self._text_location = TextBox("",
                                      small_font,
                                      DEFAULT_FGCOLOR)
        self._text_duration = TextBox("",
                                      small_font,
                                      DEFAULT_FGCOLOR)
        self._bgcolor = DEFAULT_BGCOLOR
        self._fgcolor = DEFAULT_FGCOLOR
        self.current_meeting = None
        self.set_meeting(meeting)
        self._set_image_prop()

    def set_meeting(self, meeting):
        """Reload the dynamic text parts"""
        if self.current_meeting != meeting:
            self.current_meeting = meeting
            if not meeting.is_available():
                self._bgcolor = BUSY_BGCOLOR
                self._fgcolor = BUSY_FGCOLOR
                self._text_summary.set_text(meeting.get_summary())
                self._text_location.set_text("Plats: {}".format(meeting.get_location()))
                self._text_duration.set_text("Åter: {}".format(meeting.get_end_time()))
            else:
                self._bgcolor = AVAILABLE_BGCOLOR
                self._fgcolor = AVAILABLE_FGCOLOR
                self._text_summary.set_text("Inget möte bokat")
                self._text_location.set_text("")
                self._text_duration.set_text("")
                self._bgcolor = AVAILABLE_BGCOLOR

            self._text_header.set_color(self._fgcolor)
            self._text_summary.set_color(self._fgcolor)
            self._text_location.set_color(self._fgcolor)
            self._text_duration.set_color(self._fgcolor)
            self._set_image_prop()

    def get_bgcolor(self):
        """Gets the current background color"""
        return self._bgcolor

    def _set_image_prop(self):
        """Create surface and rect roperties"""
        size = self.get_content_size()
        self.image = pygame.surface.Surface(size)
        self.image.fill(self._bgcolor)
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
        return (width + 21, height + 7) # Add some padding after the text

    def _render_text(self):
        render_sprite_at_pos(self.image, self._text_header, (5, 0))
        render_sprite_at_pos(self.image, self._text_summary, (5, 30))
        render_sprite_at_pos(self.image, self._text_location, (5, 50))
        render_sprite_at_pos(self.image, self._text_duration, (5, 70))

    def render(self, surface):
        """render at the specified display position"""
        surface.blit(self.image, self.rect)

class UpcommingMeetingWithTimeline:
    """
    Composes the texts to be displayed
    """
    def __init__(self, meeting: Meeting, height: int):
        medium_font = pygame.font.Font("assets/FreeSansBold.ttf", 15)
        self._time_line = TimeLine((0, 30),
                                   meeting.get_start_time_datetime(),
                                   medium_font,
                                   (20, 20, 20))
        self._next_meeting = UpcommingMeeting(meeting, height)
        self.image = pygame.surface.Surface((self.get_content_width(), height))
        self.rect = self.image.get_rect()
        self.image.set_colorkey(DEFAULT_BGCOLOR)

    def get_content_width(self):
        """Calculate the max width of the current text"""
        return  self._time_line.rect.width + self._next_meeting.rect.width + 4

    def update(self):
        """Update the surface content"""
        self.image.fill(DEFAULT_BGCOLOR)
        self.image.set_colorkey(DEFAULT_BGCOLOR)
        self._time_line.update()
        self._time_line.render(self.image)
        self._next_meeting.rect.left = self._time_line.rect.width + 4
        self._next_meeting.render(self.image)

    def render(self, surface):
        """render at the specified display position"""
        self.update()
        surface.blit(self.image, self.rect)

class UpcommingMeeting:
    """
    Composes the texts to be displayed
    """
    def __init__(self, meeting: Meeting, height: int):
        medium_font = pygame.font.Font("assets/FreeSansBold.ttf", 15)
        small_font = pygame.font.Font("assets/FreeSansBold.ttf", 10)
        summary = meeting.get_summary()
        location = meeting.get_location()

        if not summary:
            summary = "Okänt möte"
        if not location:
            location = "Okänd plats"

        self._text_heading = TextBox("Kommande möte:",
                                     small_font,
                                     (20, 20, 20))
        self._text_summary = TextBox(summary,
                                     medium_font,
                                     (20, 20, 20))
        self._text_location = TextBox(location,
                                      small_font,
                                      (20, 20, 20))
        self._text_duration = TextBox(meeting.get_start_time() + " - " + meeting.get_end_time(),
                                      medium_font,
                                      ACCENT)


        background = BorderedRect(pygame.rect.Rect(0, 0, self.get_content_width() + 10, height))
        self.image = background.image
        self.rect = background.rect
        self._render_text()

    def get_content_width(self):
        """Calculate the max width of the current text"""
        width = 100
        for text_provider in (self._text_heading,
                              self._text_summary,
                              self._text_location,
                              self._text_duration):
            width = max(text_provider.rect.width, width)
        return width

    def _render_text(self):
        render_sprite_at_pos(self.image, self._text_heading, (5, 5))
        render_sprite_at_pos(self.image, self._text_summary, (5, 20))
        render_sprite_at_pos(self.image, self._text_location, (5, 38))
        render_sprite_at_pos(self.image, self._text_duration, (5, 55))

    def render(self, surface):
        """render at the specified display position"""
        surface.blit(self.image, self.rect)

def render_sprite_at_pos(surface, sprite, pos):
    """ Render at a specific pos """
    sprite.rect.topleft = pos
    sprite.render(surface)
