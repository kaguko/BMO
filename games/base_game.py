"""
BMO Mini-Games Base Class
Lớp nền tảng cho tất cả các trò chơi retro bên trong BMO.
"""
import pygame
from ..constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BMO_TEAL, BMO_BLACK,
    BMO_WHITE, BMO_YELLOW, BMO_HEART_RED
)

class BaseGame:
    def __init__(self, title="Mini Game"):
        self.title = title
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.score = 0
        self.high_score = 0
        self.is_game_over = False
        self.is_paused = False
        self.exit_requested = False
        
        # Phông chữ giao diện game
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Consolas, Arial", 28, bold=True)
        self.font_ui = pygame.font.SysFont("Consolas, Arial", 18, bold=True)
        self.font_over = pygame.font.SysFont("Consolas, Arial", 36, bold=True)

    def handle_event(self, event):
        """Xử lý sự kiện bàn phím/chuột. Có thể ghi đè bởi lớp con."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit_requested = True
            elif event.key == pygame.K_r and self.is_game_over:
                self.reset()
            elif event.key == pygame.K_p:
                self.is_paused = not self.is_paused

    def update(self):
        """Cập nhật logic game từng khung hình."""
        pass

    def draw(self, surface):
        """Vẽ khung hình game."""
        pass

    def reset(self):
        """Khởi động lại trò chơi."""
        if self.score > self.high_score:
            self.high_score = self.score
        self.score = 0
        self.is_game_over = False
        self.is_paused = False
        self.exit_requested = False

    def draw_hud(self, surface):
        """Vẽ thanh thông tin điểm số, phím thoát phía trên màn hình."""
        # Thanh nền trên cùng
        pygame.draw.rect(surface, (20, 24, 22), (0, 0, self.width, 36))
        
        # Tiêu đề game
        title_surf = self.font_ui.render(f"🎮 {self.title}", True, BMO_YELLOW)
        surface.blit(title_surf, (14, 8))
        
        # Điểm số
        score_surf = self.font_ui.render(f"SCORE: {self.score:05d}  |  HI: {self.high_score:05d}", True, BMO_WHITE)
        surface.blit(score_surf, (self.width // 2 - 120, 8))
        
        # Hướng dẫn ESC
        esc_surf = self.font_ui.render("ESC: Menu", True, (160, 180, 175))
        surface.blit(esc_surf, (self.width - 110, 8))

    def draw_game_over_screen(self, surface):
        """Vẽ màn hình Game Over phong cách retro."""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 15, 12, 200))
        surface.blit(overlay, (0, 0))
        
        # Chữ Game Over
        t_over = self.font_over.render("GAME OVER", True, BMO_HEART_RED)
        surface.blit(t_over, t_over.get_rect(center=(self.width // 2, self.height // 2 - 50)))
        
        # Điểm đạt được
        t_sc = self.font_ui.render(f"FINAL SCORE: {self.score}", True, BMO_WHITE)
        surface.blit(t_sc, t_sc.get_rect(center=(self.width // 2, self.height // 2)))
        
        # Nút bấm tiếp tục
        t_cont = self.font_ui.render("Press [R] to Play Again  |  [ESC] for Menu", True, BMO_YELLOW)
        surface.blit(t_cont, t_cont.get_rect(center=(self.width // 2, self.height // 2 + 50)))
