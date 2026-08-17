"""
BMO Face Renderer & Animation Engine (Enhanced Edition)
Vẽ khuôn mặt BMO với hơn 10 biểu cảm, chớp mắt tự nhiên, mắt dõi theo chuột,
chỉ báo pin sập nguồn, hiệu ứng nôn nhổ/nhét băng game (Cartridge Spit/Insert),
và màn hình thay pin tương tác.
"""
import pygame
import math
import random
import time
from .constants import (
    BMO_TEAL, BMO_BODY_TEAL, BMO_DARK_TEAL, BMO_BLACK, BMO_WHITE,
    BMO_ROSE, BMO_HEART_RED, BMO_YELLOW, BMO_BLUE, BMO_GREEN,
    BMO_CRT_OVERLAY, BMO_TEAR_BLUE, Expression
)

class FaceRenderer:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        
        # Trạng thái biểu cảm
        self.current_expression = Expression.IDLE
        self.is_blinking = False
        self.blink_timer = 0
        self.next_blink_time = time.time() + random.uniform(2.5, 4.5)
        
        # Mắt theo dõi chuột (Eye Tracking)
        self.pupil_offset = [0, 0]
        self.target_pupil_offset = [0, 0]
        
        # Animation variables
        self.anim_frame = 0
        self.blush_intensity = 0.0
        self.teardrop_y = 0
        self.zzz_particles = []
        self.music_notes = []
        self.heart_pulse = 1.0
        
        # Tùy chọn hiển thị
        self.show_bezel = False         # Viền thân máy BMO
        self.show_scanlines = True      # Vân CRT scanlines
        self.scanline_surface = self._create_scanline_surface()
        
        # Phông chữ
        pygame.font.init()
        self.font_subtitle = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 20, bold=True)
        self.font_hud = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 13, bold=True)
        self.font_cartridge = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 15, bold=True)
        self.font_battery_alert = pygame.font.SysFont("Segoe UI, Arial, sans-serif", 24, bold=True)
        self.font_zzz = pygame.font.SysFont("Arial", 22, bold=True)

    def _create_scanline_surface(self):
        """Tạo lớp phủ hiệu ứng màn hình CRT scanlines."""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for y in range(0, self.height, 4):
            pygame.draw.line(surf, (0, 0, 0, 35), (0, y), (self.width, y), 1)
        return surf

    def set_expression(self, expr):
        """Chuyển đổi biểu cảm."""
        self.current_expression = expr
        if expr == Expression.HAPPY or expr == Expression.HEART_EYES:
            self.blush_intensity = 1.0
        elif expr == Expression.CRYING:
            self.teardrop_y = 0

    def update(self, is_talking=False, mouse_pos=None):
        """Cập nhật các hoạt ảnh theo từng khung hình."""
        now = time.time()
        self.anim_frame += 1
        
        # Tự động đồng bộ trạng thái nói chuyện nếu không bị khóa ở biểu cảm đặc biệt
        if is_talking and self.current_expression in [Expression.IDLE, Expression.TALKING, Expression.HAPPY]:
            self.current_expression = Expression.TALKING
        elif not is_talking and self.current_expression == Expression.TALKING:
            self.current_expression = Expression.IDLE

        # Xử lý chớp mắt tự nhiên
        if now >= self.next_blink_time and self.current_expression in [Expression.IDLE, Expression.TALKING]:
            self.is_blinking = True
            if now >= self.next_blink_time + 0.16: # Thời gian chớp mắt 160ms
                self.is_blinking = False
                self.next_blink_time = now + random.uniform(2.5, 5.0)

        # Tính toán góc liếc mắt theo chuột
        if mouse_pos:
            center_x, center_y = self.width // 2, self.height // 3 + 20
            dx = mouse_pos[0] - center_x
            dy = mouse_pos[1] - center_y
            dist = math.hypot(dx, dy)
            max_offset = 8.0
            if dist > 0:
                self.target_pupil_offset = [
                    (dx / dist) * min(max_offset, dist * 0.03),
                    (dy / dist) * min(max_offset, dist * 0.03)
                ]
        else:
            self.target_pupil_offset = [0, 0]

        # Làm mượt chuyển động con ngươi (lerp)
        self.pupil_offset[0] += (self.target_pupil_offset[0] - self.pupil_offset[0]) * 0.2
        self.pupil_offset[1] += (self.target_pupil_offset[1] - self.pupil_offset[1]) * 0.2

        # Cập nhật hạt Zzz khi ngủ
        if self.current_expression in [Expression.SLEEPY, Expression.SLEEPING]:
            if random.random() < 0.04 and len(self.zzz_particles) < 5:
                self.zzz_particles.append({
                    'x': self.width * 0.65 + random.randint(-20, 20),
                    'y': self.height * 0.35,
                    'size': random.randint(16, 26),
                    'alpha': 255,
                    'speed_y': random.uniform(0.8, 1.6),
                    'speed_x': random.uniform(0.3, 0.7)
                })

        for z in self.zzz_particles[:]:
            z['y'] -= z['speed_y']
            z['x'] += z['speed_x']
            z['alpha'] -= 1.8
            if z['alpha'] <= 0 or z['y'] < 50:
                self.zzz_particles.remove(z)

        # Cập nhật nốt nhạc khi hát
        if self.current_expression == Expression.SINGING:
            if random.random() < 0.06 and len(self.music_notes) < 6:
                self.music_notes.append({
                    'x': self.width // 2 + random.randint(-120, 120),
                    'y': self.height // 2,
                    'char': random.choice(['♪', '♫', '♬']),
                    'alpha': 255,
                    'speed_y': random.uniform(1.2, 2.0),
                    'color': random.choice([BMO_BLUE, BMO_HEART_RED, BMO_YELLOW, BMO_GREEN])
                })

        for n in self.music_notes[:]:
            n['y'] -= n['speed_y']
            n['alpha'] -= 2.5
            if n['alpha'] <= 0 or n['y'] < 40:
                self.music_notes.remove(n)

        # Nước mắt rơi
        if self.current_expression == Expression.CRYING:
            self.teardrop_y += 3
            if self.teardrop_y > 180:
                self.teardrop_y = 0

        # Mắt trái tim đập phồng
        if self.current_expression == Expression.HEART_EYES:
            self.heart_pulse = 1.0 + 0.15 * math.sin(self.anim_frame * 0.2)

    def draw(self, surface, subtitle="", battery_level=100):
        """Vẽ toàn bộ khuôn mặt BMO lên bề mặt."""
        # 1. Vẽ nền màn hình xanh ngọc
        surface.fill(BMO_TEAL)
        
        # Tọa độ mắt
        left_eye_center = (self.width // 3, self.height // 3 + 20)
        right_eye_center = (2 * self.width // 3, self.height // 3 + 20)
        eye_radius = 24
        
        # 2. VẼ MẮT THEO BIỂU CẢM
        self._draw_eyes(surface, left_eye_center, right_eye_center, eye_radius)
        
        # 3. VẼ MÁ HỒNG (BLUSH)
        self._draw_cheeks(surface, left_eye_center, right_eye_center)
        
        # 4. VẼ MIỆNG
        self._draw_mouth(surface)
        
        # 5. VẼ CÁC HIỆU ỨNG ĐẶC BIỆT (Zzz, nốt nhạc, nước mắt, glitch)
        self._draw_special_effects(surface, left_eye_center, right_eye_center)
        
        # 6. HIỆU ỨNG SẮP HẾT PIN (DIMMING & LOW BATTERY GLITCH)
        if battery_level < 25:
            self._draw_low_battery_effects(surface, battery_level)

        # 7. VẼ SCANLINES CRT
        if self.show_scanlines:
            surface.blit(self.scanline_surface, (0, 0))
            
        # 8. VẼ BIỂU TƯỢNG PIN Ở GÓC TRÊN PHẢI (BATTERY HUD)
        self._draw_battery_hud(surface, battery_level)

        # 9. VẼ PHỤ ĐỀ / LỜI THOẠI CỦA BMO
        if subtitle:
            self._draw_subtitle(surface, subtitle)
            
        # 10. VẼ THÂN MÁY BMO (NẾU BẬT BEZEL)
        if self.show_bezel:
            self._draw_bmo_bezel(surface)

    def _draw_battery_hud(self, surface, battery_level):
        """Vẽ biểu tượng thanh pin retro ở góc trên phải."""
        bx = self.width - 95
        by = 14
        bw, bh = 42, 18
        
        # Vỏ ngoài pin
        pygame.draw.rect(surface, BMO_DARK_TEAL, (bx, by, bw, bh), 2, border_radius=4)
        # Cực dương pin (nhỏ bên phải)
        pygame.draw.rect(surface, BMO_DARK_TEAL, (bx + bw, by + 4, 4, 10), border_radius=1)
        
        # Màu thanh pin theo mức
        if battery_level > 35:
            b_col = BMO_GREEN
        elif battery_level > 15:
            b_col = BMO_YELLOW
        else:
            # Nhấp nháy đỏ báo động
            b_col = BMO_HEART_RED if (self.anim_frame // 15) % 2 == 0 else (120, 30, 30)
            
        inner_w = int((bw - 6) * max(0.05, battery_level / 100.0))
        pygame.draw.rect(surface, b_col, (bx + 3, by + 3, inner_w, bh - 6), border_radius=2)
        
        # Số % pin
        pct_str = f"{int(battery_level)}%"
        p_surf = self.font_hud.render(pct_str, True, BMO_DARK_TEAL if battery_level > 15 else BMO_HEART_RED)
        surface.blit(p_surf, (bx - 38, by + 1))

    def _draw_low_battery_effects(self, surface, battery_level):
        """Tạo hiệu ứng mờ dần và glitch khi pin yếu."""
        # 1. Lớp phủ tối dần (Dimming)
        darkness = int((25 - battery_level) * 8.5)
        darkness = min(220, max(15, darkness))
        dim_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        dim_surf.fill((10, 15, 12, darkness))
        surface.blit(dim_surf, (0, 0))
        
        # 2. Vệt glitch giật màn hình
        if battery_level <= 15 and random.random() < 0.35:
            for _ in range(3):
                gy = random.randint(0, self.height)
                gh = random.randint(6, 25)
                shift = random.randint(-15, 15)
                sub_rect = pygame.Rect(0, gy, self.width, gh)
                sub_surf = surface.subsurface(sub_rect).copy()
                surface.blit(sub_surf, (shift, gy))

    def _draw_eyes(self, surface, left_eye, right_eye, radius):
        """Vẽ cặp mắt BMO với đa dạng trạng thái."""
        expr = self.current_expression
        
        # Nếu đang chớp mắt hoặc ngủ
        if self.is_blinking or expr in [Expression.SLEEPY, Expression.SLEEPING]:
            # Hai đường thẳng nằm ngang
            pygame.draw.line(surface, BMO_BLACK, (left_eye[0] - 26, left_eye[1]), (left_eye[0] + 26, left_eye[1]), 8)
            pygame.draw.line(surface, BMO_BLACK, (right_eye[0] - 26, right_eye[1]), (right_eye[0] + 26, right_eye[1]), 8)
            return

        # Mắt nôn mửa nhổ băng game: > <
        if expr == Expression.VOMIT:
            pygame.draw.line(surface, BMO_BLACK, (left_eye[0] - 24, left_eye[1] - 14), (left_eye[0] + 20, left_eye[1]), 7)
            pygame.draw.line(surface, BMO_BLACK, (left_eye[0] - 24, left_eye[1] + 14), (left_eye[0] + 20, left_eye[1]), 7)
            pygame.draw.line(surface, BMO_BLACK, (right_eye[0] + 24, right_eye[1] - 14), (right_eye[0] - 20, right_eye[1]), 7)
            pygame.draw.line(surface, BMO_BLACK, (right_eye[0] + 24, right_eye[1] + 14), (right_eye[0] - 20, right_eye[1]), 7)
            return

        # Mắt cười hạnh phúc / Hát: ^ ^ (Vòng cung ngược)
        if expr in [Expression.HAPPY, Expression.LAUGH, Expression.SINGING]:
            rect_l = pygame.Rect(left_eye[0] - 26, left_eye[1] - 20, 52, 40)
            rect_r = pygame.Rect(right_eye[0] - 26, right_eye[1] - 20, 52, 40)
            pygame.draw.arc(surface, BMO_BLACK, rect_l, 0, math.pi, 8)
            pygame.draw.arc(surface, BMO_BLACK, rect_r, 0, math.pi, 8)
            return

        # Mắt trái tim (Heart Eyes)
        if expr == Expression.HEART_EYES:
            self._draw_heart(surface, left_eye[0], left_eye[1], int(22 * self.heart_pulse))
            self._draw_heart(surface, right_eye[0], right_eye[1], int(22 * self.heart_pulse))
            return

        # Mắt giận dữ BMO Chop: \ /
        if expr == Expression.ANGRY_CHOP:
            pygame.draw.polygon(surface, BMO_BLACK, [
                (left_eye[0] - 24, left_eye[1] - 12),
                (left_eye[0] + 24, left_eye[1] + 16),
                (left_eye[0] + 16, left_eye[1] + 24),
                (left_eye[0] - 24, left_eye[1] + 6)
            ])
            pygame.draw.polygon(surface, BMO_BLACK, [
                (right_eye[0] + 24, right_eye[1] - 12),
                (right_eye[0] - 24, right_eye[1] + 16),
                (right_eye[0] - 16, right_eye[1] + 24),
                (right_eye[0] + 24, right_eye[1] + 6)
            ])
            pygame.draw.line(surface, BMO_BLACK, (left_eye[0] - 30, left_eye[1] - 25), (left_eye[0] + 20, left_eye[1] - 10), 6)
            pygame.draw.line(surface, BMO_BLACK, (right_eye[0] + 30, right_eye[1] - 25), (right_eye[0] - 20, right_eye[1] - 10), 6)
            return

        # Mắt ngạc nhiên / Sốc: O O to tròn
        if expr in [Expression.SHOCKED, Expression.SURPRISED]:
            pygame.draw.circle(surface, BMO_BLACK, left_eye, radius + 8)
            pygame.draw.circle(surface, BMO_BLACK, right_eye, radius + 8)
            pygame.draw.circle(surface, BMO_WHITE, (left_eye[0] - 6, left_eye[1] - 6), 9)
            pygame.draw.circle(surface, BMO_WHITE, (right_eye[0] - 6, right_eye[1] - 6), 9)
            return

        # Mắt buồn / Khóc: U U
        if expr in [Expression.SAD, Expression.CRYING]:
            rect_l = pygame.Rect(left_eye[0] - 24, left_eye[1] - 10, 48, 36)
            rect_r = pygame.Rect(right_eye[0] - 24, right_eye[1] - 10, 48, 36)
            pygame.draw.arc(surface, BMO_BLACK, rect_l, math.pi, 2 * math.pi, 7)
            pygame.draw.arc(surface, BMO_BLACK, rect_r, math.pi, 2 * math.pi, 7)
            return

        # Mắt mặc định (IDLE / TALKING): Tròn đen + con ngươi liếc nhẹ + điểm sáng trắng
        px = int(self.pupil_offset[0])
        py = int(self.pupil_offset[1])
        
        pygame.draw.circle(surface, BMO_BLACK, (left_eye[0] + px, left_eye[1] + py), radius)
        pygame.draw.circle(surface, BMO_BLACK, (right_eye[0] + px, right_eye[1] + py), radius)
        
        # Điểm sáng dễ thương
        pygame.draw.circle(surface, BMO_WHITE, (left_eye[0] + px - 7, left_eye[1] + py - 7), 6)
        pygame.draw.circle(surface, BMO_WHITE, (right_eye[0] + px - 7, right_eye[1] + py - 7), 6)
        pygame.draw.circle(surface, BMO_WHITE, (left_eye[0] + px + 5, left_eye[1] + py + 6), 3)
        pygame.draw.circle(surface, BMO_WHITE, (right_eye[0] + px + 5, right_eye[1] + py + 6), 3)

    def _draw_cheeks(self, surface, left_eye, right_eye):
        """Vẽ hai má hồng đáng yêu."""
        expr = self.current_expression
        is_blushing = expr in [Expression.HAPPY, Expression.LAUGH, Expression.HEART_EYES, Expression.SINGING]
        
        if is_blushing or self.blush_intensity > 0.1:
            alpha = int(180 * max(self.blush_intensity, 1.0 if is_blushing else 0.0))
            blush_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.ellipse(blush_surf, (*BMO_ROSE, alpha), (left_eye[0] - 50, left_eye[1] + 28, 36, 18))
            pygame.draw.ellipse(blush_surf, (*BMO_ROSE, alpha), (right_eye[0] + 14, right_eye[1] + 28, 36, 18))
            surface.blit(blush_surf, (0, 0))

    def _draw_mouth(self, surface):
        """Vẽ các hình dạng khuôn miệng BMO."""
        expr = self.current_expression
        cx = self.width // 2
        top = self.height // 2 + 38

        # 0. Miệng nôn mửa nhổ băng game
        if expr == Expression.VOMIT:
            pygame.draw.ellipse(surface, BMO_BLACK, (cx - 36, top - 2, 72, 48))
            pygame.draw.ellipse(surface, (60, 110, 90), (cx - 28, top + 6, 56, 34))
            return

        # 1. Trạng thái nói chuyện (Talking Lip-Sync bập bẹ 4 khung hình)
        if expr == Expression.TALKING:
            frame = (self.anim_frame // 6) % 4
            if frame == 0:
                pygame.draw.rect(surface, BMO_BLACK, (cx - 24, top + 14, 48, 8), border_radius=3)
            elif frame == 1:
                pygame.draw.rect(surface, BMO_BLACK, (cx - 20, top + 6, 40, 20), border_radius=4)
            elif frame == 2:
                pygame.draw.rect(surface, BMO_BLACK, (cx - 16, top, 32, 30), border_radius=5)
                pygame.draw.rect(surface, BMO_ROSE, (cx - 8, top + 18, 16, 8), border_radius=3)
            else:
                pygame.draw.polygon(surface, BMO_BLACK, [(cx - 26, top + 8), (cx + 26, top + 8), (cx + 18, top + 26), (cx - 18, top + 26)])
            return

        # 2. Cười to / Vui sướng
        if expr in [Expression.HAPPY, Expression.LAUGH]:
            rect_m = pygame.Rect(cx - 30, top - 4, 60, 42)
            pygame.draw.arc(surface, BMO_BLACK, rect_m, math.pi, 2 * math.pi, 8)
            pygame.draw.line(surface, BMO_BLACK, (cx - 30, top + 17), (cx + 30, top + 17), 7)
            pygame.draw.circle(surface, BMO_ROSE, (cx, top + 14), 10)
            return

        # 3. BMO Chop! (Tức giận quyết tâm)
        if expr == Expression.ANGRY_CHOP:
            pygame.draw.rect(surface, BMO_BLACK, (cx - 28, top + 4, 56, 22), border_radius=3)
            pygame.draw.line(surface, BMO_WHITE, (cx - 26, top + 15), (cx + 26, top + 15), 3)
            return

        # 4. Ngạc nhiên / Sốc: Chữ O
        if expr in [Expression.SHOCKED, Expression.SURPRISED]:
            pygame.draw.ellipse(surface, BMO_BLACK, (cx - 16, top + 4, 32, 38))
            return

        # 5. Hát (Singing): Chữ O tròn nhỏ
        if expr == Expression.SINGING:
            osc = int(4 * math.sin(self.anim_frame * 0.3))
            pygame.draw.circle(surface, BMO_BLACK, (cx, top + 14), 16 + osc)
            pygame.draw.circle(surface, BMO_ROSE, (cx, top + 16), 8)
            return

        # 6. Buồn / Khóc: Miệng mếu cong xuống
        if expr in [Expression.SAD, Expression.CRYING]:
            rect_sad = pygame.Rect(cx - 24, top + 10, 48, 30)
            pygame.draw.arc(surface, BMO_BLACK, rect_sad, 0, math.pi, 6)
            return

        # 7. Mặc định (IDLE): Nụ cười nhẹ đặc trưng BMO
        y = top + 14
        pygame.draw.line(surface, BMO_BLACK, (cx - 22, y), (cx + 22, y), 6)
        pygame.draw.line(surface, BMO_BLACK, (cx - 28, y - 5), (cx - 22, y), 5)
        pygame.draw.line(surface, BMO_BLACK, (cx + 22, y), (cx + 28, y - 5), 5)

    def _draw_heart(self, surface, x, y, size):
        """Vẽ hình trái tim pixel/vector."""
        half = size // 2
        pygame.draw.circle(surface, BMO_HEART_RED, (x - half // 2, y - half // 3), half)
        pygame.draw.circle(surface, BMO_HEART_RED, (x + half // 2, y - half // 3), half)
        points = [
            (x - size + 2, y - half // 4),
            (x + size - 2, y - half // 4),
            (x, y + size)
        ]
        pygame.draw.polygon(surface, BMO_HEART_RED, points)

    def _draw_special_effects(self, surface, left_eye, right_eye):
        """Vẽ các hiệu ứng giọt nước mắt, Zzz, nốt nhạc bay."""
        if self.current_expression == Expression.CRYING:
            ty = left_eye[1] + 15 + self.teardrop_y
            pygame.draw.circle(surface, BMO_TEAR_BLUE, (left_eye[0] - 10, ty), 8)
            pygame.draw.polygon(surface, BMO_TEAR_BLUE, [(left_eye[0] - 18, ty), (left_eye[0] - 2, ty), (left_eye[0] - 10, ty - 14)])
            
            ty_r = right_eye[1] + 15 + ((self.teardrop_y + 60) % 180)
            pygame.draw.circle(surface, BMO_TEAR_BLUE, (right_eye[0] + 10, ty_r), 8)
            pygame.draw.polygon(surface, BMO_TEAR_BLUE, [(right_eye[0] + 2, ty_r), (right_eye[0] + 18, ty_r), (right_eye[0] + 10, ty_r - 14)])

        for z in self.zzz_particles:
            z_surf = self.font_zzz.render("Z", True, BMO_BLACK)
            z_surf.set_alpha(int(z['alpha']))
            surface.blit(z_surf, (int(z['x']), int(z['y'])))

        for n in self.music_notes:
            n_font = pygame.font.SysFont("Segoe UI Symbol, Arial", 24, bold=True)
            n_surf = n_font.render(n['char'], True, n['color'])
            n_surf.set_alpha(int(n['alpha']))
            surface.blit(n_surf, (int(n['x']), int(n['y'])))

        if self.current_expression == Expression.GLITCH:
            for _ in range(6):
                gy = random.randint(0, self.height)
                gh = random.randint(4, 20)
                shift = random.randint(-25, 25)
                sub_rect = pygame.Rect(0, gy, self.width, gh)
                sub_surf = surface.subsurface(sub_rect).copy()
                surface.blit(sub_surf, (shift, gy))

    def _draw_subtitle(self, surface, text):
        """Vẽ bong bóng phụ đề câu nói ở cạnh dưới màn hình."""
        padding = 14
        lines = []
        words = text.split(' ')
        curr_line = ""
        
        for w in words:
            test_line = curr_line + (" " if curr_line else "") + w
            if self.font_subtitle.size(test_line)[0] < self.width - 80:
                curr_line = test_line
            else:
                lines.append(curr_line)
                curr_line = w
        if curr_line:
            lines.append(curr_line)

        total_h = len(lines) * 26 + padding * 2
        bar_y = self.height - total_h - 20
        
        bg_rect = pygame.Rect(30, bar_y, self.width - 60, total_h)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (24, 28, 26, 210), (0, 0, bg_rect.width, bg_rect.height), border_radius=12)
        pygame.draw.rect(bg_surf, (141, 213, 201, 180), (0, 0, bg_rect.width, bg_rect.height), width=2, border_radius=12)
        surface.blit(bg_surf, bg_rect.topleft)

        for i, line in enumerate(lines):
            t_render = self.font_subtitle.render(line, True, BMO_WHITE)
            t_rect = t_render.get_rect(center=(self.width // 2, bar_y + padding + i * 26 + 10))
            surface.blit(t_render, t_rect)

    def _draw_bmo_bezel(self, surface):
        """Vẽ viền thân máy GameBoy / BMO case xung quanh."""
        bezel_w = 20
        pygame.draw.rect(surface, BMO_BODY_TEAL, (0, 0, self.width, bezel_w))
        pygame.draw.rect(surface, BMO_BODY_TEAL, (0, self.height - bezel_w, self.width, bezel_w))
        pygame.draw.rect(surface, BMO_BODY_TEAL, (0, 0, bezel_w, self.height))
        pygame.draw.rect(surface, BMO_BODY_TEAL, (self.width - bezel_w, 0, bezel_w, self.height))
        pygame.draw.rect(surface, BMO_DARK_TEAL, (bezel_w, bezel_w, self.width - 2*bezel_w, self.height - 2*bezel_w), 4, border_radius=8)

    def draw_cartridge_swap(self, surface, old_name, new_name, progress):
        """
        Vẽ hoạt ảnh BMO 'Nôn mửa' băng game cũ & nhét băng game mới vào.
        Progress từ 0.0 -> 1.0 (0.0-0.5: nhổ băng cũ ra; 0.5-1.0: cắm băng mới vào).
        """
        surface.fill(BMO_TEAL)
        cx, cy = self.width // 2, self.height // 2
        
        # Mắt nhăn & mặt rung nhẹ khi nôn
        shake_x = int(random.uniform(-4, 4)) if progress < 0.55 else 0
        shake_y = int(random.uniform(-3, 3)) if progress < 0.55 else 0
        
        left_eye = (self.width // 3 + shake_x, self.height // 3 + 20 + shake_y)
        right_eye = (2 * self.width // 3 + shake_x, self.height // 3 + 20 + shake_y)
        
        if progress < 0.5:
            self.set_expression(Expression.VOMIT)
        else:
            self.set_expression(Expression.EXCITED)
            
        self._draw_eyes(surface, left_eye, right_eye, 24)
        self._draw_cheeks(surface, left_eye, right_eye)
        self._draw_mouth(surface)
        
        cart_w, cart_h = 130, 85
        
        # Giai đoạn 1: Băng cũ văng ra bên trái kèm tiếng "Khục... ọc!"
        if progress < 0.5:
            p1 = progress / 0.5
            cart_x = cx - 20 - int(p1 * 340)
            cart_y = cy + 40 - int(math.sin(p1 * math.pi) * 80) + int(p1 * 120)
            rot_ang = int(p1 * 180)
            
            # Vẽ vệt khói/nước miếng bay theo băng
            for i in range(4):
                fx = cx - int(p1 * 200 * (i+1)/4)
                fy = cy + 40 + random.randint(-15, 15)
                pygame.draw.circle(surface, (120, 210, 180), (fx, fy), random.randint(6, 14))
                
            self._draw_cartridge_box(surface, cart_x, cart_y, old_name, color=(140, 145, 150), rot=rot_ang)
            
            # Bong bóng chữ vui nhộn
            b_surf = self.font_battery_alert.render("🤮 Khục... ỌC!", True, (200, 40, 40))
            surface.blit(b_surf, (cx - 160, cy - 80))
            
        # Giai đoạn 2: Băng mới từ trên bay vào cắm chặt vào miệng BMO
        else:
            p2 = (progress - 0.5) / 0.5
            target_x = cx - cart_w // 2
            target_y = cy + 20
            start_x = self.width + 40
            start_y = -80
            
            cart_x = int(start_x + (target_x - start_x) * p2)
            cart_y = int(start_y + (target_y - start_y) * p2)
            
            self._draw_cartridge_box(surface, cart_x, cart_y, new_name, color=BMO_YELLOW, rot=int((1-p2)*60))
            
            if p2 > 0.7:
                # Tia sáng 8-bit hào hứng
                for ang in range(0, 360, 45):
                    rad = math.radians(ang + self.anim_frame * 5)
                    lx = cx + math.cos(rad) * 90
                    ly = cy + 40 + math.sin(rad) * 90
                    pygame.draw.line(surface, BMO_WHITE, (cx, cy + 40), (lx, ly), 3)
                    
            b_surf = self.font_battery_alert.render("🎮 CLICK-CLACK! Loading...", True, BMO_BLACK)
            surface.blit(b_surf, b_surf.get_rect(center=(cx, cy - 80)))

        if self.show_scanlines:
            surface.blit(self.scanline_surface, (0, 0))

    def _draw_cartridge_box(self, surface, x, y, label, color=BMO_YELLOW, rot=0):
        """Vẽ hình chiếc băng game GameBoy / BMO cartridge."""
        w, h = 130, 85
        cart_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Thân băng
        pygame.draw.rect(cart_surf, color, (0, 0, w, h), border_radius=8)
        pygame.draw.rect(cart_surf, BMO_BLACK, (0, 0, w, h), width=3, border_radius=8)
        # Rãnh cắm phía dưới
        pygame.draw.rect(cart_surf, (80, 80, 80), (12, h - 8, w - 24, 8), border_radius=2)
        # Nhãn dán trên băng
        pygame.draw.rect(cart_surf, BMO_WHITE, (10, 8, w - 20, h - 26), border_radius=4)
        pygame.draw.rect(cart_surf, BMO_BLACK, (10, 8, w - 20, h - 26), width=2, border_radius=4)
        
        # Tên trò chơi trên nhãn
        t_s = self.font_cartridge.render(label[:12], True, BMO_BLACK)
        cart_surf.blit(t_s, t_s.get_rect(center=(w // 2, 28)))
        sub_s = self.font_hud.render("BMO GAME", True, (120, 120, 120))
        cart_surf.blit(sub_s, sub_s.get_rect(center=(w // 2, 48)))
        
        if rot != 0:
            cart_surf = pygame.transform.rotate(cart_surf, rot)
            
        surface.blit(cart_surf, (x, y))

    def draw_low_battery_screen(self, surface, p_hold_progress):
        """
        Vẽ màn hình BMO sập nguồn tối đen và cơ chế tương tác Thay 2 Cục Pin AA.
        """
        surface.fill((12, 16, 14)) # Đen tối màn hình tắt
        cx = self.width // 2
        cy = self.height // 2
        
        # 1. Mắt nhắm ngủ lịm / Màn hình tắt
        pygame.draw.line(surface, (40, 55, 48), (cx - 150, cy - 100), (cx - 90, cy - 100), 5)
        pygame.draw.line(surface, (40, 55, 48), (cx + 90, cy - 100), (cx + 150, cy - 100), 5)
        
        # 2. Tiêu đề cảnh báo
        alert_col = BMO_HEART_RED if (self.anim_frame // 20) % 2 == 0 else (160, 40, 40)
        t_alert = self.font_battery_alert.render("🪫 BMO SẬP NGUỒN (0% BATTERY)", True, alert_col)
        surface.blit(t_alert, t_alert.get_rect(center=(cx, 60)))
        
        sub_txt = self.font_subtitle.render("BMO: 'BMO cần pin... BMO is losing power...'", True, (160, 180, 175))
        surface.blit(sub_txt, sub_txt.get_rect(center=(cx, 95)))

        # 3. Khay chứa 2 viên pin AA của BMO
        slot_w, slot_h = 240, 110
        pygame.draw.rect(surface, (25, 34, 30), (cx - slot_w//2, cy - 20, slot_w, slot_h), border_radius=10)
        pygame.draw.rect(surface, (60, 85, 75), (cx - slot_w//2, cy - 20, slot_w, slot_h), width=3, border_radius=10)
        
        # Nhãn khay pin
        k_txt = self.font_hud.render("AA BATTERY COMPARTMENT (x2)", True, (120, 160, 145))
        surface.blit(k_txt, k_txt.get_rect(center=(cx, cy - 6)))

        # Vẽ 2 viên pin AA đang được nhét vào
        p_pct = min(1.0, max(0.0, p_hold_progress))
        
        for i, py_offset in enumerate([-18, 22]):
            bx = cx - 80 + int((1.0 - p_pct) * 120)
            by_pos = cy + 24 + py_offset
            # Thân pin AA vàng/xanh
            pygame.draw.rect(surface, BMO_YELLOW, (bx, by_pos, 140, 26), border_radius=4)
            pygame.draw.rect(surface, (180, 140, 20), (bx, by_pos, 140, 26), width=2, border_radius=4)
            pygame.draw.rect(surface, BMO_BLUE, (bx, by_pos, 40, 26), border_radius=4)
            # Cực dương
            pygame.draw.rect(surface, (200, 200, 200), (bx + 140, by_pos + 6, 6, 14), border_radius=2)
            # Chữ "AA"
            aa_s = self.font_hud.render("AA +", True, BMO_BLACK)
            surface.blit(aa_s, (bx + 55, by_pos + 4))

        # 4. Thanh tiến trình thay pin
        bar_w, bar_h = 320, 22
        bar_x = cx - bar_w // 2
        bar_y = cy + 120
        pygame.draw.rect(surface, (30, 40, 36), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
        fill_w = int(bar_w * p_pct)
        if fill_w > 0:
            pygame.draw.rect(surface, BMO_GREEN, (bar_x, bar_y, fill_w, bar_h), border_radius=6)
        pygame.draw.rect(surface, BMO_WHITE, (bar_x, bar_y, bar_w, bar_h), width=2, border_radius=6)

        # 5. Hướng dẫn bấm phím
        ins_surf = self.font_subtitle.render("👉 GIỮ PHÍM [P] HOẶC [SPACE] ĐỂ LẮP PIN MỚI", True, BMO_YELLOW)
        surface.blit(ins_surf, ins_surf.get_rect(center=(cx, cy + 175)))
        
        esc_surf = self.font_hud.render("[ESC]: Buộc hồi sinh ngay lập tức", True, (110, 135, 125))
        surface.blit(esc_surf, esc_surf.get_rect(center=(cx, self.height - 35)))

    def check_interaction_click(self, pos):
        """Xử lý sự kiện nhấp chuột tương tác lên khuôn mặt BMO."""
        x, y = pos
        # 1. Nhấp lên trán / đầu -> Xoa đầu (Heart Eyes)
        if 200 <= x <= 600 and 60 <= y <= 190:
            self.set_expression(Expression.HEART_EYES)
            return "pet_head"
            
        # 2. Nhấp vào má trái / má phải -> Nhéo má / Cù léc (Happy / Laugh)
        if (150 <= x <= 280 and 260 <= y <= 380) or (520 <= x <= 650 and 260 <= y <= 380):
            self.set_expression(Expression.LAUGH)
            return "tickle_cheek"
            
        # 3. Nhấp vào miệng -> Ngạc nhiên
        if 320 <= x <= 480 and 320 <= y <= 440:
            self.set_expression(Expression.SURPRISED)
            return "poke_mouth"
            
        return None
