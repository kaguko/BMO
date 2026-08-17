"""
BMO TTS (Text-to-Speech) Manager
Quản lý giọng nói đa luồng, đồng bộ khẩu hình miệng và phụ đề trên màn hình.
"""
import pyttsx3
import threading
import queue
import time
import os

class TTSManager:
    def __init__(self):
        self.speech_queue = queue.Queue()
        self.is_talking = False
        self.current_subtitle = ""
        self.subtitle_timer = 0
        self.muted = False
        self.voice_index = 0
        self.voices = []
        self._worker_thread = None
        self._stop_event = threading.Event()
        
        self._init_engine()
        self._start_worker()

    def _init_engine(self):
        """Khởi tạo engine pyttsx3 và tìm giọng nói phù hợp nhất cho BMO."""
        try:
            self.engine = pyttsx3.init()
            # Tốc độ nói nhanh, nhẹ nhàng giống robot con nít BMO
            self.engine.setProperty('rate', 180)
            self.voices = self.engine.getProperty('voices') or []
            
            # Ưu tiên tìm giọng nữ trẻ (Zira, Hazel, Maria...) để gần giọng BMO nhất
            preferred = os.environ.get('BMO_VOICE_KEYWORD', 'zira').lower()
            chosen_idx = 0
            for idx, v in enumerate(self.voices):
                haystack = f"{v.id} {v.name}".lower()
                if preferred in haystack or 'female' in haystack or 'girl' in haystack:
                    chosen_idx = idx
                    break
                    
            if self.voices:
                self.apply_voice(chosen_idx)
        except Exception as e:
            print(f"[TTSManager] Init error: {e}")
            self.engine = None

    def apply_voice(self, index):
        """Đổi giọng theo index."""
        if not self.engine or not self.voices:
            return
        self.voice_index = index % len(self.voices)
        v = self.voices[self.voice_index]
        try:
            self.engine.setProperty('voice', v.id)
            print(f"[TTSManager] Voice selected: {v.name}")
        except Exception as e:
            print(f"[TTSManager] Voice switch error: {e}")

    def next_voice(self):
        """Chuyển sang giọng kế tiếp."""
        self.apply_voice(self.voice_index + 1)
        if self.voices:
            return self.voices[self.voice_index].name
        return "Default"

    def _start_worker(self):
        """Chạy luồng nền chuyên đọc câu thoại để không bao giờ lag Pygame."""
        def _worker():
            while not self._stop_event.is_set():
                try:
                    text, on_start_cb, on_finish_cb = self.speech_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                if self.muted or not self.engine or not text:
                    self.speech_queue.task_done()
                    continue

                try:
                    self.is_talking = True
                    self.current_subtitle = text
                    self.subtitle_timer = time.time() + max(3.0, len(text) * 0.08)
                    
                    if on_start_cb:
                        on_start_cb()
                        
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    print(f"[TTSManager] Speak error: {e}")
                finally:
                    self.is_talking = False
                    if on_finish_cb:
                        on_finish_cb()
                    self.speech_queue.task_done()

        self._worker_thread = threading.Thread(target=_worker, daemon=True)
        self._worker_thread.start()

    def speak(self, text, on_start=None, on_finish=None, clear_queue=False):
        """Đưa câu nói vào hàng đợi đọc."""
        if not text:
            return
        if clear_queue:
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                    self.speech_queue.task_done()
                except Exception:
                    pass
        self.current_subtitle = text
        self.subtitle_timer = time.time() + max(3.5, len(text) * 0.08)
        self.speech_queue.put((text, on_start, on_finish))

    def get_subtitle(self):
        """Lấy phụ đề câu nói hiện tại."""
        if time.time() > self.subtitle_timer:
            self.current_subtitle = ""
        return self.current_subtitle

    def toggle_mute(self):
        """Bật/tắt giọng nói."""
        self.muted = not self.muted
        return not self.muted

    def stop(self):
        """Dừng worker."""
        self._stop_event.set()

tts = TTSManager()
