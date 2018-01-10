"""
Renders the availablilty message in a specified box
"""
import pygame

class TextDisplay():
    """
    Renders a text in a box
    """
    def __init__(self, text, font: pygame.font.Font, color, location):
        self.font = font
        self.color = color
        self.location = location
        self.set_text(text)

    def set_text(self, text):
        """Set the text to be renderd"""
        self.text = text
        self.text_surface = self.font.render(text, True, self.color)
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.left, self.text_rect.top = self.location

    def render(self, display):
        """render at the specified display position"""
        display.blit(self.text_surface, self.text_rect, pygame.rect.Rect(0,0,130,self.text_rect.height+5))

class CenterTextDisplay(TextDisplay):
    """
    Renders a text in a box
    """
    def __init__(self, text, font, color, location):
        TextDisplay.__init__(self, text, font, color, location)

    def set_text(self, text):
        """Set the text to be renderd and center pos"""
        TextDisplay.set_text(self, text)
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = self.location
