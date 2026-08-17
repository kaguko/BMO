"""
Game 3: Chiptune Simon Memory
Trò chơi rèn luyện trí nhớ âm nhạc với 4 nút bấm biểu tượng của BMO:
Vàng (D-Pad), Xanh dương (Tam giác), Xanh lá (Tròn), Đỏ (Vuông).
"""
import pygame
import random
import time
from .base_game import BaseGame
from ..constants import (
    BMO_TEAL, BMO_BODY_TEAL, BMO_DARK_TEAL, BMO_BLACK, BMO_WHITE,
    BMO_YELLOW, BMO_BLUE, BMO_GREEN, BMO_HEART_RED
)
from ..audio_synth import synth

class SimonGame(BaseGame):
    def __init__(self):
        super().__init__(title="BMO Simon Memory")
        
        # Cấu hình 4 nút bấm BMO
        self.buttons = [
            {'name': 'YELLOW D-PAD', 'color': BMO_YELLOW, 'bright': (255, 240, 120), 'key': 'W / 1 / UP', 'sound': 'simon_0'},
            {'name': 'BLUE TRIANGLE', 'color': BMO_BLUE, 'bright': (130, 210, 255), 'key': 'D / 2 / RIGHT', 'sound': 'simon_1'},
            {'name': 'GREEN CIRCLE', 'color': BMO_GREEN, 'bright': (100, 230, 150), 'key': 'S / 3 / DOWN', 'sound': 'simon_2'},
            {'name': 'RED SQUARE', 'color': BMO_HEART_RED, 'bright': (255, 140, 140), 'key': 'A / 4 / LEFT', 'sound': 'simon_3'},
        ]
        
        self.sequence = []
        self.player_index = 0
        self.state = "START"  # "START", "PLAYING_SEQ", "PLAYER_TURN", "GAME_OVER", "SUCCESS"
        self.active_button = None
        self.active_timer = 0
        
        # Quản lý phát chuỗi của BMO
        self.seq_index = 0
        self.seq_timer = 0
        self.round_num = 1
        
        self._calculate_button_rects()

    def _calculate_button_rects(self):
        cx, cy = self.width // 2, self.height // 2 + 20
        btn_size = 110
        gap = 20
        
        # 0: Trên (Yellow), 1: Phải (Blue), 2: Dưới (Green), 3: Trái (Red)
        self.btn_rects = [
            pygame.Rect(cx - btn_size // 2, cy - btn_size - gap, btn_size, btn_size),
            pygame.Rect(cx + gap, cy - btn_size // 2, btn_size, btn_size),
            pygame.Rect(cx - btn_size // 2, cy + gap, btn_size, btn_size),
            pygame.Rect(cx - btn_size - gap, cy - btn_size // 2, btn_size, btn_size),
        ]

    def reset(self):
        super().reset()
        self.sequence.clear()
        self.player_index = 0
        self.round_num = 1
        self.state = "PLAYING_SEQ"
        self.seq_index = 0
        self.seq_timer = time.time() + 0.6
        self._add_step_to_sequence()

    def _add_step_to_sequence(self):
        self.sequence.append(random.randint(0, 3))
        self.seq_index = 0
        self.player_index = 0
        self.state = "PLAYING_SEQ"
        self.seq_timer = time.time() + 0.6

    def handle_event(self, event):
        super().handle_event(event)
        if self.is_game_over:
            return

        if self.state == "START":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reset()
            return

        if self.state != "PLAYER_TURN":
            return

        btn_pressed = None

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_1, pygame.K_UP]:
                btn_pressed = 0
            elif event.key in [pygame.K_d, pygame.K_2, pygame.K_RIGHT]:
                btn_pressed = 1
            elif event.key in [pygame.K_s, pygame.K_3, pygame.K_DOWN]:
                btn_pressed = 2
            elif event.key in [pygame.K_a, pygame.K_4, pygame.K_LEFT]:
                btn_pressed = 3
                
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.btn_rects):
                if rect.collidepoint(event.pos):
                    btn_pressed = i
                    break

        if btn_pressed is not None:
            self._handle_player_input(btn_pressed)

    def _handle_player_input(self, btn_idx):
        self.active_button = btn_idx
        self.active_timer = time.time() + 0.25
        synth.play(self.buttons[btn_idx]['sound'])

        # Kiểm tra tính đúng đắn của nốt nhạc
        if btn_idx == self.sequence[self.player_index]:
            self.player_index += 1
            self.score += 25 * self.round_num
            
            # Nếu hoàn thành chuỗi của vòng này
            if self.player_index >= len(self.sequence):
                self.round_num += 1
                self.score += 100
                synth.play('win')
                self.state = "SUCCESS"
                self.seq_timer = time.time() + 0.8
        else:
            # Bấm sai -> Game Over
            self.state = "GAME_OVER"
            self.is_game_over = True
            synth.play('game_over')

    def update(self):
        now = time.time()

        # Tắt hiệu ứng sáng nút bấm sau thời gian ngắn
        if self.active_button is not None and now > self.active_timer:
            self.active_button = None

        if self.state == "PLAYING_SEQ":
            if now >= self.seq_timer:
                if self.seq_index < len(self.sequence):
                    btn_idx = self.sequence[self.seq_index]
                    self.active_button = btn_idx
                    self.active_timer = now + 0.35
                    synth.play(self.buttons[btn_idx]['sound'])
                    self.seq_index += 1
                    self.seq_timer = now + 0.55
                else:
                    # Chuyển lượt cho người chơi
                    self.state = "PLAYER_TURN"
                    self.active_button = None

        elif self.state == "SUCCESS":
            if now >= self.seq_timer:
                self._add_step_to_sequence()

    def draw(self, surface):
        surface.fill(BMO_TEAL)
        
        # 1. Khung máy BMO ở giữa
        cx, cy = self.width // 2, self.height // 2 + 20
        pygame.draw.circle(surface, BMO_DARK_TEAL, (cx, cy), 170)
        pygame.draw.circle(surface, BMO_BODY_TEAL, (cx, cy), 160)

        # 2. Vẽ 4 nút bấm
        for i, rect in enumerate(self.btn_rects):
            b_info = self.buttons[i]
            is_lit = (self.active_button == i)
            draw_color = b_info['bright'] if is_lit else b_info['color']
            
            if i == 0:  # Nút Vàng (D-Pad trên)
                pygame.draw.rect(surface, draw_color, rect, border_radius=14)
                pygame.draw.polygon(surface, BMO_BLACK, [(cx, rect.top + 20), (cx - 15, rect.bottom - 20), (cx + 15, rect.bottom - 20)])
            elif i == 1:  # Nút Xanh Dương (Tam giác phải)
                pygame.draw.rect(surface, draw_color, rect, border_radius=14)
                pygame.draw.polygon(surface, BMO_WHITE, [(rect.right - 25, cy), (rect.left + 25, cy - 20), (rect.left + 25, cy + 20)])
            elif i == 2:  # Nút Xanh Lá (Tròn dưới)
                pygame.draw.rect(surface, draw_color, rect, border_radius=14)
                pygame.draw.circle(surface, BMO_WHITE, (cx, rect.centery), 18)
            elif i == 3:  # Nút Đỏ (Vuông trái)
                pygame.draw.rect(surface, draw_color, rect, border_radius=14)
                pygame.draw.rect(surface, BMO_WHITE, (rect.centerx - 16, rect.centery - 16, 32, 32), border_radius=4)

            # Viền nổi khối
            pygame.draw.rect(surface, BMO_BLACK, rect, width=4, border_radius=14)

        # Vòng tròn tâm
        pygame.draw.circle(surface, BMO_BLACK, (cx, cy), 40)
        round_t = self.font_ui.render(f"R:{self.round_num}", True, BMO_WHITE)
        surface.blit(round_t, round_t.get_rect(center=(cx, cy)))

        # 3. Trạng thái hiển thị lượt
        if self.state == "START":
            msg = "Press [SPACE] to Start Simon Memory!"
            color = BMO_BLACK
        elif self.state == "PLAYING_SEQ":
            msg = f"🎵 BMO is playing note {self.seq_index}/{len(self.sequence)}... Listen!"
            color = BMO_DARK_TEAL
        elif self.state == "PLAYER_TURN":
            msg = f"✨ Your Turn! Repeat the sequence ({self.player_index}/{len(self.sequence)})"
            color = (20, 90, 40)
        else:
            msg = ""

        if msg:
            msg_surf = self.font_ui.render(msg, True, color)
            surface.blit(msg_surf, msg_surf.get_rect(center=(self.width // 2, 80)))

        # 4. Thanh HUD
        self.draw_hud(surface)

        # 5. Game Over
        if self.is_game_over:
            self.draw_game_over_screen(surface)
