"""
BMO - Adventure Time Companion & Retro Gaming Console
Chạy BMO 100% offline không cần API AI bên ngoài.

Tác giả: Adventure Time BMO Project
"""
import sys
import os

# Thêm cả thư mục gốc và thư mục BMO vào sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
bmo_sub_dir = os.path.join(current_dir, "BMO")

for d in [current_dir, bmo_sub_dir]:
    if os.path.exists(d) and d not in sys.path:
        sys.path.insert(0, d)

try:
    from BMO.bmo_controller import BMOController
except ImportError:
    try:
        from bmo.bmo_controller import BMOController
    except ImportError:
        from bmo_controller import BMOController

def main():
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
