"""
Tool 3: Football in the Mirror Mode (Enhanced)
Chế độ tương tác với Football - người bạn tri kỷ sống trong gương của BMO.
Tự động đối thoại hoán đổi liên tục giữa BMO và Football với chất giọng khác nhau.
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
    },
    {
        'title': "Scene 4: The Secret Dance in Treehouse",
        'dialogues': [
            ("BMO", "Finn and Jake are outside slaying vampires! It's time for our secret dance!", "win"),
            ("FOOTBALL", "Yay! Look at my mirror spins! Whoosh whoosh!", "chirp"),
            ("BMO", "Haha! Ronnie the Sock is cheering for us from the sofa!", "coin"),
            ("FOOTBALL", "We are the best dancing robot boys in all of Ooo!", "win")
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
        self.auto_advance_timer = time.time() + 4.5
        
        # Phông chữ Segoe UI / Arial
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Segoe UI, Arial", 22, bold=True)
        self.font_speaker = pygame.font.SysFont("Segoe UI, Arial", 19, bold=True)
        self.font_text = pygame.font.SysFont("Segoe UI, Arial", 17)
        self.font_ui = pygame.font.SysFont("Segoe UI, Arial", 14)
        
        self._trigger_current_line()

    def reset_to_first(self):
        """Khởi động lại từ đầu khi tự động mở từ Idle."""
        self.exit_requested = False
        self.story_idx = 0
        self.line_idx = 0
        self.auto_advance_timer = time.time() + 4.5
        self._trigger_current_line()

    def _trigger_current_line(self):
        story = FOOTBALL_STORIES[self.story_idx]
        speaker, line, snd = story['dialogues'][self.line_idx]
        synth.play(snd)
        
        # BMO: Giọng robot cao chuẩn (1.28x), FOOTBALL: Giọng thì thầm trong gương cao hơn (1.44x)
        pitch = 1.28 if speaker == "BMO" else 1.44
        tts.speak(f"{speaker}: {line}", clear_queue=True, pitch_override=pitch)
        self.auto_advance_timer = time.time() + max(4.0, len(line) * 0.09)

    def next_dialogue(self):
        story = FOOTBALL_STORIES[self.story_idx]
        if self.line_idx < len(story['dialogues']) - 1:
            self.line_idx += 1
        else:
            self.story_idx = (self.story_idx + 1) % len(FOOTBALL_STORIES)
            self.line_idx = 0
        self._trigger_current_line()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                self.exit_requested = True
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.next_dialogue()
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                idx = event.key - pygame.K_1
                if idx < len(FOOTBALL_STORIES):
                    self.story_idx = idx
                    self.line_idx = 0
                    self._trigger_current_line()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.next_dialogue()

    def update(self):
        self.anim_tick += 1
        # Tự động nhảy dòng thoại khi hết câu đọc
        if time.time() >= self.auto_advance_timer and not tts.is_talking:
            self.next_dialogue()

    def draw(self, surface):
        surface.fill((120, 195, 185))  # Nền phòng tắm nhà trên cây
        
        story = FOOTBALL_STORIES[self.story_idx]
        speaker, line, _ = story['dialogues'][self.line_idx]
        
        # 1. Vẽ khung phân chia Gương (Mirror Split Screen)
        split_x = self.width // 2
        # Nửa bên phải: Thế giới trong gương
        pygame.draw.rect(surface, (150, 225, 215), (split_x, 0, split_x, self.height))
        # Khung viền gương vàng gỗ ở giữa
        pygame.draw.rect(surface, (190, 145, 60), (split_x - 8, 0, 16, self.height - 145))
        pygame.draw.rect(surface, (130, 95, 40), (split_x - 4, 0, 8, self.height - 145))
        
        # Hiệu ứng ánh sáng gương lấp lánh bên phải
        glimmer_y = (self.anim_tick * 2) % (self.height - 150)
        pygame.draw.line(surface, (255, 255, 255, 100), (split_x + 20, glimmer_y), (self.width - 20, glimmer_y + 40), 2)

        # 2. Vẽ BMO (Bên trái - Thế giới thực)
        bmo_cx = split_x // 2
        bmo_cy = 180
        is_bmo_talking = (speaker == "BMO" and tts.is_talking)
        self._draw_character(surface, bmo_cx, bmo_cy, "BMO (Real World)", is_bmo_talking, is_mirror=False)

        # 3. Vẽ FOOTBALL (Bên phải - Trong gương)
        foot_cx = split_x + split_x // 2
        foot_cy = 180
        is_foot_talking = (speaker == "FOOTBALL" and tts.is_talking)
        self._draw_character(surface, foot_cx, foot_cy, "FOOTBALL (In The Mirror)", is_foot_talking, is_mirror=True)

        # 4. Tiêu đề cảnh diễn
        t_surf = self.font_title.render(f"🪞 {story['title']}", True, BMO_BLACK)
        surface.blit(t_surf, t_surf.get_rect(center=(self.width // 2, 35)))

        # 5. Hộp thoại dưới đáy
        box_y = self.height - 145
        box_h = 130
        pygame.draw.rect(surface, (20, 26, 24), (20, box_y, self.width - 40, box_h), border_radius=12)
        spk_border = BMO_YELLOW if speaker == "BMO" else (100, 200, 255)
        pygame.draw.rect(surface, spk_border, (20, box_y, self.width - 40, box_h), width=3, border_radius=12)

        # Tên người nói
        spk_color = BMO_YELLOW if speaker == "BMO" else (100, 200, 255)
        spk_tag = "🤖 [BMO]" if speaker == "BMO" else "🪞 [FOOTBALL IN MIRROR]"
        spk_surf = self.font_speaker.render(f"{spk_tag}:", True, spk_color)
        surface.blit(spk_surf, (40, box_y + 12))

        # Nội dung thoại (Tự động ngắt dòng nếu dài)
        words = line.split(' ')
        lines = []
        curr_line = ""
        for w in words:
            test = curr_line + (" " if curr_line else "") + w
            if self.font_text.size(test)[0] < self.width - 90:
                curr_line = test
            else:
                lines.append(curr_line)
                curr_line = w
        if curr_line:
            lines.append(curr_line)

        for i, l_text in enumerate(lines):
            txt_surf = self.font_text.render(l_text, True, BMO_WHITE)
            surface.blit(txt_surf, (40, box_y + 40 + i * 24))

        # Hướng dẫn bấm nút
        h_surf = self.font_ui.render("[SPACE/Click]: Next Line  |  [1 - 4]: Scene  |  [ESC]: Return to BMO Face", True, (160, 180, 175))
        surface.blit(h_surf, (40, box_y + box_h - 24))

    def _draw_character(self, surface, cx, cy, label, is_talking, is_mirror=False):
        """Vẽ hình dáng BMO hoặc Football."""
        body_w, body_h = 110, 100
        bx = cx - body_w // 2
        by = cy - body_h // 2
        
        body_col = BMO_BODY_TEAL if not is_mirror else (80, 185, 170)
        screen_col = BMO_TEAL if not is_mirror else (160, 235, 225)
        
        # Nhún nhảy nhẹ khi đang nói
        bounce = int(3 * math.sin(self.anim_tick * 0.3)) if is_talking else 0
        by += bounce
        
        pygame.draw.rect(surface, body_col, (bx, by, body_w, body_h), border_radius=10)
        pygame.draw.rect(surface, BMO_BLACK, (bx, by, body_w, body_h), width=3, border_radius=10)
        
        # Màn hình mặt
        pygame.draw.rect(surface, screen_col, (bx + 10, by + 10, body_w - 20, 56), border_radius=6)
        
        # Mắt
        eye_y = by + 30
        eye_l_x = bx + 30
        eye_r_x = bx + body_w - 30
        
        if is_talking:
            # Mắt nháy vui
            pygame.draw.arc(surface, BMO_BLACK, (eye_l_x - 10, eye_y - 8, 20, 16), math.pi, 2*math.pi, 3)
            pygame.draw.arc(surface, BMO_BLACK, (eye_r_x - 10, eye_y - 8, 20, 16), math.pi, 2*math.pi, 3)
            # Miệng nói
            m_frame = (self.anim_tick // 6) % 3
            if m_frame == 0:
                pygame.draw.rect(surface, BMO_BLACK, (cx - 12, by + 46, 24, 8), border_radius=2)
            elif m_frame == 1:
                pygame.draw.circle(surface, BMO_BLACK, (cx, by + 50), 9)
                pygame.draw.circle(surface, BMO_ROSE, (cx, by + 52), 5)
            else:
                pygame.draw.rect(surface, BMO_BLACK, (cx - 10, by + 45, 20, 14), border_radius=3)
        else:
            pygame.draw.circle(surface, BMO_BLACK, (eye_l_x, eye_y), 7)
            pygame.draw.circle(surface, BMO_BLACK, (eye_r_x, eye_y), 7)
            pygame.draw.circle(surface, BMO_WHITE, (eye_l_x - 2, eye_y - 2), 2)
            pygame.draw.circle(surface, BMO_WHITE, (eye_r_x - 2, eye_y - 2), 2)
            # Miệng cười nhẹ
            pygame.draw.line(surface, BMO_BLACK, (cx - 10, by + 50), (cx + 10, by + 50), 3)

        # Má hồng
        pygame.draw.circle(surface, BMO_ROSE, (bx + 20, by + 48), 6)
        pygame.draw.circle(surface, BMO_ROSE, (bx + body_w - 20, by + 48), 6)

        # Nút bấm BMO dưới thân
        pygame.draw.rect(surface, BMO_YELLOW, (bx + 16, by + 74, 14, 14), border_radius=2)
        pygame.draw.circle(surface, BMO_BLUE, (bx + 54, by + 81), 5)
        pygame.draw.circle(surface, BMO_GREEN, (bx + 76, by + 81), 5)
        pygame.draw.rect(surface, BMO_HEART_RED, (bx + 90, by + 77, 9, 9), border_radius=2)

        # Nhãn tên
        lbl_surf = self.font_speaker.render(label, True, BMO_BLACK)
        surface.blit(lbl_surf, lbl_surf.get_rect(center=(cx, by + body_h + 20)))
