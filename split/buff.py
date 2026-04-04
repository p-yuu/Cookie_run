import pygame
import random
import config
from config import BUFF, DEBUFF, WIDTH

class Buff(pygame.sprite.Sprite):
    def __init__(self, kind):
        pygame.sprite.Sprite.__init__(self)

        if kind == "speed_up":
            self.image = BUFF
            self.effect = 3
        elif kind == "speed_down":
            self.image = DEBUFF
            self.effect = -2

        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = random.choice([150,355])
    
    def update(self):
        self.rect.x -= config.game_speed
        if self.rect.right <= 0:
            self.kill()
    
    def get_effect(self):
        return self.effect
