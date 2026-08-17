"""
BMO Master Controller (Enhanced Edition)
Điều phối toàn bộ hệ thống BMO: Khuôn mặt biểu cảm, Hội thoại offline,
Chế độ Football trong gương (tự động khi Idle), Cơ chế sập nguồn & Thay 2 pin AA,
Hiệu ứng "Nôn mửa" băng game (Cartridge Spit/Insert), 4 Mini-Games và Công cụ.
"""
import pygame
import random
import time
from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BMO_TEAL, BMO_BODY_TEAL,
    BMO_DARK_TEAL, BMO_BLACK, BMO_WHITE, BMO_YELLOW,
    BMO_BLUE, BMO_GREEN, BMO_HEART_RED, AppMode, Expression,
    HOTKEYS_INFO, IS_MOBILE
)
from .audio_synth import synth
from .tts_manager import tts
from .face_renderer import FaceRenderer
from .dialog_engine import dialog_engine
from .menu_system import MenuSystem
from .games import RunnerGame, BugInvadersGame, SimonGame, RainicornFlapGame
from .tools import TimerTool, JukeboxTool, FootballTool

class BMOController:
    def __init__(self):
        pygame.init()
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        # Android: fullscreen; Desktop: fixed window
        if IS_MOBILE:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("BMO - Adventure Time Companion & Retro Console")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Chế độ hiện tại
        self.mode = AppMode.FACE
        
        # Khởi tạo các hệ thống con
        self.face = FaceRenderer(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.menu = MenuSystem()
        
        # Mini-games
        self.game_runner = RunnerGame()
        self.game_bugs = BugInvadersGame()
        self.game_simon = SimonGame()
        self.game_rainicorn = RainicornFlapGame()
        self.active_game = None
        self.current_game_name = "IDLE CHIP"
        
        # Tools
        self.tool_timer = TimerTool()
        self.tool_jukebox = JukeboxTool()
        self.tool_football = FootballTool()
        self.active_tool = None
        
        # Thanh nhập liệu Chat (Interactive Chat Input Bar)
        self.is_chatting = False
        self.chat_text = ""
        self.chat_cursor_visible = True
        self.chat_cursor_timer = 0
        
        # 1. Quản lý thời gian Idle (Treo máy -> Tự bật Football)
        self.last_activity_time = time.time()
        self.idle_timeout = 45.0  # 45 giây không thao tác -> BMO tự nói chuyện với Football
        
        # 2. Giả lập Pin & Sập nguồn (Low Battery & Thay Pin)
        self.battery_level = 100.0
        self.p_hold_progress = 0.0
        self.is_holding_p = False
        self._last_battery_sfx_time = 0
        
        # 3. Hiệu ứng Nôn mửa / Đổi băng game (Cartridge Spit / Insert Transition)
        self.cartridge_old_name = "CHOP RUNNER"
        self.cartridge_new_name = "BUG INVADERS"
        self.cartridge_progress = 0.0
        self.cartridge_target_game = None
        self._cart_insert_played = False
        
        # Phông chữ giao diện (Segoe UI / Arial hỗ trợ tiếng Việt mượt mà)
        self.font_chat = pygame.font.SysFont("Segoe UI, Arial", 18, bold=True)
        self.font_hint = pygame.font.SysFont("Segoe UI, Arial", 14)
        self.font_settings = pygame.font.SysFont("Segoe UI, Arial", 18, bold=True)
        
        # Lời chào đầu tiên khi bật máy BMO
        self._boot_greeting()

    def _boot_greeting(self):
        synth.play('win')
        greeting = "Yay! BMO is online! Press ENTER to chat, or ESC for mini-games!"
        tts.speak(greeting)
        self.face.set_expression(Expression.HAPPY)

    def run(self):
        """Vòng lặp điều khiển chính (60 FPS)."""
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            # 1. Xử lý các sự kiện đầu vào
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                # Cập nhật thời gian hoạt động cuối
                if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION]:
                    self.last_activity_time = time.time()
                self._handle_event(event)

            # 2. Cập nhật logic theo chế độ
            self._update(mouse_pos)

            # 3. Vẽ khung hình
            self._draw()

            pygame.display.flip()
            self.clock.tick(FPS)

        # Dọn dẹp tài nguyên khi tắt
        tts.stop()
        synth.stop_music()
        pygame.quit()

    def _handle_event(self, event):
        # 0. Nếu đang ở màn hình Sập nguồn (LOW_BATTERY)
        if self.mode == AppMode.LOW_BATTERY:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_p, pygame.K_SPACE]:
                    self.is_holding_p = True
                elif event.key == pygame.K_ESCAPE:
                    # Hồi sinh ngay
                    self._recharge_battery_complete()
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_p, pygame.K_SPACE]:
                    self.is_holding_p = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.is_holding_p = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.is_holding_p = False
            return

        # 1. Nếu Menu đang mở -> Chuyển sự kiện cho Menu
        if self.menu.is_open:
            action = self.menu.handle_event(event)
            if action:
                self._handle_menu_action(action)
            return

        # 2. Nếu đang trong chế độ gõ Chat
        if self.is_chatting:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self._submit_chat()
                elif event.key == pygame.K_ESCAPE:
                    self.is_chatting = False
                    synth.play('bloop')
                elif event.key == pygame.K_BACKSPACE:
                    self.chat_text = self.chat_text[:-1]
                else:
                    if len(self.chat_text) < 70 and event.unicode and event.unicode.isprintable():
                        self.chat_text += event.unicode
            return

        # 3. Phím bấm toàn cục (Global Hotkeys)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_TAB:
                self.menu.toggle()
                return
            elif event.key == pygame.K_RETURN and self.mode == AppMode.FACE:
                self.is_chatting = True
                self.chat_text = ""
                synth.play('chirp')
                return
            elif event.key == pygame.K_e and self.mode == AppMode.FACE:
                # Đổi biểu cảm ngẫu nhiên
                exprs = [
                    Expression.HAPPY, Expression.LAUGH, Expression.EXCITED,
                    Expression.HEART_EYES, Expression.SHOCKED, Expression.ANGRY_CHOP,
                    Expression.SINGING, Expression.SLEEPY, Expression.IDLE
                ]
                new_expr = random.choice(exprs)
                self.face.set_expression(new_expr)
                synth.play('chirp')
                return
            elif event.key == pygame.K_v:
                # Đổi giọng nói TTS
                v_name = tts.next_voice()
                tts.speak(f"Voice changed to {v_name}")
                return
            elif event.key == pygame.K_m:
                # Bật/tắt SFX
                is_on = synth.toggle_sound()
                tts.speak(f"Sound effects {'enabled' if is_on else 'muted'}")
                return
            elif event.key == pygame.K_c:
                # Bật/tắt CRT Scanlines
                self.face.show_scanlines = not self.face.show_scanlines
                synth.play('bloop')
                return
            elif event.key == pygame.K_b:
                # Bật/tắt Khung Bezel BMO
                self.face.show_bezel = not self.face.show_bezel
                synth.play('bloop')
                return
            elif event.key == pygame.K_l:
                # Phím nóng kích hoạt sập nguồn hết pin ngay lập tức để trải nghiệm
                self._trigger_battery_depletion()
                return
            elif event.key == pygame.K_h:
                self.mode = AppMode.HELP
                return

        # 4. Phím tắt số chọn nhanh khi ở màn hình chính
        if self.mode == AppMode.FACE and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # BMO Chop hoặc chào
                self._submit_quick_prompt("bmo chop")
            elif event.key == pygame.K_1:
                self._start_game_with_cartridge_swap(self.game_runner, "CHOP RUNNER")
            elif event.key == pygame.K_2:
                self._start_game_with_cartridge_swap(self.game_bugs, "BUG INVADERS")
            elif event.key == pygame.K_3:
                self._start_game_with_cartridge_swap(self.game_simon, "SIMON CHIPTUNE")
            elif event.key == pygame.K_4:
                self._start_game_with_cartridge_swap(self.game_rainicorn, "RAINICORN FLAP")
            elif event.key == pygame.K_5:
                self.active_tool = self.tool_timer
                self.mode = AppMode.TOOLS
            elif event.key == pygame.K_6:
                self.active_tool = self.tool_jukebox
                self.mode = AppMode.TOOLS
            elif event.key == pygame.K_7:
                self._open_football_mode()

        # 5. Nhấp chuột tương tác lên khuôn mặt BMO (và nút cảm ứng Mobile)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Kiểm tra nút cảm ứng Mobile trước
            if IS_MOBILE:
                touch_rects = getattr(self, '_mobile_touch_btn_rects', {})
                for btn_id, rect in touch_rects.items():
                    if rect.collidepoint(event.pos):
                        if btn_id == "menu":
                            self.menu.toggle()
                        elif btn_id == "chat":
                            if self.mode == AppMode.FACE:
                                self.is_chatting = not self.is_chatting
                                self.chat_text = ""
                                synth.play('chirp')
                        elif btn_id == "g1":
                            self._start_game_with_cartridge_swap(self.game_runner, "CHOP RUNNER")
                        elif btn_id == "g2":
                            self._start_game_with_cartridge_swap(self.game_bugs, "BUG INVADERS")
                        elif btn_id == "g3":
                            self._start_game_with_cartridge_swap(self.game_simon, "SIMON CHIPTUNE")
                        elif btn_id == "g4":
                            self._start_game_with_cartridge_swap(self.game_rainicorn, "RAINICORN FLAP")
                        return  # Đã xử lý touch bar -> không truyền tiếp cho face

            # Tương tác vuốt/nhấp vào khuôn mặt BMO
            if self.mode == AppMode.FACE:
                pet_action = self.face.check_interaction_click(event.pos)
                if pet_action == "pet_head":
                    synth.play('win')
                    tts.speak("Hehehe! BMO loves head pats! Yay!", clear_queue=True)
                elif pet_action == "tickle_cheek":
                    synth.play('chirp')
                    tts.speak("Beep boop! That tickles BMO!", clear_queue=True)
                elif pet_action == "poke_mouth":
                    synth.play('bloop')
                    tts.speak("Aaaaah! Who wants to play video games?", clear_queue=True)

        # 6. Chuyển sự kiện cho Game / Tool đang hoạt động
        if self.mode == AppMode.GAMES and self.active_game:
            self.active_game.handle_event(event)
            if self.active_game.exit_requested:
                self.mode = AppMode.FACE
                self.active_game = None

        elif self.mode == AppMode.TOOLS and self.active_tool:
            self.active_tool.handle_event(event)
            if self.active_tool.exit_requested:
                self.mode = AppMode.FACE
                self.active_tool = None

        elif self.mode in [AppMode.SETTINGS, AppMode.HELP]:
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE]:
                self.mode = AppMode.FACE
                synth.play('bloop')

    def _open_football_mode(self):
        """Mở chế độ Football trong gương."""
        self.active_tool = self.tool_football
        self.tool_football.reset_to_first()
        self.mode = AppMode.TOOLS

    def _trigger_battery_depletion(self):
        """Kích hoạt trạng thái sập nguồn (Hết pin)."""
        self.battery_level = 0.0
        self.mode = AppMode.LOW_BATTERY
        self.p_hold_progress = 0.0
        self.is_holding_p = False
        synth.play('power_down')
        tts.speak("BMO cần pin... BMO is losing power... please change my AA batteries!", clear_queue=True)

    def _recharge_battery_complete(self):
        """Hoàn tất quá trình thay pin và hồi sinh BMO."""
        self.battery_level = 100.0
        self.mode = AppMode.FACE
        self.p_hold_progress = 0.0
        self.is_holding_p = False
        synth.play('power_up')
        tts.speak("Yay! BMO is back alive! New AA batteries feel so good!", clear_queue=True)
        self.face.set_expression(Expression.HEART_EYES)

    def _start_game_with_cartridge_swap(self, game_instance, game_name):
        """Khởi chạy game kèm hoạt ảnh BMO nôn mửa băng cũ và nhét băng mới."""
        self.cartridge_old_name = self.current_game_name
        self.cartridge_new_name = game_name
        self.current_game_name = game_name
        self.cartridge_target_game = game_instance
        self.cartridge_progress = 0.0
        self._cart_insert_played = False
        self.mode = AppMode.CARTRIDGE_SWAP
        synth.play('barf')

    def _submit_chat(self):
        """Gửi câu chat tới DialogEngine."""
        query = self.chat_text.strip()
        self.is_chatting = False
        self.chat_text = ""
        if not query:
            return

        self._process_dialog_response(query)

    def _submit_quick_prompt(self, prompt):
        self._process_dialog_response(prompt)

    def _process_dialog_response(self, query):
        reply, expr, snd, action = dialog_engine.respond(query)
        
        # Đổi biểu cảm khuôn mặt
        self.face.set_expression(expr)
        
        # Phát âm thanh SFX
        if snd:
            synth.play(snd)
            
        # Đọc câu thoại TTS
        tts.speak(reply, clear_queue=True)
        
        # Thực hiện hành động đặc biệt nếu có
        if action == "play_theme":
            synth.play_adventure_theme()
        elif action == "open_games_menu":
            self.menu.open()
        elif action == "start_game_runner":
            self._start_game_with_cartridge_swap(self.game_runner, "CHOP RUNNER")
        elif action == "start_game_bugs":
            self._start_game_with_cartridge_swap(self.game_bugs, "BUG INVADERS")
        elif action == "start_game_simon":
            self._start_game_with_cartridge_swap(self.game_simon, "SIMON CHIPTUNE")
        elif action == "start_game_rainicorn":
            self._start_game_with_cartridge_swap(self.game_rainicorn, "RAINICORN FLAP")
        elif action == "football_mode":
            self._open_football_mode()
        elif action == "trigger_low_battery":
            self._trigger_battery_depletion()
        elif action == "recharge_battery":
            self._recharge_battery_complete()
        elif action == "demo_cartridge_swap":
            self._start_game_with_cartridge_swap(self.game_runner, "CHOP RUNNER")

    def _handle_menu_action(self, action_id):
        if action_id == "face":
            self.mode = AppMode.FACE
        elif action_id == "game_runner":
            self._start_game_with_cartridge_swap(self.game_runner, "CHOP RUNNER")
        elif action_id == "game_bugs":
            self._start_game_with_cartridge_swap(self.game_bugs, "BUG INVADERS")
        elif action_id == "game_simon":
            self._start_game_with_cartridge_swap(self.game_simon, "SIMON CHIPTUNE")
        elif action_id == "game_rainicorn":
            self._start_game_with_cartridge_swap(self.game_rainicorn, "RAINICORN FLAP")
        elif action_id == "tool_timer":
            self.active_tool = self.tool_timer
            self.mode = AppMode.TOOLS
        elif action_id == "tool_jukebox":
            self.active_tool = self.tool_jukebox
            self.mode = AppMode.TOOLS
        elif action_id == "tool_football":
            self._open_football_mode()
        elif action_id == "settings":
            self.mode = AppMode.SETTINGS
        elif action_id == "help":
            self.mode = AppMode.HELP

    def _update(self, mouse_pos):
        now = time.time()
        
        # 1. Kiểm tra Idle treo máy -> Tự động nói chuyện với Football trong gương
        if self.mode == AppMode.FACE and not self.is_chatting and not self.menu.is_open:
            if now - self.last_activity_time >= self.idle_timeout:
                self.last_activity_time = now
                self._open_football_mode()
                tts.speak("Oh, you are away! Let me talk to my best friend Football in the mirror!", clear_queue=True)

        # 2. Tiêu hao pin tự nhiên (Khoảng 0.02% mỗi frame ~ 1.2% mỗi phút)
        if self.mode not in [AppMode.LOW_BATTERY, AppMode.CARTRIDGE_SWAP]:
            self.battery_level = max(0.0, self.battery_level - 0.015)
            if self.battery_level <= 0.0:
                self._trigger_battery_depletion()

        # 3. Xử lý tiến trình thay pin trong màn hình LOW_BATTERY
        if self.mode == AppMode.LOW_BATTERY:
            if self.is_holding_p:
                self.p_hold_progress += 0.02
                if now - self._last_battery_sfx_time > 0.25:
                    synth.play('battery_install')
                    self._last_battery_sfx_time = now
                if self.p_hold_progress >= 1.0:
                    self._recharge_battery_complete()
            else:
                self.p_hold_progress = max(0.0, self.p_hold_progress - 0.03)

        # 4. Xử lý tiến trình hoạt ảnh Nôn mửa & Nhét băng game
        elif self.mode == AppMode.CARTRIDGE_SWAP:
            self.cartridge_progress += 0.018 # ~1.0 giây
            if self.cartridge_progress >= 0.5 and not self._cart_insert_played:
                synth.play('cartridge_insert')
                self._cart_insert_played = True
            if self.cartridge_progress >= 1.0:
                self.mode = AppMode.GAMES
                self.active_game = self.cartridge_target_game
                self.active_game.reset()
                synth.play('win')

        # Cập nhật con trỏ nhấp nháy khi gõ chat
        if self.is_chatting:
            if now - self.chat_cursor_timer > 0.5:
                self.chat_cursor_visible = not self.chat_cursor_visible
                self.chat_cursor_timer = now

        if self.mode == AppMode.FACE:
            self.face.update(is_talking=tts.is_talking, mouse_pos=mouse_pos)
        elif self.mode == AppMode.GAMES and self.active_game:
            self.active_game.update()
        elif self.mode == AppMode.TOOLS and self.active_tool:
            self.active_tool.update()

    def _draw(self):
        # 1. Vẽ giao diện theo chế độ hiện tại
        if self.mode == AppMode.FACE:
            sub = tts.get_subtitle()
            self.face.draw(self.screen, subtitle=sub, battery_level=self.battery_level)
            self._draw_face_overlay_hints()
            if self.is_chatting:
                self._draw_chat_input_bar()

        elif self.mode == AppMode.CARTRIDGE_SWAP:
            self.face.draw_cartridge_swap(
                self.screen, self.cartridge_old_name, self.cartridge_new_name, self.cartridge_progress
            )

        elif self.mode == AppMode.LOW_BATTERY:
            self.face.draw_low_battery_screen(self.screen, self.p_hold_progress)

        elif self.mode == AppMode.GAMES and self.active_game:
            self.active_game.draw(self.screen)

        elif self.mode == AppMode.TOOLS and self.active_tool:
            self.active_tool.draw(self.screen)

        elif self.mode == AppMode.SETTINGS:
            self._draw_settings_screen()

        elif self.mode == AppMode.HELP:
            self._draw_help_screen()

        # 2. Vẽ Menu đè lên trên nếu đang mở
        self.menu.draw(self.screen)

        # 3. Nút cảm ứng on-screen cho Mobile
        if IS_MOBILE:
            self._draw_mobile_touch_bar()

    def _draw_face_overlay_hints(self):
        """Vẽ các gợi ý phím tắt nhỏ tinh tế ở góc màn hình."""
        if IS_MOBILE:
            return  # Không hiện hint bàn phím trên điện thoại
        hint_text = "[ENTER]: Chat BMO  |  [ESC/TAB]: Menu  |  [SPACE]: BMO Chop!  |  [L]: Hết pin  |  [H]: Help"
        h_surf = self.font_hint.render(hint_text, True, (40, 75, 65))
        self.screen.blit(h_surf, (16, 12))

    def _draw_mobile_touch_bar(self):
        """Vẽ thanh nút cảm ứng dưới màn hình cho Mobile Android."""
        btn_h = 60
        bar_y = self.height - btn_h
        bar_bg = pygame.Surface((self.width, btn_h), pygame.SRCALPHA)
        bar_bg.fill((20, 28, 24, 220))
        self.screen.blit(bar_bg, (0, bar_y))

        # Định nghĩa các nút
        touch_btns = [
            {"id": "menu",  "label": "☰",   "color": BMO_DARK_TEAL},
            {"id": "chat",  "label": "💬",   "color": BMO_BLUE},
            {"id": "g1",    "label": "1",    "color": BMO_GREEN},
            {"id": "g2",    "label": "2",    "color": BMO_YELLOW},
            {"id": "g3",    "label": "3",    "color": BMO_HEART_RED},
            {"id": "g4",    "label": "4",    "color": (140, 100, 220)},
        ]
        btn_w = self.width // len(touch_btns)
        font_btn = pygame.font.SysFont("Segoe UI, Arial", 22, bold=True)

        self._mobile_touch_btn_rects = {}
        for i, btn in enumerate(touch_btns):
            bx = i * btn_w
            pygame.draw.rect(self.screen, btn["color"], (bx + 4, bar_y + 4, btn_w - 8, btn_h - 8), border_radius=8)
            pygame.draw.rect(self.screen, BMO_WHITE, (bx + 4, bar_y + 4, btn_w - 8, btn_h - 8), width=2, border_radius=8)
            lbl = font_btn.render(btn["label"], True, BMO_WHITE)
            self.screen.blit(lbl, lbl.get_rect(center=(bx + btn_w // 2, bar_y + btn_h // 2)))
            self._mobile_touch_btn_rects[btn["id"]] = pygame.Rect(bx, bar_y, btn_w, btn_h)

    def _draw_chat_input_bar(self):
        """Vẽ thanh gõ câu hỏi trò chuyện với BMO."""
        bar_h = 75
        bar_y = self.height - bar_h - 15
        bar_w = self.width - 40
        
        # Nền hộp thoại
        bg_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (20, 28, 24, 240), (0, 0, bar_w, bar_h), border_radius=10)
        pygame.draw.rect(bg_surf, BMO_YELLOW, (0, 0, bar_w, bar_h), width=2, border_radius=10)
        self.screen.blit(bg_surf, (20, bar_y))

        # Tiêu đề gợi ý
        prompt_title = "💬 Hỏi BMO (Finn, Jake, Chuyện cười, Kể chuyện, Hát, Football, Hết pin, Nôn băng...):"
        pt_surf = self.font_hint.render(prompt_title, True, BMO_YELLOW)
        self.screen.blit(pt_surf, (35, bar_y + 10))

        # Nội dung đang gõ + Con trỏ nhấp nháy
        cursor_char = "|" if self.chat_cursor_visible else " "
        display_txt = f"> {self.chat_text}{cursor_char}"
        txt_surf = self.font_chat.render(display_txt, True, BMO_WHITE)
        self.screen.blit(txt_surf, (35, bar_y + 36))

        # Gợi ý phím thoát
        esc_surf = self.font_hint.render("[ENTER]: Gửi/Send  |  [ESC]: Hủy", True, (160, 180, 175))
        self.screen.blit(esc_surf, (self.width - 240, bar_y + 10))

    def _draw_settings_screen(self):
        self.screen.fill(BMO_TEAL)
        cx = self.width // 2
        
        # Tiêu đề
        t_surf = self.font_settings.render("⚙️ BMO SYSTEM SETTINGS", True, BMO_BLACK)
        self.screen.blit(t_surf, t_surf.get_rect(center=(cx, 60)))

        settings_list = [
            f"1. Voice Profile: {tts.pitch_modes[tts.pitch_mode_index]['name']} [Press V]",
            f"2. 8-Bit Audio SFX: {'ENABLED' if synth.enabled else 'MUTED'} [Press M]",
            f"3. CRT Scanlines Effect: {'ON' if self.face.show_scanlines else 'OFF'} [Press C]",
            f"4. BMO Handheld Bezel: {'ON' if self.face.show_bezel else 'OFF'} [Press B]",
        ]

        for i, s in enumerate(settings_list):
            py = 140 + i * 55
            pygame.draw.rect(self.screen, (230, 248, 244), (cx - 250, py - 8, 500, 44), border_radius=8)
            pygame.draw.rect(self.screen, BMO_DARK_TEAL, (cx - 250, py - 8, 500, 44), width=2, border_radius=8)
            s_surf = self.font_settings.render(s, True, BMO_BLACK)
            self.screen.blit(s_surf, (cx - 230, py + 4))

        # Phím quay lại
        b_surf = self.font_hint.render("Press [ESC] or [ENTER] to return to BMO", True, (40, 70, 60))
        self.screen.blit(b_surf, b_surf.get_rect(center=(cx, self.height - 50)))

    def _draw_help_screen(self):
        self.screen.fill(BMO_TEAL)
        cx = self.width // 2
        
        # Tiêu đề
        t_surf = self.font_settings.render("❓ BMO MANUAL & KEYBOARD SHORTCUTS", True, BMO_BLACK)
        self.screen.blit(t_surf, t_surf.get_rect(center=(cx, 45)))

        for i, (key, desc) in enumerate(HOTKEYS_INFO):
            py = 90 + i * 36
            # Nút phím
            pygame.draw.rect(self.screen, BMO_YELLOW, (cx - 260, py, 110, 28), border_radius=5)
            pygame.draw.rect(self.screen, BMO_BLACK, (cx - 260, py, 110, 28), width=2, border_radius=5)
            k_surf = self.font_hint.render(key, True, BMO_BLACK)
            self.screen.blit(k_surf, k_surf.get_rect(center=(cx - 205, py + 14)))

            # Mô tả
            d_surf = self.font_hint.render(desc, True, BMO_BLACK)
            self.screen.blit(d_surf, (cx - 130, py + 6))

        # Lời nhắn BMO
        b_surf = self.font_hint.render("Tip: You can click and pet BMO's forehead or cheeks with your mouse! [ESC to Back]", True, (30, 60, 50))
        self.screen.blit(b_surf, b_surf.get_rect(center=(cx, self.height - 35)))
