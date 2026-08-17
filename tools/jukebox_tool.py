"""
Tool 2: BMO Chiptune Jukebox & Synth Piano
Bàn phím đàn 8-bit tương tác gõ phím máy tính và máy nghe nhạc chiptune Adventure Time.
"""
import pygame
import time
import math
from ..constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BMO_TEAL, BMO_BODY_TEAL,
    BMO_DARK_TEAL, BMO_BLACK, BMO_WHITE, BMO_YELLOW,
    BMO_BLUE, BMO_GREEN, BMO_HEART_RED, BMO_ROSE
)
from ..audio_synth import synth

# Bảng nốt nhạc Piano 8 phím cơ bản (Octave 4 - 5)
PIANO_KEYS = [
    {'note': 'C4 (Đồ)', 'key_char': 'A / 1', 'key_codes': [pygame.K_a, pygame.K_1], 'freq': 261.63, 'color': (255, 100, 100)},
    {'note': 'D4 (Rê)', 'key_char': 'S / 2', 'key_codes': [pygame.K_s, pygame.K_2], 'freq': 293.66, 'color': (255, 180, 80)},
    {'note': 'E4 (Mi)', 'key_char': 'D / 3', 'key_codes': [pygame.K_d, pygame.K_3], 'freq': 329.63, 'color': (255, 240, 90)},
    {'note': 'F4 (Fa)', 'key_char': 'F / 4', 'key_codes': [pygame.K_f, pygame.K_4], 'freq': 349.23, 'color': (100, 230, 140)},
    {'note': 'G4 (Sol)', 'key_char': 'G / 5', 'key_codes': [pygame.K_g, pygame.K_5], 'freq': 392.00, 'color': (90, 200, 255)},
    {'note': 'A4 (La)', 'key_char': 'H / 6', 'key_codes': [pygame.K_h, pygame.K_6], 'freq': 440.00, 'color': (140, 140, 255)},
    {'note': 'B4 (Si)', 'key_char': 'J / 7', 'key_codes': [pygame.K_j, pygame.K_7], 'freq': 493.88, 'color': (210, 120, 240)},
    {'note': 'C5 (Đố)', 'key_char': 'K / 8', 'key_codes': [pygame.K_k, pygame.K_8], 'freq': 523.25, 'color': (255, 120, 190)},
]

class JukeboxTool:
    def __init__(self):
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.wave_type = 'square'  # 'square', 'triangle', 'sawtooth', 'sine'
        self.active_keys = {}      # key_index -> release_time
        self.now_playing = "None"
        self.exit_requested = False
        
        # BMO Dance animation
        self.dance_frame = 0
        
        # Phông chữ
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Consolas, Arial", 26, bold=True)
        self.font_note = pygame.font.SysFont("Consolas, monospace", 16, bold=True)
        self.font_ui = pygame.font.SysFont("Consolas, Arial", 18, bold=True)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                synth.stop_music()
                self.exit_requested = True
                
            # Đổi dạng sóng âm thanh (W)
            elif event.key == pygame.K_w:
                waves = ['square', 'triangle', 'sawtooth', 'sine']
                curr_idx = waves.index(self.wave_type)
                self.wave_type = waves[(curr_idx + 1) % len(waves)]
                synth.play('chirp')

            # Phát bài hát mẫu (F1, F2, F3)
            elif event.key == pygame.K_F1 or event.key == pygame.K_z:
                self.now_playing = "Adventure Time Main Theme"
                synth.play_adventure_theme()
            elif event.key == pygame.K_F2 or event.key == pygame.K_x:
                self.now_playing = "Time Is An Illusion (BMO Song)"
                synth.play_bmo_song()
            elif event.key == pygame.K_SPACE:
                synth.stop_music()
                self.now_playing = "None"
                synth.play('bloop')

            # Phím đàn Piano
            for i, p_key in enumerate(PIANO_KEYS):
                if event.key in p_key['key_codes']:
                    self._play_piano_key(i)
                    
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if my < 45 and mx > self.width - 100:
                synth.stop_music()
                self.exit_requested = True
                return
            elif 180 <= my <= 230:
                # Nhấp vào tên bài hát -> Đổi phát bài hát mẫu
                if self.now_playing == "None":
                    self.now_playing = "Adventure Time Theme"
                    synth.play_adventure_theme()
                elif self.now_playing == "Adventure Time Theme":
                    self.now_playing = "Time Is An Illusion"
                    synth.play_bmo_song()
                else:
                    self.now_playing = "None"
                    synth.stop_music()
                return
            elif my < 90 and mx < 200:
                # Đổi dạng sóng
                waves = ['square', 'triangle', 'sawtooth', 'sine']
                curr_idx = waves.index(self.wave_type)
                self.wave_type = waves[(curr_idx + 1) % len(waves)]
                synth.play('chirp')
                return

            # Nhấp chuột vào phím đàn
            key_w = (self.width - 80) // len(PIANO_KEYS)
            start_x = 40
            py = self.height - 240
            for i in range(len(PIANO_KEYS)):
                rect = pygame.Rect(start_x + i * key_w, py, key_w - 6, 170)
                if rect.collidepoint(event.pos):
                    self._play_piano_key(i)
                    break

    def _play_piano_key(self, index):
        synth.play_note(PIANO_KEYS[index]['freq'], duration=0.35, wave_type=self.wave_type)
        self.active_keys[index] = time.time() + 0.25

    def update(self):
        self.dance_frame += 1
        now = time.time()
        for idx in list(self.active_keys.keys()):
            if now > self.active_keys[idx]:
                del self.active_keys[idx]

    def draw(self, surface):
        surface.fill(BMO_TEAL)
        
        # 1. Tiêu đề
        t_surf = self.font_title.render("🎹 BMO Chiptune Synthesizer & Jukebox", True, BMO_BLACK)
        surface.blit(t_surf, t_surf.get_rect(center=(self.width // 2, 40)))

        # 2. Vũ điệu BMO đang nhảy múa theo nhạc
        cx = self.width // 2
        cy = 135
        dance_offset_x = int(12 * math.sin(self.dance_frame * 0.15))
        dance_offset_y = int(6 * math.cos(self.dance_frame * 0.3))
        
        # Thân máy BMO nhảy
        bx, by = cx + dance_offset_x - 30, cy + dance_offset_y
        pygame.draw.rect(surface, BMO_BODY_TEAL, (bx, by, 60, 50), border_radius=6)
        pygame.draw.rect(surface, (230, 250, 245), (bx + 6, by + 6, 48, 22), border_radius=3)
        # Mắt cười
        pygame.draw.arc(surface, BMO_BLACK, (bx + 12, by + 10, 12, 10), math.pi, 2*math.pi, 2)
        pygame.draw.arc(surface, BMO_BLACK, (bx + 36, by + 10, 12, 10), math.pi, 2*math.pi, 2)
        pygame.draw.circle(surface, BMO_ROSE, (bx + 8, by + 20), 4)
        pygame.draw.circle(surface, BMO_ROSE, (bx + 52, by + 20), 4)
        # Tay BMO giơ lên nhảy
        pygame.draw.line(surface, BMO_BLACK, (bx - 2, by + 25), (bx - 12, by + 10 + dance_offset_y), 3)
        pygame.draw.line(surface, BMO_BLACK, (bx + 62, by + 25), (bx + 72, by + 10 - dance_offset_y), 3)

        # 3. Thông tin bài hát đang phát
        now_str = f"🎵 Track: {self.now_playing}  |  Wave: [{self.wave_type.upper()}]"
        track_surf = self.font_ui.render(now_str, True, BMO_DARK_TEAL)
        surface.blit(track_surf, track_surf.get_rect(center=(self.width // 2, 215)))

        # 4. Vẽ bàn phím Piano (8 phím lớn)
        key_w = (self.width - 80) // len(PIANO_KEYS)
        start_x = 40
        key_y = self.height - 230
        key_h = 160

        for i, p_key in enumerate(PIANO_KEYS):
            kx = start_x + i * key_w
            is_pressed = (i in self.active_keys)
            
            # Màu phím
            key_color = p_key['color'] if is_pressed else BMO_WHITE
            offset_y = 6 if is_pressed else 0
            
            # Thân phím
            pygame.draw.rect(surface, key_color, (kx, key_y + offset_y, key_w - 6, key_h), border_radius=8)
            pygame.draw.rect(surface, BMO_BLACK, (kx, key_y + offset_y, key_w - 6, key_h), width=3, border_radius=8)
            
            # Vạch màu ở đuôi phím
            pygame.draw.rect(surface, p_key['color'], (kx + 4, key_y + key_h - 26 + offset_y, key_w - 14, 18), border_radius=4)

            # Tên nốt & phím bấm
            n_surf = self.font_note.render(p_key['note'], True, BMO_BLACK)
            k_surf = self.font_ui.render(p_key['key_char'], True, BMO_BLACK)
            
            surface.blit(k_surf, k_surf.get_rect(center=(kx + (key_w - 6)//2, key_y + 35 + offset_y)))
            surface.blit(n_surf, n_surf.get_rect(center=(kx + (key_w - 6)//2, key_y + 80 + offset_y)))

        # 5. Hướng dẫn phím nóng
        guide_str = "[A-K or 1-8]: Play Notes  |  [Z/X]: Jukebox Tracks  |  [W]: Change Synth Wave  |  [ESC]: Menu"
        g_surf = self.font_ui.render(guide_str, True, (40, 70, 60))
        surface.blit(g_surf, g_surf.get_rect(center=(self.width // 2, self.height - 35)))
