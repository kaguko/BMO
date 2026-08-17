"""
BMO Constants and Theme Configuration
Màu sắc, kích thước, phông chữ và các hằng số dùng chung cho BMO.
Hỗ trợ cả Desktop (800x600) lẫn Mobile Android (portrait 480x854).
"""
import os
import pygame

# Phát hiện môi trường Android / Mobile
_IS_ANDROID = 'ANDROID_ARGUMENT' in os.environ or 'ANDROID_ROOT' in os.environ

if _IS_ANDROID:
    # Màn hình mobile portrait chuẩn (sẽ fullscreen trên thiết bị thật)
    SCREEN_WIDTH = 480
    SCREEN_HEIGHT = 854
    IS_MOBILE = True
else:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    IS_MOBILE = False

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
    VOMIT = "vomit"

# Các chế độ hoạt động chính (App Modes)
class AppMode:
    FACE = "face"                     # Chế độ mặt tương tác & trò chuyện
    GAMES = "games"                   # Mini-games
    TOOLS = "tools"                   # Công cụ (Timer, Jukebox, Mirror)
    SETTINGS = "settings"             # Cài đặt âm thanh, giọng nói, scanlines
    HELP = "help"                     # Hướng dẫn sử dụng phím tắt
    LOW_BATTERY = "low_battery"       # BMO sập nguồn hết pin & Thay pin
    CARTRIDGE_SWAP = "cartridge_swap" # Chuyển cảnh nhổ/nhét băng game

# Phím tắt điều khiển nhanh
HOTKEYS_INFO = [
    ("ESC / TAB", "Mở/Đóng Menu điều khiển chính"),
    ("ENTER", "Mở thanh Chat trò chuyện với BMO"),
    ("SPACE", "BMO chào / BMO Chop! / Tương tác"),
    ("1 - 4", "Chơi 4 Mini-Games (Kèm hiệu ứng nôn băng)"),
    ("5 - 7", "Mở Timer / Jukebox / Gương Football"),
    ("L", "Giả lập BMO Sập nguồn (Hết pin)"),
    ("P", "Thay 2 pin AA khi BMO hết pin"),
    ("E", "Đổi biểu cảm khuôn mặt ngẫu nhiên"),
    ("V", "Đổi chế độ giọng nói TTS"),
    ("M", "Bật/Tắt âm thanh SFX 8-bit"),
    ("C / B", "Bật/Tắt CRT Scanlines & Khung Bezel"),
    ("H", "Xem bảng hướng dẫn chi tiết"),
]
