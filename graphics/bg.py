"""
Handle the background
"""
import pygame

class Background():
    """Paint the background"""
    def __init__(self, image_file, location):
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location

    def render(self, display):
        """render at the specified display position"""
        display.blit(self.image, self.rect)
