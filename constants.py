"""
BMO Constants and Theme Configuration
Màu sắc, kích thước, phông chữ và các hằng số dùng chung cho BMO.
"""
import pygame

# Kích thước cửa sổ
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Bảng màu BMO chuẩn hoạt hình Adventure Time
BMO_TEAL = (141, 213, 201)        # #8DD5C9 - Màu nền màn hình BMO
BMO_BODY_TEAL = (70, 168, 155)    # #46A89B - Màu vỏ ngoài máy BMO
BMO_DARK_TEAL = (48, 92, 85)      # #305C55 - Viền/bóng thân máy
BMO_BLACK = (24, 28, 26)          # #181C1A - Mắt, miệng, nét vẽ
BMO_WHITE = (245, 250, 248)       # Trắng ngà điểm sáng mắt/giao diện
BMO_ROSE = (240, 128, 144)        # Má hồng khi vui/ngại ngùng
BMO_HEART_RED = (235, 87, 87)     # Mắt trái tim / nút đỏ
BMO_YELLOW = (245, 208, 51)       # Nút D-Pad vàng
BMO_BLUE = (63, 169, 245)         # Nút tam giác xanh dương
BMO_GREEN = (39, 174, 96)         # Nút tròn xanh lá
BMO_CRT_OVERLAY = (20, 40, 35)    # Màu vân quét CRT Scanline
BMO_GOLD = (255, 215, 0)          # Vàng kim điểm thưởng
BMO_TEAR_BLUE = (92, 179, 240)    # Nước mắt BMO

# Các trạng thái biểu cảm của BMO
class Expression:
    IDLE = "idle"
    TALKING = "talking"
    HAPPY = "happy"
    LAUGH = "laugh"
    EXCITED = "excited"
    SAD = "sad"
    CRYING = "crying"
    ANGRY_CHOP = "angry_chop"
    SLEEPY = "sleepy"
    SLEEPING = "sleeping"
    HEART_EYES = "heart_eyes"
    SHOCKED = "shocked"
    SURPRISED = "surprised"
    SINGING = "singing"
    FOOTBALL = "football"
    GLITCH = "glitch"

# Các chế độ hoạt động chính (App Modes)
class AppMode:
    FACE = "face"           # Chế độ mặt tương tác & trò chuyện
    GAMES = "games"         # Menu / Mini-games
    TOOLS = "tools"         # Công cụ (Timer, Jukebox, Mirror)
    SETTINGS = "settings"   # Cài đặt âm thanh, giọng nói, scanlines
    HELP = "help"           # Hướng dẫn sử dụng phím tắt

# Phím tắt điều khiển nhanh
HOTKEYS_INFO = [
    ("ESC", "Mở Menu / Quay lại"),
    ("ENTER", "Mở thanh Chat / Nhập lệnh"),
    ("SPACE", "BMO chào / BMO Chop!"),
    ("1 - 4", "Chơi nhanh 4 Mini-Games"),
    ("5 - 7", "Mở Timer / Jukebox / Gương Football"),
    ("E", "Đổi biểu cảm ngẫu nhiên"),
    ("V", "Đổi giọng nói TTS"),
    ("M", "Bật/Tắt âm thanh SFX"),
    ("C", "Bật/Tắt hiệu ứng CRT Scanlines"),
    ("H", "Xem hướng dẫn chi tiết"),
]
