"""
Game 2: Bug Catcher / Space Invaders
Trò chơi bắn bọ điện tử retro: BMO bảo vệ bộ vi xử lý khỏi các lỗi bọ máy tính (Glitched Bugs).
"""
import pygame
import random
import math
from .base_game import BaseGame
from ..constants import (
    BMO_TEAL, BMO_BODY_TEAL, BMO_BLACK, BMO_WHITE,
    BMO_YELLOW, BMO_HEART_RED, BMO_GREEN, BMO_BLUE
)
from ..audio_synth import synth

class BugInvadersGame(BaseGame):
    def __init__(self):
        super().__init__(title="BMO Bug Catcher")
        
        # BMO Defender Ship
        self.ship_x = self.width // 2 - 25
        self.ship_y = self.height - 70
        self.ship_w = 50
        self.ship_h = 32
        self.ship_speed = 7.0
        self.lives = 3
        
        # Đạn laser
        self.lasers = []
        self.laser_cooldown = 0
        
        # Bọ (Bugs)
        self.bugs = []
        self.bug_dir = 1
        self.bug_speed = 1.6
        self.wave = 1
        
        # Hạt nổ
        self.particles = []
        
        self._spawn_bug_wave()

    def reset(self):
        super().reset()
        self.ship_x = self.width // 2 - 25
        self.lives = 3
        self.lasers.clear()
        self.particles.clear()
        self.wave = 1
        self.bug_speed = 1.6
        self._spawn_bug_wave()

    def _spawn_bug_wave(self):
        """Tạo ma trận đàn bọ."""
        self.bugs.clear()
        rows = 4
        cols = 8
        spacing_x = 65
        spacing_y = 45
        start_x = (self.width - cols * spacing_x) // 2
        start_y = 65
        
        for r in range(rows):
            for c in range(cols):
                is_gold = (r == 0 and c in [3, 4])
                self.bugs.append({
                    'x': start_x + c * spacing_x,
                    'y': start_y + r * spacing_y,
                    'w': 34,
                    'h': 26,
                    'row': r,
                    'is_gold': is_gold,
                    'color': BMO_YELLOW if is_gold else (BMO_BLUE if r % 2 == 0 else BMO_HEART_RED),
                    'leg_anim': random.uniform(0, math.pi * 2)
                })

    def handle_event(self, event):
        super().handle_event(event)
        if self.is_game_over or self.is_paused:
            return

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_w, pygame.K_UP]:
                self._shoot()

    def _shoot(self):
        if self.laser_cooldown <= 0:
            self.lasers.append({
                'x': self.ship_x + self.ship_w // 2 - 3,
                'y': self.ship_y - 8,
                'w': 6,
                'h': 14
            })
            self.laser_cooldown = 12
            synth.play('laser')

    def update(self):
        if self.is_game_over or self.is_paused:
            return

        # Điều khiển di chuyển BMO Defender
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.ship_x = max(10, self.ship_x - self.ship_speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.ship_x = min(self.width - self.ship_w - 10, self.ship_x + self.ship_speed)
        if keys[pygame.K_SPACE]:
            self._shoot()

        if self.laser_cooldown > 0:
            self.laser_cooldown -= 1

        # Cập nhật đạn laser
        for laser in self.lasers[:]:
            laser['y'] -= 10
            if laser['y'] < 30:
                self.lasers.remove(laser)

        # Di chuyển đàn bọ
        touch_edge = False
        for bug in self.bugs:
            bug['x'] += self.bug_dir * self.bug_speed
            bug['leg_anim'] += 0.2
            if bug['x'] <= 15 or bug['x'] + bug['w'] >= self.width - 15:
                touch_edge = True

        if touch_edge:
            self.bug_dir *= -1
            for bug in self.bugs:
                bug['y'] += 18
                # Nếu bọ chạm đất
                if bug['y'] + bug['h'] >= self.ship_y:
                    self.is_game_over = True
                    synth.play('game_over')
                    return

        # Kiểm tra bắn trúng bọ
        for laser in self.lasers[:]:
            l_rect = pygame.Rect(laser['x'], laser['y'], laser['w'], laser['h'])
            for bug in self.bugs[:]:
                b_rect = pygame.Rect(bug['x'], bug['y'], bug['w'], bug['h'])
                if l_rect.colliderect(b_rect):
                    self._create_particles(bug['x'] + 17, bug['y'] + 13, bug['color'])
                    self.score += 200 if bug['is_gold'] else 50
                    synth.play('coin' if bug['is_gold'] else 'hit')
                    self.bugs.remove(bug)
                    if laser in self.lasers:
                        self.lasers.remove(laser)
                    break

        # Nếu quét sạch đàn bọ -> Qua màn mới nhanh hơn
        if not self.bugs:
            self.wave += 1
            self.score += 500
            self.bug_speed = min(4.5, self.bug_speed + 0.4)
            synth.play('win')
            self._spawn_bug_wave()

        # Cập nhật hạt nổ
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['alpha'] -= 12
            if p['alpha'] <= 0:
                self.particles.remove(p)

    def _create_particles(self, x, y, color):
        for _ in range(10):
            self.particles.append({
                'x': x, 'y': y,
                'vx': random.uniform(-4, 4),
                'vy': random.uniform(-4, 4),
                'color': color,
                'alpha': 255
            })

    def draw(self, surface):
        surface.fill((18, 24, 22))  # Màu nền máy tính retro tối
        
        # 1. Vẽ lưới mạch điện tử nền
        for gx in range(0, self.width, 50):
            pygame.draw.line(surface, (28, 38, 34), (gx, 36), (gx, self.height), 1)
        for gy in range(36, self.height, 50):
            pygame.draw.line(surface, (28, 38, 34), (0, gy), (self.width, gy), 1)

        # 2. Vẽ Đạn Laser
        for l in self.lasers:
            pygame.draw.rect(surface, BMO_YELLOW, (l['x'], l['y'], l['w'], l['h']), border_radius=2)
            pygame.draw.rect(surface, BMO_WHITE, (l['x'] + 1, l['y'], l['w'] - 2, l['h']))

        # 3. Vẽ Đàn Bọ (Pixel Bugs)
        for b in self.bugs:
            bx, by = int(b['x']), int(b['y'])
            # Thân bọ
            pygame.draw.rect(surface, b['color'], (bx + 6, by + 4, 22, 18), border_radius=4)
            # Mắt bọ
            pygame.draw.rect(surface, BMO_WHITE, (bx + 9, by + 8, 4, 4))
            pygame.draw.rect(surface, BMO_WHITE, (bx + 21, by + 8, 4, 4))
            # Râu bọ
            pygame.draw.line(surface, b['color'], (bx + 8, by + 4), (bx + 3, by - 4), 2)
            pygame.draw.line(surface, b['color'], (bx + 26, by + 4), (bx + 31, by - 4), 2)
            
            # Chân bọ cựa quậy
            leg_w = int(4 * math.sin(b['leg_anim']))
            pygame.draw.line(surface, b['color'], (bx + 6, by + 10), (bx - 2 + leg_w, by + 8), 2)
            pygame.draw.line(surface, b['color'], (bx + 6, by + 18), (bx - 2 - leg_w, by + 22), 2)
            pygame.draw.line(surface, b['color'], (bx + 28, by + 10), (bx + 36 - leg_w, by + 8), 2)
            pygame.draw.line(surface, b['color'], (bx + 28, by + 18), (bx + 36 + leg_w, by + 22), 2)

        # 4. Vẽ BMO Defender Ship
        sx, sy = int(self.ship_x), int(self.ship_y)
        pygame.draw.rect(surface, BMO_BODY_TEAL, (sx, sy + 6, self.ship_w, self.ship_h - 6), border_radius=4)
        # Nòng súng trên nóc
        pygame.draw.rect(surface, BMO_YELLOW, (sx + self.ship_w//2 - 4, sy, 8, 8))
        # Màn hình nhỏ BMO
        pygame.draw.rect(surface, BMO_TEAL, (sx + 8, sy + 10, self.ship_w - 16, 12), border_radius=2)
        pygame.draw.circle(surface, BMO_BLACK, (sx + 16, sy + 15), 2)
        pygame.draw.circle(surface, BMO_BLACK, (sx + 34, sy + 15), 2)

        # 5. Hạt nổ
        for p in self.particles:
            p_surf = pygame.Surface((5, 5), pygame.SRCALPHA)
            p_surf.fill((*p['color'], max(0, int(p['alpha']))))
            surface.blit(p_surf, (int(p['x']), int(p['y'])))

        # 6. Thanh HUD
        self.draw_hud(surface)
        
        # Hiển thị Wave
        wave_t = self.font_ui.render(f"WAVE: {self.wave}", True, BMO_BLUE)
        surface.blit(wave_t, (180, 8))

        # Hướng dẫn nút bấm
        help_t = self.font_ui.render("[A/D or Left/Right]: Move   |   [SPACE]: Shoot Laser Net", True, (120, 150, 140))
        surface.blit(help_t, (self.width // 2 - 200, self.height - 24))

        # 7. Game Over
        if self.is_game_over:
            self.draw_game_over_screen(surface)
