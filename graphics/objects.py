""" A clooection of various graphics objects """
from datetime import datetime
from math import floor
import pytz
import pygame
import pygame.gfxdraw

FOREGROUND = (40, 40, 40)
BACKGROUND = (255, 255, 255)
ACCENT = (100, 100, 100)
AVAILABLE_COLOR = (127, 147, 121)
LEFT = 0
RIGHT = 1

class RendderableSprite(pygame.sprite.Sprite):
    """ Adds the ability to render the sprite directly """

    def render(self, surface):
        """ Render according the the rect """
        if self.image is not None:
            surface.blit(self.image, self.rect)


class Image(RendderableSprite):
    """ The base class for an image loded from a file """
    def __init__(self, image_file_name: str):
        """ Graphic Sprite Constructor. """

        # Call the parent class (Sprite) constructor
        super().__init__()

        # Load the image
        self.image = pygame.image.load(image_file_name).convert()
        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values
        # of rect.x and rect.y
        self.rect = self.image.get_rect()

    def render(self, surface):
        surface.blit(self.image, self.rect)

class BorderedRect(RendderableSprite):
    """ The base class for an image loded from a file """
    def __init__(self, rect: pygame.rect.Rect):
        """ Graphic Sprite Constructor. """

        # Call the parent class (Sprite) constructor
        super().__init__()

        self.rect = rect
        # Load the image
        self.image = pygame.surface.Surface((rect.width, rect.height))
        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values
        # of rect.x and rect.y
         # Draw anchor line
        self.image.fill(BACKGROUND)
        pygame.draw.rect(self.image,
                         FOREGROUND,
                         pygame.Rect(0, 0, rect.width - 1, rect.height - 1),
                         2)

    def render(self, surface):
        surface.blit(self.image, self.rect)

class Ballout():
    """ Paint the boubble at the offset from the anchor point """
    def __init__(self, width: int, height: int, anchor_location: tuple, balloon_location: tuple):
        self.anc_x, self.anc_y = anchor_location
        self.top_x, self.top_y = balloon_location
        self.color = FOREGROUND
        self.set_size((width, height))

    def set_size(self, size: tuple):
        """ Set the size """
        self.width = size[0]
        self.height = size[1] #Border should be outside
        #self.top_x = abs(self.anc_x + self.offset_x - self.width)
        #self.top_y = abs(self.anc_y + self.offset_y - self.height - 5)

    def get_pos(self):
        """ return the position """
        return (self.top_x, self.top_y)

    def set_color(self, color: tuple):
        """ Sets the color of lines and dot """
        self.color = color

    def render(self, surface):
        """ render at the specified display position """

        # Draw anchor line
        pygame.draw.lines(surface, self.color, False,
                          [[self.anc_x, self.anc_y],
                           [self.top_x, self.top_y + self.height + 4],
                           [self.top_x + self.width, self.top_y + self.height + 4]], 2)

        # Draw anchor point
        pygame.gfxdraw.aacircle(surface, self.anc_x, self.anc_y, 6, self.color)
        pygame.gfxdraw.filled_circle(surface, self.anc_x, self.anc_y, 6, self.color)

        # Draw box then border
        box = BorderedRect(pygame.Rect(self.top_x, self.top_y, self.width, self.height))
        box.render(surface)

class TextBox(pygame.sprite.Sprite):
    """
    Renders a text in a box
    """
    def __init__(self, text, font: pygame.font.Font, color):
        super().__init__()
        self.font = font
        self.color = color
        self.text = None
        self.surface = None
        self.rect = None
        self.set_text(text)

    def set_text(self, text):
        """ Set the text to render """
        if self.text != text:
            self.surface = self.font.render(text, True, self.color)
            self.rect = self.surface.get_rect()
            self.text = text

    def set_color(self, color):
        """ Set the text to render """
        if self.color != color:
            self.surface = self.font.render(self.text, True, color)
            self.rect = self.surface.get_rect()
            self.color = color

    def render(self, display):
        """render at the specified display position"""
        if self.surface:
            display.blit(self.surface, self.rect)

class Clock:
    """
    Renders a text in a box
    """
    def __init__(self, topleft: tuple, time_zone: pytz.timezone):
        self.topleft = topleft
        self.timezone = time_zone
        self.time_text = TextBox("", pygame.font.Font("assets/FreeSansBold.ttf", 50), FOREGROUND)

    def render(self, display):
        """render at the specified display position"""
        self.time_text.set_text(datetime.now(self.timezone).strftime("%H:%M:%S"))
        self.time_text.rect.topleft = self.topleft
        self.time_text.render(display)

class TimeLine(RendderableSprite):
    """
    Renders a text in a box
    """
    def __init__(self, top_left: tuple, start_time: datetime, font: pygame.font.Font, color):
        super().__init__()
        self._top_left = top_left
        self._start_time = start_time
        self._color = color
        self.rect = pygame.rect.Rect(0, 0, 0, 0)
        self.image = None
        self.time_text = TextBox("", font, color)
        self.update()

    def get_time_diff(self):
        """Calculate the diff until now"""
        return (self._start_time - datetime.now(self._start_time.tzinfo)).total_seconds()

    def get_time_pixels(self):
        """Calculate the time in pixels"""
        return floor(self.get_time_diff() / 15)

    def time_to_eta(self):
        """Get a formatted string for the time diff"""
        diff = self.get_time_diff()
        minutes = floor(diff // 60)
        if diff > 3600:
            hours = floor(diff // 3600)
            minutes -= hours * 60
            return "{}h {}m {}s".format(hours, minutes, floor(diff % 60))

        return "{}m {}s".format(minutes, floor(diff % 60))

    def update(self):
        """Update the image surface"""
        if self.time_text.text != self.time_to_eta():
            width = self.get_time_pixels()
            if width > 0:
                self.image = pygame.surface.Surface((width, 50))
                self.image.fill(BACKGROUND)
                self.image.set_colorkey(BACKGROUND)

                self.rect = self.image.get_rect()
                self.rect.topleft = self._top_left

                self.time_text.set_text(self.time_to_eta())
                if width > self.time_text.rect.width:
                    self.time_text.rect.topleft = self.rect.topleft
                    self.time_text.render(self.image)
                pygame.draw.line(self.image, self._color, (0, 48), (width, 48), 2)
