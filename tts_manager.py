"""
BMO TTS (Text-to-Speech) Manager - Adventure Time Lore Accurate Engine
Quản lý giọng nói đa luồng, chuyển đổi cao độ (Pitch Shifting) thành giọng robot BMO
dễ thương (giống chất giọng Niki Yang trong phim), đồng bộ khẩu hình miệng và phụ đề.
"""
import pyttsx3
import threading
import queue
import time
import os
import tempfile
import wave
import numpy as np
import pygame

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
        
        # Cấu hình cao độ (Pitch Factor) chuẩn BMO
        # 1.28x tương đương nâng cao ~4.2 semitones: Giọng cao, trong trẻo, hoạt bát của BMO
        self.pitch_modes = [
            {"name": "BMO Lore (High Pitch)", "factor": 1.28, "rate": 185},
            {"name": "BMO Chibi (Extra Cute)", "factor": 1.42, "rate": 195},
            {"name": "Natural Voice (Standard)", "factor": 1.0, "rate": 180},
        ]
        self.pitch_mode_index = 0
        
        # Kênh âm thanh riêng cho giọng nói trong Pygame
        self.voice_channel = None
        self._init_mixer_channel()
        
        self._init_engine()
        self._start_worker()

    def _init_mixer_channel(self):
        """Khởi tạo kênh phát âm thanh giọng nói nếu Pygame mixer khả dụng."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            # Dành kênh 7 cho TTS
            self.voice_channel = pygame.mixer.Channel(7)
        except Exception as e:
            print(f"[TTSManager] Mixer init warning: {e}")
            self.voice_channel = None

    def _init_engine(self):
        """Khởi tạo engine pyttsx3 và tìm giọng nữ/trẻ phù hợp nhất cho BMO.
        Trên Android/Linux: sử dụng espeak nếu pyttsx3 SAPI5 không khả dụng."""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 185)
            self.voices = self.engine.getProperty('voices') or []
            
            # Ưu tiên giọng nữ trẻ (Zira, Hazel, Maria...) hoặc espeak trên Android
            preferred = os.environ.get('BMO_VOICE_KEYWORD', 'zira').lower()
            chosen_idx = 0
            for idx, v in enumerate(self.voices):
                haystack = f"{v.id} {v.name}".lower()
                if preferred in haystack or 'female' in haystack or 'girl' in haystack or 'zira' in haystack:
                    chosen_idx = idx
                    break
                    
            if self.voices:
                self.apply_voice(chosen_idx)
        except Exception as e:
            print(f"[TTSManager] pyttsx3 init failed ({e}), trying espeak fallback...")
            self.engine = None
            self._try_espeak_fallback()

    def _try_espeak_fallback(self):
        """Fallback TTS via espeak subprocess cho Android/Linux."""
        import shutil
        if shutil.which('espeak') or shutil.which('espeak-ng'):
            self._espeak_cmd = shutil.which('espeak-ng') or shutil.which('espeak')
            print(f"[TTSManager] Using espeak fallback: {self._espeak_cmd}")
        else:
            self._espeak_cmd = None
            print("[TTSManager] No TTS available - BMO will speak silently 🔇")



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
        """Chuyển đổi chế độ giọng (giữa BMO Lore, Chibi, Natural và các voice của hệ thống)."""
        # Xoay vòng giữa các chế độ pitch BMO và các voice hệ thống
        self.pitch_mode_index = (self.pitch_mode_index + 1) % len(self.pitch_modes)
        if self.pitch_mode_index == 0:
            self.apply_voice(self.voice_index + 1)
            
        cur_mode = self.pitch_modes[self.pitch_mode_index]
        cur_vname = self.voices[self.voice_index].name.split('-')[0].strip() if self.voices else "Default"
        return f"{cur_mode['name']} ({cur_vname})"

    def _pitch_shift_audio(self, raw_data, n_channels, sampwidth, framerate, factor=1.28):
        """Dịch chuyển cao độ âm thanh bằng giải thuật nội suy resampling numpy."""
        if factor == 1.0 or not raw_data:
            return raw_data
            
        dtype = np.int16 if sampwidth == 2 else np.uint8
        audio = np.frombuffer(raw_data, dtype=dtype)
        
        old_len = len(audio)
        new_len = int(old_len / factor)
        if new_len <= 0:
            return raw_data
            
        old_indices = np.arange(old_len)
        new_indices = np.linspace(0, old_len - 1, new_len)
        resampled = np.interp(new_indices, old_indices, audio).astype(dtype)
        return resampled.tobytes()

    def _start_worker(self):
        """Chạy luồng nền chuyên xử lý âm thanh & đọc thoại."""
        def _worker():
            temp_dir = tempfile.gettempdir()
            pid = os.getpid()
            raw_wav_path = os.path.join(temp_dir, f"bmo_raw_{pid}.wav")
            out_wav_path = os.path.join(temp_dir, f"bmo_voice_{pid}.wav")

            while not self._stop_event.is_set():
                try:
                    item = self.speech_queue.get(timeout=0.1)
                except queue.Empty:
                    # Cập nhật trạng thái nói từ kênh âm thanh
                    if self.voice_channel:
                        self.is_talking = self.voice_channel.get_busy()
                    continue

                text, on_start_cb, on_finish_cb, pitch_override, custom_sub = item
                if self.muted or not text:
                    self.speech_queue.task_done()
                    continue
                
                # Khi không có engine pyttsx3 (ví dụ Android) -> dùng espeak
                if not self.engine:
                    espeak = getattr(self, '_espeak_cmd', None)
                    if espeak:
                        import subprocess
                        self.is_talking = True
                        self.current_subtitle = custom_sub if custom_sub is not None else text
                        self.subtitle_timer = time.time() + max(3.0, len(self.current_subtitle) * 0.075)
                        try:
                            subprocess.run([espeak, '-s', '185', '-v', 'en', text], timeout=15)
                        except Exception:
                            pass
                        finally:
                            self.is_talking = False
                    self.speech_queue.task_done()
                    continue

                mode = self.pitch_modes[self.pitch_mode_index]
                pitch_factor = pitch_override if pitch_override is not None else mode["factor"]
                rate = mode["rate"]

                try:
                    self.is_talking = True
                    self.current_subtitle = custom_sub if custom_sub is not None else text
                    self.subtitle_timer = time.time() + max(3.0, len(self.current_subtitle) * 0.075)

                    if on_start_cb:
                        on_start_cb()

                    # 1. Thử xuất ra file WAV và Pitch-Shift sang chất giọng BMO chuẩn
                    try:
                        self.engine.setProperty('rate', rate)
                        if os.path.exists(raw_wav_path):
                            try: os.remove(raw_wav_path)
                            except Exception: pass

                        self.engine.save_to_file(text, raw_wav_path)
                        self.engine.runAndWait()

                        if os.path.exists(raw_wav_path) and os.path.getsize(raw_wav_path) > 44:
                            with wave.open(raw_wav_path, 'rb') as wf:
                                n_channels = wf.getnchannels()
                                sampwidth = wf.getsampwidth()
                                framerate = wf.getframerate()
                                n_frames = wf.getnframes()
                                raw_bytes = wf.readframes(n_frames)

                            shifted_bytes = self._pitch_shift_audio(
                                raw_bytes, n_channels, sampwidth, framerate, factor=pitch_factor
                            )

                            with wave.open(out_wav_path, 'wb') as wf:
                                wf.setnchannels(n_channels)
                                wf.setsampwidth(sampwidth)
                                wf.setframerate(framerate)
                                wf.writeframes(shifted_bytes)

                            # Phát qua Pygame Mixer
                            if pygame.mixer.get_init():
                                voice_snd = pygame.mixer.Sound(out_wav_path)
                                if self.voice_channel:
                                    self.voice_channel.play(voice_snd)
                                    while self.voice_channel.get_busy() and not self._stop_event.is_set():
                                        time.sleep(0.03)
                                else:
                                    voice_snd.play()
                                    time.sleep(voice_snd.get_length())
                            else:
                                self.engine.say(text)
                                self.engine.runAndWait()
                        else:
                            # Fallback nếu không ghi được file
                            self.engine.say(text)
                            self.engine.runAndWait()

                    except Exception as sub_err:
                        print(f"[TTSManager] Pitch-shift fallback: {sub_err}")
                        self.engine.say(text)
                        self.engine.runAndWait()

                except Exception as e:
                    print(f"[TTSManager] Speak error: {e}")
                finally:
                    self.is_talking = False
                    if on_finish_cb:
                        on_finish_cb()
                    self.speech_queue.task_done()

            # Dọn dẹp file tạm khi thoát
            for f in [raw_wav_path, out_wav_path]:
                if os.path.exists(f):
                    try: os.remove(f)
                    except Exception: pass

        self._worker_thread = threading.Thread(target=_worker, daemon=True)
        self._worker_thread.start()

    def speak(self, text, on_start=None, on_finish=None, clear_queue=False, pitch_override=None, subtitle=None):
        """Đưa câu nói vào hàng đợi đọc."""
        if not text:
            return
        if clear_queue:
            if self.voice_channel:
                try:
                    self.voice_channel.stop()
                except Exception:
                    pass
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                    self.speech_queue.task_done()
                except Exception:
                    pass
        disp_sub = subtitle if subtitle is not None else text
        self.current_subtitle = disp_sub
        self.subtitle_timer = time.time() + max(3.5, len(disp_sub) * 0.08)
        self.speech_queue.put((text, on_start, on_finish, pitch_override, subtitle))

    def get_subtitle(self):
        """Lấy phụ đề câu nói hiện tại."""
        if time.time() > self.subtitle_timer:
            self.current_subtitle = ""
        return self.current_subtitle

    def toggle_mute(self):
        """Bật/tắt giọng nói."""
        self.muted = not self.muted
        if self.muted and self.voice_channel:
            self.voice_channel.stop()
        return not self.muted

    def stop(self):
        """Dừng worker và ngắt kênh âm thanh."""
        self._stop_event.set()
        if self.voice_channel:
            try:
                self.voice_channel.stop()
            except Exception:
                pass

tts = TTSManager()
