"""
BMO Retro OSD Menu System
Menu điều khiển On-Screen Display phong cách GameBoy retro của BMO.
"""
import pygame
from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BMO_TEAL, BMO_BODY_TEAL,
    BMO_DARK_TEAL, BMO_BLACK, BMO_WHITE, BMO_YELLOW,
    BMO_BLUE, BMO_GREEN, BMO_HEART_RED
)
from .audio_synth import synth

MENU_ITEMS = [
    {"id": "face", "title": "🎭 BMO Face & Chat Companion", "desc": "Mặt tương tác, xoa đầu, mắt theo chuột, trò chuyện offline"},
    {"id": "game_runner", "title": "🏃 Game 1: BMO Chop! Adventure Runner", "desc": "Chạy nhảy vượt chướng ngại vật & chém quái vật xứ Ooo"},
    {"id": "game_bugs", "title": "👾 Game 2: BMO Bug Catcher", "desc": "Bắn laser bảo vệ máy tính khỏi đàn bọ điện tử"},
    {"id": "game_simon", "title": "🎵 Game 3: Simon Chiptune Memory", "desc": "Rèn luyện trí nhớ âm nhạc với 4 nút màu BMO"},
    {"id": "game_rainicorn", "title": "🌈 Game 4: Lady Rainicorn Sky Flap", "desc": "Bay lượn đuôi cầu vồng qua vương quốc kẹo ngọt"},
    {"id": "tool_timer", "title": "⏰ Tool: BMO Pomodoro & Timer", "desc": "Đồng hồ bấm giờ học tập / làm việc có báo thức"},
    {"id": "tool_jukebox", "title": "🎹 Tool: Chiptune Synth & Jukebox", "desc": "Đàn piano 8 phím và nghe các bài hát Adventure Time"},
    {"id": "tool_football", "title": "🪞 Tool: Football in the Mirror", "desc": "Đóng kịch tương tác với người bạn trong gương"},
    {"id": "settings", "title": "⚙️ Settings & Controls", "desc": "Bật/tắt âm thanh, scanlines CRT và đổi giọng nói"},
    {"id": "help", "title": "❓ Help & Lore Guide", "desc": "Hướng dẫn chi tiết cách chơi và các câu lệnh bí mật"}
]

class MenuSystem:
    def __init__(self):
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.selected_index = 0
        self.is_open = False
        
        # Phông chữ
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Consolas, Arial", 26, bold=True)
        self.font_item = pygame.font.SysFont("Consolas, Arial", 18, bold=True)
        self.font_desc = pygame.font.SysFont("Consolas, Arial", 14)
        self.font_footer = pygame.font.SysFont("Consolas, Arial", 15)

    def open(self):
        self.is_open = True
        synth.play('chirp')

    def close(self):
        self.is_open = False
        synth.play('bloop')

    def toggle(self):
        if self.is_open:
            self.close()
        else:
            self.open()

    def handle_event(self, event):
        """Xử lý điều khiển menu."""
        if not self.is_open:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.selected_index = (self.selected_index - 1) % len(MENU_ITEMS)
                synth.play('beep')
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.selected_index = (self.selected_index + 1) % len(MENU_ITEMS)
                synth.play('beep')
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                synth.play('coin')
                selected_id = MENU_ITEMS[self.selected_index]["id"]
                self.is_open = False
                return selected_id
            elif event.key == pygame.K_ESCAPE:
                self.close()
                return "close_menu"

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Nhấp chuột chọn mục
            start_y = 90
            item_h = 42
            mx, my = event.pos
            if 60 <= mx <= self.width - 60:
                for i in range(len(MENU_ITEMS)):
                    iy = start_y + i * item_h
                    if iy <= my <= iy + item_h - 6:
                        self.selected_index = i
                        synth.play('coin')
                        selected_id = MENU_ITEMS[i]["id"]
                        self.is_open = False
                        return selected_id

        return None

    def draw(self, surface):
        """Vẽ lớp phủ Menu OSD."""
        if not self.is_open:
            return

        # 1. Nền mờ tối bán trong suốt
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((12, 18, 16, 230))
        surface.blit(overlay, (0, 0))

        # 2. Khung hộp Menu BMO
        box_w = self.width - 100
        box_h = self.height - 70
        bx = 50
        by = 35
        
        pygame.draw.rect(surface, BMO_DARK_TEAL, (bx, by, box_w, box_h), border_radius=14)
        pygame.draw.rect(surface, BMO_BODY_TEAL, (bx + 4, by + 4, box_w - 8, box_h - 8), border_radius=10)
        pygame.draw.rect(surface, (20, 30, 26), (bx + 14, by + 14, box_w - 28, box_h - 28), border_radius=8)

        # 3. Tiêu đề Menu
        title_surf = self.font_title.render("🎮 BMO SYSTEM MENU", True, BMO_YELLOW)
        surface.blit(title_surf, title_surf.get_rect(center=(self.width // 2, by + 35)))

        # 4. Danh sách các mục (Items)
        start_y = by + 65
        item_h = 42
        
        for i, item in enumerate(MENU_ITEMS):
            iy = start_y + i * item_h
            is_selected = (i == self.selected_index)
            
            # Thanh chọn nổi bật
            if is_selected:
                pygame.draw.rect(surface, BMO_YELLOW, (bx + 25, iy, box_w - 50, item_h - 6), border_radius=6)
                t_color = BMO_BLACK
                d_color = (60, 60, 50)
                # Mũi tên con trỏ BMO
                arrow = self.font_item.render("▶", True, BMO_HEART_RED)
                surface.blit(arrow, (bx + 35, iy + 6))
            else:
                t_color = BMO_WHITE
                d_color = (150, 175, 165)

            # Tên mục
            t_surf = self.font_item.render(item["title"], True, t_color)
            surface.blit(t_surf, (bx + 60, iy + 4))
            
            # Mô tả ngắn
            d_surf = self.font_desc.render(item["desc"], True, d_color)
            surface.blit(d_surf, (bx + 60, iy + 22))

        # 5. Thanh hướng dẫn phím dưới đáy
        f_surf = self.font_footer.render("[▲/▼ or W/S]: Navigate  |  [ENTER/SPACE]: Select  |  [ESC]: Back", True, BMO_TEAL)
        surface.blit(f_surf, f_surf.get_rect(center=(self.width // 2, by + box_h - 22)))
