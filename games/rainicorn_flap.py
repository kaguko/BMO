"""
Game 4: Lady Rainicorn Sky Flap
Trò chơi bay lượn trên bầu trời xứ Ooo: Điều khiển Lady Rainicorn với dải cầu vồng rực rỡ
vượt qua các cột pha lê kẹo ngọt.
"""
import pygame
import random
import math
from .base_game import BaseGame
from ..constants import (
    BMO_TEAL, BMO_BLACK, BMO_WHITE,
    BMO_YELLOW, BMO_HEART_RED, BMO_GREEN, BMO_BLUE
)
from ..audio_synth import synth

RAINBOW_COLORS = [
    (255, 80, 80),   # Đỏ
    (255, 160, 50),  # Cam
    (255, 230, 60),  # Vàng
    (70, 210, 110),  # Xanh lá
    (60, 170, 240),  # Xanh dương
    (170, 100, 230)  # Tím
]

class RainicornFlapGame(BaseGame):
    def __init__(self):
        super().__init__(title="Lady Rainicorn Sky Flap")
        
        # Lady Rainicorn
        self.bird_x = 120
        self.bird_y = self.height // 2
        self.bird_vy = 0
        self.bird_w = 48
        self.bird_h = 24
        
        # Dải đuôi cầu vồng
        self.trail = []
        
        # Cột chướng ngại vật (Pillars)
        self.pillars = []
        self.pillar_gap = 160
        self.pillar_speed = 3.5
        self.spawn_timer = 0
        
        # Tiền vàng bay
        self.coins = []
        
        self._spawn_pillar()

    def reset(self):
        super().reset()
        self.bird_y = self.height // 2
        self.bird_vy = 0
        self.trail.clear()
        self.pillars.clear()
        self.coins.clear()
        self.spawn_timer = 0
        self._spawn_pillar()

    def _spawn_pillar(self):
        min_h = 70
        max_h = self.height - self.pillar_gap - min_h - 40
        top_h = random.randint(min_h, max_h)
        bot_y = top_h + self.pillar_gap
        bot_h = self.height - bot_y
        
        p_x = self.width + 40
        self.pillars.append({
            'x': p_x, 'w': 54,
            'top_h': top_h,
            'bot_y': bot_y, 'bot_h': bot_h,
            'passed': False,
            'color': random.choice([(230, 100, 160), (140, 100, 220), (80, 190, 200)])
        })
        
        # Cơ hội sinh đồng xu ở giữa khe
        if random.random() < 0.6:
            self.coins.append({
                'x': p_x + 22,
                'y': top_h + self.pillar_gap // 2,
                'r': 10
            })

    def handle_event(self, event):
        super().handle_event(event)
        if self.is_game_over or self.is_paused:
            return

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_w, pygame.K_UP]:
                self._flap()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._flap()

    def _flap(self):
        self.bird_vy = -8.5
        synth.play('jump')

    def update(self):
        if self.is_game_over or self.is_paused:
            return

        # Trọng lực
        self.bird_vy += 0.45
        self.bird_y += self.bird_vy

        # Lưu vết đuôi cầu vồng
        self.trail.append((self.bird_x, self.bird_y + self.bird_h // 2))
        if len(self.trail) > 28:
            self.trail.pop(0)

        # Chạm nóc hoặc sàn
        if self.bird_y < 36 or self.bird_y + self.bird_h >= self.height - 10:
            self.is_game_over = True
            synth.play('game_over')
            return

        # Sinh cột định kỳ
        self.spawn_timer += 1
        if self.spawn_timer > 90:
            self.spawn_timer = 0
            self._spawn_pillar()

        bird_rect = pygame.Rect(self.bird_x, self.bird_y, self.bird_w, self.bird_h)

        # Cập nhật cột
        for p in self.pillars[:]:
            p['x'] -= self.pillar_speed
            top_rect = pygame.Rect(p['x'], 36, p['w'], p['top_h'] - 36)
            bot_rect = pygame.Rect(p['x'], p['bot_y'], p['w'], p['bot_h'])

            # Va chạm
            if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bot_rect):
                self.is_game_over = True
                synth.play('game_over')
                return

            # Vượt qua cột thành công
            if not p['passed'] and p['x'] + p['w'] < self.bird_x:
                p['passed'] = True
                self.score += 50
                synth.play('chirp')

            if p['x'] + p['w'] < -20:
                self.pillars.remove(p)

        # Cập nhật tiền vàng
        for c in self.coins[:]:
            c['x'] -= self.pillar_speed
            c_rect = pygame.Rect(c['x'] - c['r'], c['y'] - c['r'], c['r']*2, c['r']*2)
            if bird_rect.colliderect(c_rect):
                self.score += 100
                synth.play('coin')
                self.coins.remove(c)
            elif c['x'] < -20:
                self.coins.remove(c)

    def draw(self, surface):
        surface.fill((210, 245, 255))  # Nền trời xanh pastel kẹo ngọt
        
        # 1. Vẽ Đuôi Cầu Vồng (Rainbow Ribbon Trail)
        if len(self.trail) > 2:
            for c_idx, color in enumerate(RAINBOW_COLORS):
                offset_y = (c_idx - 2.5) * 3
                pts = [(pt[0] - (len(self.trail) - i) * 3, pt[1] + offset_y) for i, pt in enumerate(self.trail)]
                if len(pts) >= 2:
                    pygame.draw.lines(surface, color, False, pts, 4)

        # 2. Vẽ Cột Pha Lê Kẹo (Crystal Candy Pillars)
        for p in self.pillars:
            # Cột trên
            pygame.draw.rect(surface, p['color'], (p['x'], 36, p['w'], p['top_h'] - 36), border_radius=6)
            pygame.draw.rect(surface, BMO_WHITE, (p['x'] + 4, 36, 6, p['top_h'] - 40)) # Vết sáng phản chiếu
            pygame.draw.rect(surface, (50, 40, 60), (p['x'], 36, p['w'], p['top_h'] - 36), width=3, border_radius=6)
            
            # Cột dưới
            pygame.draw.rect(surface, p['color'], (p['x'], p['bot_y'], p['w'], p['bot_h']), border_radius=6)
            pygame.draw.rect(surface, BMO_WHITE, (p['x'] + 4, p['bot_y'] + 4, 6, p['bot_h'] - 8))
            pygame.draw.rect(surface, (50, 40, 60), (p['x'], p['bot_y'], p['w'], p['bot_h']), width=3, border_radius=6)

        # 3. Vẽ Tiền Vàng
        for c in self.coins:
            pygame.draw.circle(surface, BMO_YELLOW, (int(c['x']), int(c['y'])), c['r'])
            pygame.draw.circle(surface, (255, 240, 150), (int(c['x'] - 2), int(c['y'] - 2)), c['r'] - 4)

        # 4. Vẽ Lady Rainicorn
        bx, by = self.bird_x, int(self.bird_y)
        # Thân dài trắng ngà
        pygame.draw.ellipse(surface, (250, 245, 235), (bx, by, self.bird_w, self.bird_h))
        # Sừng kỳ lân vàng
        pygame.draw.polygon(surface, BMO_YELLOW, [(bx + self.bird_w - 6, by + 4), (bx + self.bird_w + 14, by - 8), (bx + self.bird_w - 2, by + 8)])
        # Bờm tóc hồng
        pygame.draw.ellipse(surface, (255, 180, 200), (bx + 8, by - 4, 28, 10))
        # Mắt hiền lành
        pygame.draw.circle(surface, BMO_BLACK, (bx + self.bird_w - 12, by + 9), 3)

        # 5. Thanh HUD
        self.draw_hud(surface)

        # Hướng dẫn nút
        help_t = self.font_ui.render("[SPACE / UP / CLICK]: Flap Sky Flight", True, (80, 100, 110))
        surface.blit(help_t, (self.width // 2 - 140, self.height - 24))

        # 6. Game Over
        if self.is_game_over:
            self.draw_game_over_screen(surface)
