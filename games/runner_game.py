"""
Game 1: BMO Chop! Adventure Runner
Trò chơi chạy vô tận retro: Nhảy tránh chướng ngại vật, thu thập pin năng lượng
và dùng tuyệt chiêu BMO CHOP! chém quái vật trên vùng đất Ooo.
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

class RunnerGame(BaseGame):
    def __init__(self):
        super().__init__(title="BMO Chop! Adventure Runner")
        self.ground_y = self.height - 100
        
        # Nhân vật BMO
        self.player_x = 100
        self.player_y = self.ground_y - 50
        self.player_w = 44
        self.player_h = 50
        self.velocity_y = 0
        self.is_jumping = False
        self.is_chopping = False
        self.chop_timer = 0
        self.lives = 3
        
        # Môi trường cuộn Parallax
        self.scroll_x = 0
        self.game_speed = 5.0
        
        # Đối tượng trong game
        self.obstacles = []     # Gnomes, Dơi, Bụi gai
        self.collectibles = []  # Pin, Kim cương kẹo
        self.particles = []     # Hiệu ứng nổ pixel
        self.spawn_timer = 0
        
        # Mây & Phong cảnh nền
        self.clouds = [{'x': random.randint(0, self.width), 'y': random.randint(50, 200), 'w': random.randint(60, 120)} for _ in range(5)]
        self.mountains = [{'x': i * 200, 'h': random.randint(80, 160), 'color': (110, 185, 175)} for i in range(6)]

    def reset(self):
        super().reset()
        self.player_y = self.ground_y - 50
        self.velocity_y = 0
        self.is_jumping = False
        self.is_chopping = False
        self.chop_timer = 0
        self.lives = 3
        self.game_speed = 5.0
        self.obstacles.clear()
        self.collectibles.clear()
        self.particles.clear()
        self.spawn_timer = 0

    def handle_event(self, event):
        super().handle_event(event)
        if self.is_game_over or self.is_paused:
            return

        if event.type == pygame.KEYDOWN:
            # Nhảy (SPACE / W / UP)
            if event.key in [pygame.K_SPACE, pygame.K_w, pygame.K_UP]:
                if not self.is_jumping:
                    self.velocity_y = -14
                    self.is_jumping = True
                    synth.play('jump')
                    
            # BMO CHOP! (F / J / X / C)
            elif event.key in [pygame.K_f, pygame.K_j, pygame.K_x, pygame.K_c]:
                if not self.is_chopping:
                    self.is_chopping = True
                    self.chop_timer = 15
                    synth.play('chop')

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Hỗ trợ cảm ứng màn hình điện thoại / chuột
            if event.pos[0] > self.width * 0.65:
                # Chạm bên phải màn hình -> BMO CHOP!
                if not self.is_chopping:
                    self.is_chopping = True
                    self.chop_timer = 15
                    synth.play('chop')
            else:
                # Chạm bên trái màn hình -> Nhảy
                if not self.is_jumping:
                    self.velocity_y = -14
                    self.is_jumping = True
                    synth.play('jump')

    def update(self):
        if self.is_game_over or self.is_paused:
            return

        # Tăng tốc độ dần theo điểm số
        self.game_speed = 5.0 + min(6.0, self.score / 500.0)
        self.scroll_x += self.game_speed
        
        # Trọng lực & Nhảy
        self.velocity_y += 0.8
        self.player_y += self.velocity_y
        if self.player_y >= self.ground_y - self.player_h:
            self.player_y = self.ground_y - self.player_h
            self.velocity_y = 0
            self.is_jumping = False

        # Thời gian hồi đòn Chém (BMO Chop)
        if self.is_chopping:
            self.chop_timer -= 1
            if self.chop_timer <= 0:
                self.is_chopping = False

        # Di chuyển mây
        for c in self.clouds:
            c['x'] -= self.game_speed * 0.2
            if c['x'] + c['w'] < 0:
                c['x'] = self.width + random.randint(50, 150)
                c['y'] = random.randint(50, 180)

        # Sinh chướng ngại vật & vật phẩm ngẫu nhiên
        self.spawn_timer += 1
        if self.spawn_timer > max(45, 95 - int(self.score / 100)):
            self.spawn_timer = 0
            self._spawn_random_entity()

        # Cập nhật chướng ngại vật
        player_rect = pygame.Rect(self.player_x, self.player_y, self.player_w, self.player_h)
        chop_rect = pygame.Rect(self.player_x + self.player_w, self.player_y - 10, 50, self.player_h + 20) if self.is_chopping else None

        for obs in self.obstacles[:]:
            obs['x'] -= self.game_speed
            obs_rect = pygame.Rect(obs['x'], obs['y'], obs['w'], obs['h'])

            # Kiểm tra trúng đòn BMO CHOP!
            if chop_rect and chop_rect.colliderect(obs_rect) and obs.get('can_slash', True):
                self._create_particles(obs['x'] + obs['w']//2, obs['y'] + obs['h']//2, obs['color'])
                self.obstacles.remove(obs)
                self.score += 80
                synth.play('hit')
                continue

            # Va chạm người chơi
            if player_rect.colliderect(obs_rect):
                self.lives -= 1
                self._create_particles(self.player_x + 20, self.player_y + 25, BMO_HEART_RED)
                synth.play('hit')
                self.obstacles.remove(obs)
                if self.lives <= 0:
                    self.is_game_over = True
                    synth.play('game_over')
                continue

            # Ra khỏi màn hình
            if obs['x'] + obs['w'] < 0:
                self.obstacles.remove(obs)
                self.score += 15

        # Cập nhật vật phẩm (Pin năng lượng, Kim cương)
        for item in self.collectibles[:]:
            item['x'] -= self.game_speed
            item_rect = pygame.Rect(item['x'], item['y'], item['w'], item['h'])

            if player_rect.colliderect(item_rect):
                self._create_particles(item['x'] + 10, item['y'] + 10, item['color'])
                self.score += item['points']
                synth.play('coin')
                self.collectibles.remove(item)
            elif item['x'] + item['w'] < 0:
                self.collectibles.remove(item)

        # Cập nhật hạt nổ pixel
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['alpha'] -= 10
            if p['alpha'] <= 0:
                self.particles.remove(p)

    def _spawn_random_entity(self):
        """Sinh quái vật hoặc vật phẩm mới."""
        rand = random.random()
        if rand < 0.45:
            # Quái vật Gnome trên mặt đất (có thể chém bằng BMO Chop)
            self.obstacles.append({
                'type': 'gnome', 'x': self.width + 20, 'y': self.ground_y - 36,
                'w': 32, 'h': 36, 'color': (180, 50, 50), 'can_slash': True
            })
        elif rand < 0.70:
            # Dơi Marceline bay lơ lửng
            self.obstacles.append({
                'type': 'bat', 'x': self.width + 20, 'y': self.ground_y - 85,
                'w': 34, 'h': 24, 'color': (60, 30, 80), 'can_slash': True
            })
        elif rand < 0.85:
            # Bụi gai (Spikes - phải nhảy qua)
            self.obstacles.append({
                'type': 'spike', 'x': self.width + 20, 'y': self.ground_y - 28,
                'w': 28, 'h': 28, 'color': (30, 70, 30), 'can_slash': False
            })
        else:
            # Pin năng lượng hoặc Kim cương
            self.collectibles.append({
                'type': 'battery', 'x': self.width + 20, 'y': self.ground_y - random.randint(50, 110),
                'w': 22, 'h': 26, 'color': BMO_YELLOW, 'points': 50
            })

    def _create_particles(self, x, y, color):
        for _ in range(8):
            self.particles.append({
                'x': x, 'y': y,
                'vx': random.uniform(-4, 4),
                'vy': random.uniform(-4, 4),
                'color': color,
                'alpha': 255
            })

    def draw(self, surface):
        surface.fill(BMO_TEAL)
        
        # 1. Vẽ mây nền
        for c in self.clouds:
            pygame.draw.ellipse(surface, (215, 245, 240), (c['x'], c['y'], c['w'], 35))
            
        # 2. Vẽ dãy núi kẹo xa xa
        for m in self.mountains:
            mx = (m['x'] - self.scroll_x * 0.3) % (self.width + 200) - 100
            pygame.draw.polygon(surface, m['color'], [(mx, self.ground_y), (mx + 100, self.ground_y - m['h']), (mx + 200, self.ground_y)])

        # 3. Vẽ mặt đất & cỏ
        pygame.draw.rect(surface, (70, 168, 120), (0, self.ground_y, self.width, self.height - self.ground_y))
        pygame.draw.line(surface, (40, 110, 80), (0, self.ground_y), (self.width, self.ground_y), 4)
        
        # Vân cỏ cuộn
        for gx in range(0, self.width + 40, 30):
            ox = (gx - int(self.scroll_x)) % self.width
            pygame.draw.line(surface, (50, 130, 90), (ox, self.ground_y), (ox - 8, self.ground_y + 12), 3)

        # 4. Vẽ Chướng ngại vật
        for obs in self.obstacles:
            if obs['type'] == 'gnome':
                # Gnome đỏ pixel
                pygame.draw.rect(surface, obs['color'], (obs['x'], obs['y'], obs['w'], obs['h']), border_radius=4)
                pygame.draw.polygon(surface, BMO_HEART_RED, [(obs['x'], obs['y']), (obs['x'] + obs['w']//2, obs['y'] - 14), (obs['x'] + obs['w'], obs['y'])])
                pygame.draw.circle(surface, BMO_BLACK, (int(obs['x'] + 10), int(obs['y'] + 14)), 3)
            elif obs['type'] == 'bat':
                # Dơi tím bay vỗ cánh
                wing_osc = int(6 * math.sin(self.scroll_x * 0.2))
                pygame.draw.ellipse(surface, obs['color'], (obs['x'] + 8, obs['y'] + 6, 18, 14))
                pygame.draw.polygon(surface, obs['color'], [(obs['x'], obs['y'] + wing_osc), (obs['x'] + 12, obs['y'] + 8), (obs['x'] + 8, obs['y'] + 16)])
                pygame.draw.polygon(surface, obs['color'], [(obs['x'] + 34, obs['y'] + wing_osc), (obs['x'] + 22, obs['y'] + 8), (obs['x'] + 26, obs['y'] + 16)])
            else:
                # Bụi gai
                pygame.draw.polygon(surface, obs['color'], [(obs['x'], obs['y'] + obs['h']), (obs['x'] + obs['w']//2, obs['y']), (obs['x'] + obs['w'], obs['y'] + obs['h'])])

        # 5. Vẽ Vật phẩm (Pin năng lượng)
        for item in self.collectibles:
            # Pin vàng nhấp nháy
            pygame.draw.rect(surface, item['color'], (item['x'], item['y'] + 4, item['w'], item['h'] - 4), border_radius=3)
            pygame.draw.rect(surface, BMO_BLACK, (item['x'] + 5, item['y'], item['w'] - 10, 4))
            pygame.draw.line(surface, BMO_BLACK, (item['x'] + 11, item['y'] + 10), (item['x'] + 11, item['y'] + 18), 3)

        # 6. Vẽ Nhân vật BMO Runner
        px, py = self.player_x, self.player_y
        # Thân máy BMO
        pygame.draw.rect(surface, BMO_BODY_TEAL, (px, py, self.player_w, self.player_h), border_radius=6)
        # Màn hình BMO
        pygame.draw.rect(surface, BMO_TEAL, (px + 6, py + 6, self.player_w - 12, 22), border_radius=3)
        # Mắt & nụ cười quyết tâm
        pygame.draw.circle(surface, BMO_BLACK, (px + 14, py + 16), 3)
        pygame.draw.circle(surface, BMO_BLACK, (px + 28, py + 16), 3)
        pygame.draw.line(surface, BMO_BLACK, (px + 18, py + 22), (px + 24, py + 22), 2)
        
        # Nút bấm nhỏ trên thân
        pygame.draw.rect(surface, BMO_YELLOW, (px + 8, py + 34, 8, 8))
        pygame.draw.circle(surface, BMO_BLUE, (px + 24, py + 38), 3)
        pygame.draw.circle(surface, BMO_GREEN, (px + 34, py + 38), 3)

        # Chân BMO chạy hoạt họa
        leg_frame = int((self.scroll_x / 8) % 4)
        if not self.is_jumping:
            if leg_frame in [0, 2]:
                pygame.draw.rect(surface, BMO_BLACK, (px + 10, py + self.player_h, 6, 8))
                pygame.draw.rect(surface, BMO_BLACK, (px + 28, py + self.player_h, 6, 8))
            else:
                pygame.draw.rect(surface, BMO_BLACK, (px + 14, py + self.player_h, 6, 8))
                pygame.draw.rect(surface, BMO_BLACK, (px + 24, py + self.player_h, 6, 8))
        else:
            # Co chân khi nhảy
            pygame.draw.rect(surface, BMO_BLACK, (px + 10, py + self.player_h - 4, 8, 6))
            pygame.draw.rect(surface, BMO_BLACK, (px + 26, py + self.player_h - 4, 8, 6))

        # Hiệu ứng vung kiếm BMO CHOP!
        if self.is_chopping:
            slash_arc_rect = pygame.Rect(px + self.player_w - 10, py - 16, 60, 60)
            pygame.draw.arc(surface, BMO_WHITE, slash_arc_rect, -math.pi/4, math.pi/2, 6)
            pygame.draw.arc(surface, BMO_YELLOW, slash_arc_rect, -math.pi/4, math.pi/2, 2)
            # Dòng chữ "BMO CHOP!"
            chop_text = self.font_ui.render("CHOP!", True, BMO_HEART_RED)
            surface.blit(chop_text, (px + self.player_w + 10, py - 20))

        # 7. Vẽ hạt nổ
        for p in self.particles:
            p_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            p_surf.fill((*p['color'], max(0, int(p['alpha']))))
            surface.blit(p_surf, (int(p['x']), int(p['y'])))

        # 8. Thanh HUD & Máu (Hearts)
        self.draw_hud(surface)
        
        # Vẽ trái tim mạng sống
        for i in range(3):
            heart_color = BMO_HEART_RED if i < self.lives else (80, 80, 80)
            hx = 160 + i * 24
            pygame.draw.circle(surface, heart_color, (hx, 18), 6)

        # Hướng dẫn nút bấm góc dưới
        help_t = self.font_ui.render("[SPACE/W]: Jump   |   [F/J]: BMO CHOP!", True, (30, 60, 50))
        surface.blit(help_t, (self.width // 2 - 160, self.height - 30))

        # 9. Game Over Screen
        if self.is_game_over:
            self.draw_game_over_screen(surface)
