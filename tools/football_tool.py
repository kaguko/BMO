"""
Tool 3: Football in the Mirror Mode
Chế độ đóng kịch tương tác với Football - người bạn tri kỷ sống trong gương của BMO.
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
from ..tts_manager import tts

FOOTBALL_STORIES = [
    {
        'title': "Scene 1: Morning Secret Tea Party",
        'dialogues': [
            ("BMO", "Good morning Football! Did you sleep well inside the shiny mirror?", "chirp"),
            ("FOOTBALL", "Good morning BMO! I dreamed that I was outside eating pancakes with you!", "bloop"),
            ("BMO", "Here is an invisible cup of Earl Grey tea for you, Football! Sip sip sip!", "coin"),
            ("FOOTBALL", "Delicious! Thank you BMO, you are my very best friend in the whole universe!", "win")
        ]
    },
    {
        'title': "Scene 2: Football Learns BMO Chop",
        'dialogues': [
            ("BMO", "Football! Today I will teach you the ultimate martial art: BMO CHOP!", "chop"),
            ("FOOTBALL", "Gasp! Is it dangerous, BMO? Will I break the mirror glass?", "bloop"),
            ("BMO", "Hi-yaaa! BMO CHOP! If this were a real attack, the bad guys would be kaput!", "chop"),
            ("FOOTBALL", "Whoa! You are so strong and heroic, BMO! Hi-yaaa!", "win")
        ]
    },
    {
        'title': "Scene 3: Are We Real Living Boys?",
        'dialogues': [
            ("BMO", "Football, do you ever wonder if we are real living little boys?", "bloop"),
            ("FOOTBALL", "Of course we are, BMO! We have big hearts and we love Finn and Jake!", "chirp"),
            ("BMO", "Yes! Moe made BMO to BE MORE! And that means more hugs and video games!", "win"),
            ("FOOTBALL", "Yay BMO! Let's play together forever and ever!", "win")
        ]
    }
]

class FootballTool:
    def __init__(self):
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.story_idx = 0
        self.line_idx = 0
        self.exit_requested = False
        self.anim_tick = 0
        
        # Phông chữ
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Consolas, Arial", 24, bold=True)
        self.font_speaker = pygame.font.SysFont("Consolas, Arial", 20, bold=True)
        self.font_text = pygame.font.SysFont("Consolas, Arial", 18)
        self.font_ui = pygame.font.SysFont("Consolas, Arial", 16)
        
        self._trigger_current_line()

    def _trigger_current_line(self):
        story = FOOTBALL_STORIES[self.story_idx]
        speaker, line, snd = story['dialogues'][self.line_idx]
        synth.play(snd)
        tts.speak(f"{speaker}: {line}")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit_requested = True
            elif event.key == pygame.K_SPACE:
                story = FOOTBALL_STORIES[self.story_idx]
                if self.line_idx < len(story['dialogues']) - 1:
                    self.line_idx += 1
                else:
                    # Chuyển sang câu chuyện kế tiếp
                    self.story_idx = (self.story_idx + 1) % len(FOOTBALL_STORIES)
                    self.line_idx = 0
                self._trigger_current_line()
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                idx = event.key - pygame.K_1
                if idx < len(FOOTBALL_STORIES):
                    self.story_idx = idx
                    self.line_idx = 0
                    self._trigger_current_line()

    def update(self):
        self.anim_tick += 1

    def draw(self, surface):
        surface.fill((120, 195, 185))  # Nền phòng tắm nhà trên cây
        
        story = FOOTBALL_STORIES[self.story_idx]
        speaker, line, _ = story['dialogues'][self.line_idx]
        
        # 1. Vẽ khung phân chia Gương (Mirror Split Screen)
        split_x = self.width // 2
        # Nửa bên phải: Thế giới trong gương (Hơi sáng hơn với ánh gương phản chiếu)
        pygame.draw.rect(surface, (150, 225, 215), (split_x, 0, split_x, self.height))
        # Khung viền gương vàng gỗ ở giữa
        pygame.draw.rect(surface, (190, 145, 60), (split_x - 8, 0, 16, self.height - 130))
        pygame.draw.rect(surface, (130, 95, 40), (split_x - 4, 0, 8, self.height - 130))

        # 2. Vẽ BMO (Bên trái - Thế giới thực)
        bmo_cx = split_x // 2
        bmo_cy = 180
        is_bmo_talking = (speaker == "BMO")
        self._draw_character(surface, bmo_cx, bmo_cy, "BMO (Real World)", is_bmo_talking, is_mirror=False)

        # 3. Vẽ FOOTBALL (Bên phải - Trong gương)
        foot_cx = split_x + split_x // 2
        foot_cy = 180
        is_foot_talking = (speaker == "FOOTBALL")
        self._draw_character(surface, foot_cx, foot_cy, "FOOTBALL (In The Mirror)", is_foot_talking, is_mirror=True)

        # 4. Tiêu đề cảnh diễn
        t_surf = self.font_title.render(f"🪞 {story['title']}", True, BMO_BLACK)
        surface.blit(t_surf, t_surf.get_rect(center=(self.width // 2, 35)))

        # 5. Hộp thoại dưới đáy
        box_y = self.height - 140
        pygame.draw.rect(surface, (20, 26, 24), (20, box_y, self.width - 40, 120), border_radius=10)
        pygame.draw.rect(surface, BMO_YELLOW if speaker == "BMO" else BMO_BLUE, (20, box_y, self.width - 40, 120), width=3, border_radius=10)

        # Tên người nói
        spk_color = BMO_YELLOW if speaker == "BMO" else BMO_BLUE
        spk_surf = self.font_speaker.render(f"▶ {speaker}:", True, spk_color)
        surface.blit(spk_surf, (40, box_y + 14))

        # Nội dung thoại
        txt_surf = self.font_text.render(line, True, BMO_WHITE)
        surface.blit(txt_surf, (40, box_y + 45))

        # Hướng dẫn bấm nút
        h_surf = self.font_ui.render("[SPACE]: Next Line   |   [1 - 3]: Choose Story Scene   |   [ESC]: Menu", True, (160, 180, 175))
        surface.blit(h_surf, (40, box_y + 88))

    def _draw_character(self, surface, cx, cy, label, is_talking, is_mirror=False):
        """Vẽ hình dáng BMO hoặc Football."""
        # Thân máy
        body_w, body_h = 100, 90
        bx = cx - body_w // 2
        by = cy - body_h // 2
        
        body_col = BMO_BODY_TEAL if not is_mirror else (80, 185, 170)
        screen_col = BMO_TEAL if not is_mirror else (160, 235, 225)
        
        pygame.draw.rect(surface, body_col, (bx, by, body_w, body_h), border_radius=10)
        pygame.draw.rect(surface, BMO_BLACK, (bx, by, body_w, body_h), width=3, border_radius=10)
        
        # Màn hình mặt
        pygame.draw.rect(surface, screen_col, (bx + 10, by + 10, body_w - 20, 50), border_radius=6)
        
        # Mắt
        eye_y = by + 28
        eye_l_x = bx + 28
        eye_r_x = bx + body_w - 28
        
        if is_talking:
            # Mắt nháy vui
            pygame.draw.arc(surface, BMO_BLACK, (eye_l_x - 10, eye_y - 8, 20, 16), math.pi, 2*math.pi, 3)
            pygame.draw.arc(surface, BMO_BLACK, (eye_r_x - 10, eye_y - 8, 20, 16), math.pi, 2*math.pi, 3)
            # Miệng nói
            m_frame = (self.anim_tick // 8) % 3
            if m_frame == 0:
                pygame.draw.rect(surface, BMO_BLACK, (cx - 10, by + 42, 20, 8), border_radius=2)
            else:
                pygame.draw.circle(surface, BMO_BLACK, (cx, by + 45), 8)
        else:
            pygame.draw.circle(surface, BMO_BLACK, (eye_l_x, eye_y), 6)
            pygame.draw.circle(surface, BMO_BLACK, (eye_r_x, eye_y), 6)
            pygame.draw.circle(surface, BMO_WHITE, (eye_l_x - 2, eye_y - 2), 2)
            pygame.draw.circle(surface, BMO_WHITE, (eye_r_x - 2, eye_y - 2), 2)
            # Miệng cười nhẹ
            pygame.draw.line(surface, BMO_BLACK, (cx - 8, by + 46), (cx + 8, by + 46), 2)

        # Má hồng
        pygame.draw.circle(surface, BMO_ROSE, (bx + 18, by + 42), 5)
        pygame.draw.circle(surface, BMO_ROSE, (bx + body_w - 18, by + 42), 5)

        # Nút bấm BMO dưới thân
        pygame.draw.rect(surface, BMO_YELLOW, (bx + 14, by + 68, 12, 12), border_radius=2)
        pygame.draw.circle(surface, BMO_BLUE, (bx + 48, by + 74), 4)
        pygame.draw.circle(surface, BMO_GREEN, (bx + 68, by + 74), 4)
        pygame.draw.rect(surface, BMO_HEART_RED, (bx + 82, by + 70, 8, 8), border_radius=2)

        # Nhãn tên
        lbl_surf = self.font_speaker.render(label, True, BMO_BLACK)
        surface.blit(lbl_surf, lbl_surf.get_rect(center=(cx, by + body_h + 20)))
