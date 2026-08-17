"""
BMO Procedural 8-bit Audio & Chiptune Synthesizer
Tạo âm thanh retro, tiếng bleep, bloop, fanfares và nhạc nền 8-bit bằng numpy + pygame.mixer.
Hoạt động 100% offline không cần file mp3/wav ngoài.
"""
import numpy as np
import pygame
import threading
import time

SAMPLE_RATE = 44100

class SoundSynthesizer:
    def __init__(self):
        self.enabled = True
        self.volume = 0.6
        self._sound_cache = {}
        self._music_thread = None
        self._stop_music = threading.Event()
        
        # Đảm bảo pygame.mixer đã khởi tạo
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
            
        self._pregenerate_sounds()

    def _generate_wave(self, freq, duration, wave_type='square', decay=True, duty=0.5):
        """Sinh mảng numpy cho dạng sóng âm thanh."""
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
        
        if wave_type == 'square':
            wave = np.where((t * freq) % 1.0 < duty, 1.0, -1.0)
        elif wave_type == 'sine':
            wave = np.sin(2 * np.pi * freq * t)
        elif wave_type == 'triangle':
            wave = 2 * np.abs(2 * ((t * freq) % 1.0) - 1) - 1
        elif wave_type == 'sawtooth':
            wave = 2 * ((t * freq) % 1.0) - 1
        elif wave_type == 'noise':
            wave = np.random.uniform(-1.0, 1.0, len(t))
        else:
            wave = np.sin(2 * np.pi * freq * t)

        if decay:
            envelope = np.exp(-3 * t / duration)
            wave = wave * envelope
            
        # Chuyển đổi sang chuẩn 16-bit PCM stereo
        audio = (wave * 32767 * self.volume).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def _generate_slide_wave(self, start_freq, end_freq, duration, wave_type='square'):
        """Sinh âm thanh trượt tần số (dùng cho jump, laser, slash)."""
        num_samples = int(SAMPLE_RATE * duration)
        t = np.linspace(0, duration, num_samples, endpoint=False)
        # Tần số biến thiên theo thời gian
        freqs = np.linspace(start_freq, end_freq, num_samples)
        phase = 2 * np.pi * np.cumsum(freqs) / SAMPLE_RATE
        
        if wave_type == 'square':
            wave = np.sign(np.sin(phase))
        elif wave_type == 'noise':
            wave = np.random.uniform(-0.8, 0.8, num_samples) * (1 - t/duration)
        else:
            wave = np.sin(phase)
            
        envelope = np.linspace(1.0, 0.0, num_samples)
        wave = wave * envelope
        
        audio = (wave * 32767 * self.volume).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def _pregenerate_sounds(self):
        """Khởi tạo trước các âm thanh cơ bản."""
        try:
            # 1. Beep / Bloop tương tác
            self._sound_cache['beep'] = self._generate_wave(587.33, 0.08, 'square')      # D5
            self._sound_cache['bloop'] = self._generate_wave(440.0, 0.12, 'triangle')    # A4
            self._sound_cache['chirp'] = self._generate_slide_wave(600, 1200, 0.09, 'square')
            
            # 2. Game SFX
            self._sound_cache['jump'] = self._generate_slide_wave(220, 660, 0.18, 'square')
            self._sound_cache['laser'] = self._generate_slide_wave(900, 150, 0.14, 'sawtooth')
            self._sound_cache['chop'] = self._generate_slide_wave(400, 80, 0.15, 'noise')
            self._sound_cache['hit'] = self._generate_slide_wave(180, 60, 0.12, 'noise')
            
            # 3. Coin / Tiền vàng
            coin_t = np.linspace(0, 0.18, int(SAMPLE_RATE * 0.18), endpoint=False)
            mid = len(coin_t) // 2
            w1 = np.sin(2 * np.pi * 987.77 * coin_t[:mid])   # B5
            w2 = np.sin(2 * np.pi * 1318.51 * coin_t[mid:])  # E6
            coin_w = np.concatenate((w1, w2)) * np.exp(-4 * coin_t / 0.18)
            coin_pcm = (coin_w * 32767 * self.volume).astype(np.int16)
            self._sound_cache['coin'] = pygame.sndarray.make_sound(np.column_stack((coin_pcm, coin_pcm)))

            # 4. Simon 4 nốt (Yellow, Blue, Green, Red)
            self._sound_cache['simon_0'] = self._generate_wave(329.63, 0.35, 'triangle', decay=False) # E4 (Vàng)
            self._sound_cache['simon_1'] = self._generate_wave(277.18, 0.35, 'triangle', decay=False) # C#4 (Xanh dương)
            self._sound_cache['simon_2'] = self._generate_wave(440.00, 0.35, 'triangle', decay=False) # A4 (Xanh lá)
            self._sound_cache['simon_3'] = self._generate_wave(659.25, 0.35, 'triangle', decay=False) # E5 (Đỏ)

            # 5. Fanfare thắng / Thua
            self._sound_cache['win'] = self._generate_slide_wave(440, 880, 0.4, 'square')
            self._sound_cache['game_over'] = self._generate_slide_wave(400, 100, 0.5, 'triangle')
            self._sound_cache['alarm'] = self._generate_wave(880, 0.25, 'square')
        except Exception as e:
            print(f"[SoundSynth] Warning pre-generating sounds: {e}")

    def play(self, sound_name):
        """Phát âm thanh theo tên."""
        if not self.enabled:
            return
        snd = self._sound_cache.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def play_note(self, freq, duration=0.25, wave_type='triangle'):
        """Phát một nốt nhạc tần số bất kỳ (dùng cho đàn Piano / Jukebox)."""
        if not self.enabled:
            return
        try:
            snd = self._generate_wave(freq, duration, wave_type=wave_type, decay=True)
            snd.play()
        except Exception:
            pass

    def play_adventure_theme(self):
        """Phát giai điệu mở đầu Adventure Time phong cách 8-bit Chiptune."""
        if not self.enabled:
            return
        self.stop_music()
        self._stop_music.clear()
        
        def _theme_worker():
            # Nhịp điệu & nốt nhạc (G4, E4, D4, C4, G4, A4, C5...)
            notes = [
                (392.00, 0.25), (329.63, 0.25), (293.66, 0.25), (261.63, 0.4), # Adventure Time,
                (392.00, 0.25), (440.00, 0.25), (523.25, 0.5),                  # Come on grab your friends,
                (440.00, 0.25), (493.88, 0.25), (523.25, 0.25), (587.33, 0.4), # We'll go to very
                (523.25, 0.25), (440.00, 0.25), (392.00, 0.6),                  # distant lands!
                (392.00, 0.25), (440.00, 0.25), (523.25, 0.25), (659.25, 0.4), # With Jake the Dog
                (587.33, 0.25), (523.25, 0.25), (440.00, 0.5),                  # and Finn the Human
                (392.00, 0.2), (440.00, 0.2), (523.25, 0.3), (587.33, 0.3),    # The fun will never
                (659.25, 0.7), (523.25, 0.8)                                    # end, Adventure Time!
            ]
            for freq, dur in notes:
                if self._stop_music.is_set():
                    break
                self.play_note(freq, dur * 0.95, 'square')
                time.sleep(dur)
                
        self._music_thread = threading.Thread(target=_theme_worker, daemon=True)
        self._music_thread.start()

    def play_bmo_song(self):
        """Phát bài hát 'Time is an illusion' / BMO's song."""
        if not self.enabled:
            return
        self.stop_music()
        self._stop_music.clear()

        def _bmo_song_worker():
            melody = [
                (261.63, 0.3), (329.63, 0.3), (392.00, 0.3), (523.25, 0.5),
                (392.00, 0.3), (329.63, 0.3), (261.63, 0.6),
                (293.66, 0.3), (349.23, 0.3), (440.00, 0.3), (587.33, 0.5),
                (440.00, 0.3), (349.23, 0.3), (293.66, 0.6),
            ]
            for freq, dur in melody:
                if self._stop_music.is_set():
                    break
                self.play_note(freq, dur * 0.9, 'triangle')
                time.sleep(dur)

        self._music_thread = threading.Thread(target=_bmo_song_worker, daemon=True)
        self._music_thread.start()

    def stop_music(self):
        """Dừng bài hát đang phát."""
        self._stop_music.set()

    def toggle_sound(self):
        """Bật/tắt toàn bộ âm thanh."""
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop_music()
        return self.enabled

# Khởi tạo instance dùng chung
synth = SoundSynthesizer()
