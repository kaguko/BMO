"""
BMO Face Renderer & Animation Engine
Vẽ khuôn mặt BMO với hơn 10 biểu cảm, chớp mắt tự nhiên, mắt dõi theo chuột,
má hồng, hiệu ứng giọt nước mắt, chữ Zzz bay bổng và khung thân máy retro.
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
        self.font_subtitle = pygame.font.SysFont("Consolas, Arial, sans-serif", 20, bold=True)
        self.font_retro = pygame.font.SysFont("Consolas, monospace", 16)
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

    def draw(self, surface, subtitle=""):
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
        
        # 6. VẼ SCANLINES CRT
        if self.show_scanlines:
            surface.blit(self.scanline_surface, (0, 0))
            
        # 7. VẼ PHỤ ĐỀ / LỜI THOẠI CỦA BMO
        if subtitle:
            self._draw_subtitle(surface, subtitle)
            
        # 8. VẼ THÂN MÁY BMO (NẾU BẬT BEZEL)
        if self.show_bezel:
            self._draw_bmo_bezel(surface)

    def _draw_eyes(self, surface, left_eye, right_eye, radius):
        """Vẽ cặp mắt BMO với đa dạng trạng thái."""
        expr = self.current_expression
        
        # Nếu đang chớp mắt hoặc ngủ
        if self.is_blinking or expr in [Expression.SLEEPY, Expression.SLEEPING]:
            # Hai đường thẳng nằm ngang
            pygame.draw.line(surface, BMO_BLACK, (left_eye[0] - 26, left_eye[1]), (left_eye[0] + 26, left_eye[1]), 8)
            pygame.draw.line(surface, BMO_BLACK, (right_eye[0] - 26, right_eye[1]), (right_eye[0] + 26, right_eye[1]), 8)
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
            # Mắt xếch quyết tâm
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
            # Chân mày nhíu lại
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
            
            # Má trái & Má phải (hình bầu dục hồng pastel)
            pygame.draw.ellipse(blush_surf, (*BMO_ROSE, alpha), (left_eye[0] - 50, left_eye[1] + 28, 36, 18))
            pygame.draw.ellipse(blush_surf, (*BMO_ROSE, alpha), (right_eye[0] + 14, right_eye[1] + 28, 36, 18))
            surface.blit(blush_surf, (0, 0))

    def _draw_mouth(self, surface):
        """Vẽ các hình dạng khuôn miệng BMO."""
        expr = self.current_expression
        cx = self.width // 2
        top = self.height // 2 + 38

        # 1. Trạng thái nói chuyện (Talking Lip-Sync bập bẹ 4 khung hình)
        if expr == Expression.TALKING:
            frame = (self.anim_frame // 6) % 4
            if frame == 0:
                pygame.draw.rect(surface, BMO_BLACK, (cx - 24, top + 14, 48, 8), border_radius=3)
            elif frame == 1:
                pygame.draw.rect(surface, BMO_BLACK, (cx - 20, top + 6, 40, 20), border_radius=4)
            elif frame == 2:
                pygame.draw.rect(surface, BMO_BLACK, (cx - 16, top, 32, 30), border_radius=5)
                # Khe lưỡi hồng bên trong
                pygame.draw.rect(surface, BMO_ROSE, (cx - 8, top + 18, 16, 8), border_radius=3)
            else:
                # Miệng cười nói
                pygame.draw.polygon(surface, BMO_BLACK, [(cx - 26, top + 8), (cx + 26, top + 8), (cx + 18, top + 26), (cx - 18, top + 26)])
            return

        # 2. Cười to / Vui sướng
        if expr in [Expression.HAPPY, Expression.LAUGH]:
            # Miệng hình bán nguyệt cười to
            rect_m = pygame.Rect(cx - 30, top - 4, 60, 42)
            pygame.draw.arc(surface, BMO_BLACK, rect_m, math.pi, 2 * math.pi, 8)
            pygame.draw.line(surface, BMO_BLACK, (cx - 30, top + 17), (cx + 30, top + 17), 7)
            # Lưỡi hồng bên trong
            pygame.draw.circle(surface, BMO_ROSE, (cx, top + 14), 10)
            return

        # 3. BMO Chop! (Tức giận quyết tâm)
        if expr == Expression.ANGRY_CHOP:
            # Miệng mở gầm gừ hình chữ nhật răng cưa
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
        # Vẽ 2 vòng tròn tai tim + 1 tam giác đáy
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
        # Giọt nước mắt rơi khi khóc
        if self.current_expression == Expression.CRYING:
            ty = left_eye[1] + 15 + self.teardrop_y
            pygame.draw.circle(surface, BMO_TEAR_BLUE, (left_eye[0] - 10, ty), 8)
            pygame.draw.polygon(surface, BMO_TEAR_BLUE, [(left_eye[0] - 18, ty), (left_eye[0] - 2, ty), (left_eye[0] - 10, ty - 14)])
            
            ty_r = right_eye[1] + 15 + ((self.teardrop_y + 60) % 180)
            pygame.draw.circle(surface, BMO_TEAR_BLUE, (right_eye[0] + 10, ty_r), 8)
            pygame.draw.polygon(surface, BMO_TEAR_BLUE, [(right_eye[0] + 2, ty_r), (right_eye[0] + 18, ty_r), (right_eye[0] + 10, ty_r - 14)])

        # Chữ Zzz bay khi ngủ
        for z in self.zzz_particles:
            z_surf = self.font_zzz.render("Z", True, BMO_BLACK)
            z_surf.set_alpha(int(z['alpha']))
            surface.blit(z_surf, (int(z['x']), int(z['y'])))

        # Nốt nhạc bay khi hát
        for n in self.music_notes:
            n_font = pygame.font.SysFont("Segoe UI Symbol, Arial", 24, bold=True)
            n_surf = n_font.render(n['char'], True, n['color'])
            n_surf.set_alpha(int(n['alpha']))
            surface.blit(n_surf, (int(n['x']), int(n['y'])))

        # Hiệu ứng Glitch nếu có
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
        
        # Tự động ngắt dòng nếu câu quá dài
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
        
        # Khung nền bán trong suốt bo góc
        bg_rect = pygame.Rect(30, bar_y, self.width - 60, total_h)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (24, 28, 26, 210), (0, 0, bg_rect.width, bg_rect.height), border_radius=12)
        pygame.draw.rect(bg_surf, (141, 213, 201, 180), (0, 0, bg_rect.width, bg_rect.height), width=2, border_radius=12)
        surface.blit(bg_surf, bg_rect.topleft)

        # Vẽ text
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
        # Khung viền đen nổi khối
        pygame.draw.rect(surface, BMO_DARK_TEAL, (bezel_w, bezel_w, self.width - 2*bezel_w, self.height - 2*bezel_w), 4, border_radius=8)

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
