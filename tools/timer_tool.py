"""
Tool 1: BMO Pomodoro & Countdown Timer
Đồng hồ bấm giờ tập trung / học tập với báo thức BMO, âm thanh và lời chúc đáng yêu.
"""
import pygame
import time
import math
from ..constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BMO_TEAL, BMO_BODY_TEAL,
    BMO_DARK_TEAL, BMO_BLACK, BMO_WHITE, BMO_YELLOW,
    BMO_BLUE, BMO_GREEN, BMO_HEART_RED
)
from ..audio_synth import synth
from ..tts_manager import tts

class TimerTool:
    def __init__(self):
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        
        # Cấu hình thời gian (mặc định 25 phút Pomodoro)
        self.total_seconds = 25 * 60
        self.remaining_seconds = self.total_seconds
        self.is_running = False
        self.last_tick = 0
        self.is_alarm_ringing = False
        self.alarm_flash_timer = 0
        self.exit_requested = False
        
        # Phông chữ
        pygame.font.init()
        self.font_time = pygame.font.SysFont("Consolas, monospace", 64, bold=True)
        self.font_title = pygame.font.SysFont("Consolas, Arial", 26, bold=True)
        self.font_ui = pygame.font.SysFont("Consolas, Arial", 18, bold=True)

    def reset(self, minutes=25):
        self.total_seconds = minutes * 60
        self.remaining_seconds = self.total_seconds
        self.is_running = False
        self.is_alarm_ringing = False
        self.exit_requested = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit_requested = True
            elif event.key == pygame.K_SPACE:
                # Tắt chuông nếu đang kêu hoặc Bật/Dừng đếm giờ
                if self.is_alarm_ringing:
                    self.is_alarm_ringing = False
                else:
                    self.is_running = not self.is_running
                    self.last_tick = time.time()
                    synth.play('bloop')
            elif event.key == pygame.K_r:
                self.reset(int(self.total_seconds / 60))
                synth.play('chirp')
            elif event.key in [pygame.K_UP, pygame.K_w]:
                if not self.is_running:
                    self.total_seconds = min(120 * 60, self.total_seconds + 5 * 60)
                    self.remaining_seconds = self.total_seconds
                    synth.play('bloop')
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                if not self.is_running:
                    self.total_seconds = max(1 * 60, self.total_seconds - 5 * 60)
                    self.remaining_seconds = self.total_seconds
                    synth.play('bloop')
            # Phím tắt chọn nhanh 5m, 15m, 25m, 45m
            elif event.key == pygame.K_1:
                self.reset(5)
            elif event.key == pygame.K_2:
                self.reset(15)
            elif event.key == pygame.K_3:
                self.reset(25)
            elif event.key == pygame.K_4:
                self.reset(45)

    def update(self):
        now = time.time()
        
        if self.is_running and self.remaining_seconds > 0:
            if now - self.last_tick >= 1.0:
                self.remaining_seconds -= 1
                self.last_tick = now
                # Tiếng tích tắc nhỏ
                if self.remaining_seconds % 60 == 0:
                    synth.play('beep')
                    
                if self.remaining_seconds <= 0:
                    self.is_running = False
                    self.is_alarm_ringing = True
                    synth.play('alarm')
                    tts.speak("BMO Alert! Time's up! Great job focusing my wonderful friend! Yay BMO!")

        if self.is_alarm_ringing:
            self.alarm_flash_timer += 1
            if self.alarm_flash_timer % 30 == 0:
                synth.play('alarm')

    def draw(self, surface):
        # Đổi màu nền nhấp nháy nếu chuông báo đang reo
        if self.is_alarm_ringing and (self.alarm_flash_timer // 15) % 2 == 0:
            surface.fill((255, 180, 180))
        else:
            surface.fill(BMO_TEAL)

        # 1. Vẽ vòng đồng hồ trung tâm
        cx, cy = self.width // 2, self.height // 2 - 20
        radius = 140
        pygame.draw.circle(surface, BMO_DARK_TEAL, (cx, cy), radius + 8)
        pygame.draw.circle(surface, (230, 248, 244), (cx, cy), radius)

        # Vẽ cung tròn tiến độ (Progress Ring)
        if self.total_seconds > 0:
            progress = self.remaining_seconds / self.total_seconds
            angle = progress * 2 * math.pi
            # Kim đồng hồ
            hand_x = cx + int((radius - 20) * math.sin(angle))
            hand_y = cy - int((radius - 20) * math.cos(angle))
            pygame.draw.line(surface, BMO_HEART_RED if self.is_running else BMO_DARK_TEAL, (cx, cy), (hand_x, hand_y), 6)
            pygame.draw.circle(surface, BMO_BLACK, (cx, cy), 10)

        # 2. Hiển thị chữ số đồng hồ đếm ngược
        mins = int(self.remaining_seconds // 60)
        secs = int(self.remaining_seconds % 60)
        time_str = f"{mins:02d}:{secs:02d}"
        
        t_surf = self.font_time.render(time_str, True, BMO_BLACK)
        t_rect = t_surf.get_rect(center=(cx, cy + 50))
        surface.blit(t_surf, t_rect)

        # 3. Trạng thái (RUNNING / PAUSED / FINISHED)
        if self.is_alarm_ringing:
            status_str = "⏰ TIME'S UP! BMO SAYS YAY!"
            status_col = BMO_HEART_RED
        elif self.is_running:
            status_str = "⏱️ FOCUSING... (BMO is cheering you on!)"
            status_col = (20, 100, 50)
        else:
            status_str = "⏸️ PAUSED (Press SPACE to Start)"
            status_col = (80, 80, 80)

        st_surf = self.font_title.render(status_str, True, status_col)
        surface.blit(st_surf, st_surf.get_rect(center=(self.width // 2, cy - 90)))

        # 4. Các nút chỉnh nhanh thời gian (5m, 15m, 25m, 45m)
        presets = [("1: 5m", 5), ("2: 15m", 15), ("3: 25m", 25), ("4: 45m", 45)]
        for i, (label, m) in enumerate(presets):
            px = self.width // 2 - 180 + i * 120
            py = self.height - 130
            is_active = (self.total_seconds == m * 60 and not self.is_running)
            pygame.draw.rect(surface, BMO_YELLOW if is_active else BMO_BODY_TEAL, (px - 45, py, 90, 34), border_radius=6)
            pygame.draw.rect(surface, BMO_BLACK, (px - 45, py, 90, 34), width=2, border_radius=6)
            
            p_surf = self.font_ui.render(label, True, BMO_BLACK if is_active else BMO_WHITE)
            surface.blit(p_surf, p_surf.get_rect(center=(px, py + 17)))

        # 5. Hướng dẫn sử dụng
        help_str = "[SPACE]: Start/Pause  |  [UP/DOWN]: +/- 5m  |  [R]: Reset  |  [ESC]: Menu"
        h_surf = self.font_ui.render(help_str, True, (40, 70, 60))
        surface.blit(h_surf, h_surf.get_rect(center=(self.width // 2, self.height - 40)))
