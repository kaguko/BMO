"""
BMO Face & Main Controller Launcher
"""
import sys
import os

# Thiết lập đường dẫn thư mục gốc
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

for d in [current_dir, parent_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from bmo.bmo_controller import BMOController
    def run_app():
        app = BMOController()
        app.run()
        
    if __name__ == "__main__":
        run_app()
except ImportError:
    # Fallback to local import if inside BMO folder
    from main import main
    if __name__ == "__main__":
        main()
