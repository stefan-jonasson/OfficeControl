""" A clooection of various graphics objects """
import pygame
import pygame.gfxdraw

FOREGROUND = (40, 40, 40)
BACKGROUND = (255, 255, 255)
ACCENT = (100, 100, 100)
OFFSET_HEIGHT = -50
LEFT = 0
RIGHT = 1

class RendderableSprite(pygame.sprite.Sprite):
    """ Adds the ability to render the sprite directly """

    def render(self, surface):
        """ Render according the the rect """
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

class Ballout():
    """ Paint the boubble at the offset from the anchor point """
    def __init__(self, width: int, height: int, anchor_location: tuple, offset: int):
        self.offset = offset
        self.anc_x, self.anc_y = anchor_location
        self.set_height(height)
        self.set_width(width)

    def set_size(self, size: tuple):
        """ Set the size """
        self.set_width(size[0])
        self.set_height(size[1])

    def set_width(self, width: int):
        "set the width of the control"
        self.width = width
        if self.offset < 0:
            self.top_x = abs(self.anc_x + self.offset - self.width)
        else:
            self.top_x = abs(self.anc_x + self.offset)

    def set_height(self, height: int):
        "set the height of the control"
        self.height = height + 2 #Border should be outside
        self.top_y = abs(self.anc_y + OFFSET_HEIGHT - self.height - 5)

    def get_pos(self):
        """ return the position """
        return (self.top_x + 2, self.top_y + 2)

    def render(self, surface):
        """ render at the specified display position """
        # Draw anchor line
        pygame.draw.lines(surface, FOREGROUND, False,
                          [[self.anc_x, self.anc_y],
                           [self.anc_x + self.offset, self.anc_y + OFFSET_HEIGHT],
                           [self.anc_x + self.offset +
                            ((abs(self.offset) / self.offset) * self.width),
                            self.anc_y + OFFSET_HEIGHT]], 2)

        # Draw anchor point
        pygame.gfxdraw.aacircle(surface, self.anc_x, self.anc_y, 6, ACCENT)
        pygame.gfxdraw.filled_circle(surface, self.anc_x, self.anc_y, 6, ACCENT)

        # Draw box then border
        rect = pygame.Rect(self.top_x, self.top_y, self.width, self.height)
        surface.fill(BACKGROUND, rect)
        pygame.draw.rect(surface, FOREGROUND, rect, 2)

class TextBox(pygame.sprite.Sprite):
    """
    Renders a text in a box
    """
    def __init__(self, text, font: pygame.font.Font, color):
        super().__init__()
        self.font = font
        self.color = color
        self.set_text(text)

    def set_text(self, text):
        """ Set the text to render """
        self.surface = self.font.render(text, True, self.color)
        self.rect = self.surface.get_rect()

    def render(self, display):
        """render at the specified display position"""
        display.blit(self.surface, self.rect)
