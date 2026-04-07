import pygame
import config
from config import BG, TRACK, WIDTH, CLOCK, FPS, SCREEN

class Background(pygame.sprite.Sprite):
    def __init__(self, img, mode, x_offset = 0, scale = 1.0):
        pygame.sprite.Sprite.__init__(self)
        self.image = img.copy() # 使用副本避免尺寸更改影響到未來
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * scale), int(self.image.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.x = int(x_offset * scale)
        self.rect.y = 0
        self.mode = mode
    
    def update(self):
        if self.mode == 'track':
            self.rect.x -= config.game_speed
        else:
            self.rect.x -= config.game_speed - 3
        if self.rect.right <= 0:
            self.rect.x = round(self.rect.width * 3 + self.rect.right) # x 大於 0 的 track 有三塊




if __name__ == "__main__":
    config.game_speed = 10
    config.bg_group = pygame.sprite.Group()
    for i in range(4):
        config.bg_group.add(Background(BG, 'bg', i * WIDTH, 1))
        config.bg_group.add(Background(TRACK, 'track', i * WIDTH, 1))
    
    run = True
    while run:
        CLOCK.tick(FPS)
        # ---------- 取得輸入 ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # ---------- 更新遊戲 ----------
        config.bg_group.update()
        # ---------- 畫面顯示 ----------
        SCREEN.fill((191,221,226))
        config.bg_group.draw(SCREEN)
        pygame.display.update()