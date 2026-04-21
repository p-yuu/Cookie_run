import config
import pygame


class Background(pygame.sprite.Sprite):
    def __init__(self, img, mode, x_offset=0, scale=1.0):
        pygame.sprite.Sprite.__init__(self)
        self.image = img.copy()  # 使用副本避免尺寸更改影響到未來
        self.image = pygame.transform.scale(
            self.image,
            (int(self.image.get_width() * scale), int(self.image.get_height() * scale)),
        )
        self.rect = self.image.get_rect()
        self.rect.x = int(x_offset * scale)
        self.rect.y = 0
        self.mode = mode

    def update(self):
        if self.mode == "track":
            self.rect.x -= config.game_speed
        else:
            self.rect.x -= config.game_speed - 3
        if self.rect.right <= 0:
            self.rect.x = round(
                self.rect.width * 3 + self.rect.right
            )  # x 大於 0 的 track 有三塊
