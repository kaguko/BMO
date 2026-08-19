"""
BMO - Adventure Time Companion & Retro Gaming Console
Chạy BMO 100% offline không cần API AI bên ngoài.
Hỗ trợ: Windows/macOS/Linux (Desktop) và Android (APK qua Buildozer).
"""
import sys
import os

# Thêm cả thư mục gốc và thư mục BMO vào sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
bmo_sub_dir = os.path.join(current_dir, "BMO")

for d in [current_dir, bmo_sub_dir]:
    if os.path.exists(d) and d not in sys.path:
        sys.path.insert(0, d)

# Phát hiện môi trường Android
IS_ANDROID = 'ANDROID_ARGUMENT' in os.environ or 'ANDROID_ROOT' in os.environ

if IS_ANDROID:
    # Trên Android: Bật fullscreen và chế độ cảm ứng
    os.environ['ANDROID_ARGUMENT'] = '1'
    os.environ['SDL_AUDIODRIVER'] = 'android'
    os.environ['BMO_VOICE_KEYWORD'] = 'espeak'  # Dùng espeak thay vì SAPI5

try:
    from BMO.bmo_controller import BMOController
except ImportError:
    try:
        from bmo.bmo_controller import BMOController
    except ImportError:
        from bmo_controller import BMOController

def main():
    if not IS_ANDROID:
        print("=" * 60)
        print("           🌟 BMO - ADVENTURE TIME SIMULATOR 🌟           ")
        print("=" * 60)
        print("🤖 Mode: 100% OFFLINE (No Cloud / AI API required)")
        print("🎮 Features: Interactive Face, NLP Dialog, 4 Mini-Games,")
        print("             Pomodoro Timer, Chiptune Jukebox, Football Mirror")
        print("⌨️  Controls:")
        print("   - [ENTER] : Chat with BMO")
        print("   - [ESC]   : Open Menu / Mini-Games / Tools")
        print("   - [SPACE] : BMO Chop! / Greet")
        print("   - [1 - 4] : Quick Launch Mini-Games")
        print("   - [5 - 7] : Quick Launch Tools")
        print("   - [MOUSE] : Click forehead to pet / click cheeks to tickle")
        print("=" * 60)
    
    app = BMOController()
    app.run()

if __name__ == "__main__":
    main()

