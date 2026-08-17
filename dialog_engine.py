"""
BMO Offline Dialogue & Lore Engine
Hệ thống xử lý hội thoại dựa trên luật (Rule-Based NLP), nhận diện ý định và từ khóa
về thế giới Adventure Time, các nhân vật, chuyện cười, giải đố và bài hát.
Hoạt động 100% offline không cần API AI bên ngoài.
"""
import random
import datetime
import unicodedata
from .constants import Expression

def normalize_text(text):
    """Chuẩn hóa văn bản: viết thường, loại bỏ dấu tiếng Việt để so khớp từ khóa linh hoạt."""
    text = text.lower().strip()
    # Loại bỏ dấu
    nfkd_form = unicodedata.normalize('NFKD', text)
    no_accent = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return text, no_accent

class DialogEngine:
    def __init__(self):
        self.joke_index = 0
        self.story_index = 0
        
        # Danh sách chuyện cười của BMO
        self.jokes = [
            ("Why did the computer go to the doctor? Because it had a virus! Beep boop!", Expression.LAUGH, "laugh"),
            ("Tại sao máy tính lại đi khám bác sĩ? Vì nó bị dính virus đó! Haha, BMO nói đùa hay không?", Expression.LAUGH, "laugh"),
            ("What do you call a robot that always takes the longest way? R2-Detour! Yay BMO!", Expression.HAPPY, "coin"),
            ("Finn hỏi BMO: 'BMO ơi pin của cậu ở đâu?'. BMO đáp: 'Bí mật của một cậu bé sống thực thụ không thể tiết lộ!'", Expression.EXCITED, "bloop"),
            ("Knock knock! Who's there? BMO! BMO who? BMO wants to play video games with you forever!", Expression.HEART_EYES, "win")
        ]
        
        # Danh sách câu chuyện ngắn
        self.stories = [
            ("Ngày xửa ngày xưa, ở xứ Ooo, BMO tìm thấy một chiếc tất bị mất tích. BMO quyết định nhận chiếc tất làm thú cưng và đặt tên nó là Ronnie!", Expression.HAPPY, "coin"),
            ("Một buổi sáng nọ, Finn và Jake đi giải cứu công chúa Bubblegum. BMO ở nhà một mình và mở tiệc khiêu vũ bí mật với các quả trứng trong tủ lạnh!", Expression.EXCITED, "win"),
            ("Football nhìn BMO qua chiếc gương phòng tắm và nói: 'BMO, cậu là người bạn tuyệt nhất trần đời!'. Và BMO đã mỉm cười thật tươi!", Expression.FOOTBALL, "bloop"),
            ("Moseph Giovanni đã chế tạo ra hàng ngàn robot dòng MO, nhưng người chỉ tạo ra duy nhất một BMO để 'BE MORE' - Được Yêu Thương nhiều hơn tất cả!", Expression.HEART_EYES, "win")
        ]

    def respond(self, user_input):
        """
        Xử lý câu nhập của người dùng và trả về:
        (reply_text, expression, sound_to_play, special_action)
        """
        if not user_input or not user_input.strip():
            return (
                "BMO is listening! Talk to me or press TAB to open the menu!",
                Expression.HAPPY,
                "bloop",
                None
            )

        orig, raw = normalize_text(user_input)

        # 1. BMO CHOP!
        if any(k in raw for k in ["bmo chop", "chop", "chem", "tan cong", "attack", "fight", "danh nhau"]):
            return (
                "BMO CHOP! If this were a real attack, you would be DEAD!",
                Expression.ANGRY_CHOP,
                "chop",
                "bmo_chop"
            )

        # 2. CHÀO HỎI / GREETINGS
        if any(k in raw for k in ["hello", "hi", "hey", "chao", "xin chao", "chao bmo", "alo", "yo"]):
            greetings = [
                ("Hello! I am BMO! Yay!", Expression.HAPPY, "chirp"),
                ("Chào bạn! BMO rất vui được gặp bạn hôm nay!", Expression.HAPPY, "coin"),
                ("Hi there! Who wants to play video games?", Expression.EXCITED, "win"),
                ("Chào người bạn tuyệt vời của BMO!", Expression.HEART_EYES, "chirp")
            ]
            reply, expr, snd = random.choice(greetings)
            return (reply, expr, snd, None)

        # 3. BẠN LÀ AI? / WHO ARE YOU?
        if any(k in raw for k in ["ban la ai", "who are you", "gioi thieu", "ten gi", "what is your name", "bmo la ai"]):
            return (
                "I am BMO! A living robotic boy, a game console, camera, music player, and Finn and Jake's best friend!",
                Expression.HAPPY,
                "win",
                None
            )

        # 4. FINN THE HUMAN
        if any(k in raw for k in ["finn", "finn the human", "cau be finn"]):
            return (
                "Finn is a brave hero with a golden heart! He always protects everyone with his trusty sword!",
                Expression.EXCITED,
                "coin",
                None
            )

        # 5. JAKE THE DOG
        if any(k in raw for k in ["jake", "jake the dog", "chu cho jake"]):
            return (
                "Jake is Finn's magical stretchy brother! He makes the best Bacon Pancakes in all of Ooo!",
                Expression.HAPPY,
                "bloop",
                None
            )

        # 6. PRINCESS BUBBLEGUM
        if any(k in raw for k in ["bubblegum", "cong chua keo cao su", "bonnibel", "pb"]):
            return (
                "Princess Bubblegum is super smart! She built the entire Candy Kingdom with science!",
                Expression.HAPPY,
                "chirp",
                None
            )

        # 7. MARCELINE
        if any(k in raw for k in ["marceline", "vampire", "ma ca rong"]):
            return (
                "Marceline the Vampire Queen plays the bass guitar! She does not drink blood, only the color red!",
                Expression.SHOCKED,
                "laser",
                None
            )

        # 8. ICE KING / SIMON
        if any(k in raw for k in ["ice king", "vua bang", "simon", "gunter"]):
            return (
                "Ice King can be silly and lonely, but he really loves penguins! Gunter goes Wenk Wenk!",
                Expression.SURPRISED,
                "bloop",
                None
            )

        # 9. FOOTBALL / GƯƠNG
        if any(k in raw for k in ["football", "bong da", "guong", "mirror"]):
            return (
                "Football is my secret best friend in the mirror! Shhh, don't tell anyone, Football is shy!",
                Expression.FOOTBALL,
                "chirp",
                "football_mode"
            )

        # 10. MOE / NGƯỜI TẠO RA BMO
        if any(k in raw for k in ["moe", "moseph", "ai tao ra ban", "who made you", "nguoi sang che"]):
            return (
                "Moseph Giovanni made me at the MO Co factory! He designed BMO to Be More and experience love!",
                Expression.HEART_EYES,
                "win",
                None
            )

        # 11. HÁT MỘT BÀI / SING A SONG
        if any(k in raw for k in ["sing", "hat", "bai hat", "song", "ca hat", "hat di"]):
            songs = [
                ("Time is an illusion that helps things make sense! So we are always living in the present tense!", Expression.SINGING, "win"),
                ("Bacon pancakes, makin' bacon pancakes! Take some bacon and I'll put it in a pancake!", Expression.SINGING, "coin"),
                ("Adventure Time, come on grab your friends! We'll go to very distant lands!", Expression.SINGING, "win")
            ]
            reply, expr, snd = random.choice(songs)
            return (reply, expr, snd, "play_theme")

        # 12. KỂ CHUYỆN CƯỜI / TELL A JOKE
        if any(k in raw for k in ["joke", "chuyen cuoi", "ke chuyen cuoi", "hai huoc", "vui"]):
            joke_data = self.jokes[self.joke_index % len(self.jokes)]
            self.joke_index += 1
            return (joke_data[0], joke_data[1], joke_data[2], None)

        # 13. KỂ MỘT CÂU CHUYỆN / TELL A STORY
        if any(k in raw for k in ["story", "ke chuyen", "chuyen co tich", "tell me a story"]):
            story_data = self.stories[self.story_index % len(self.stories)]
            self.story_index += 1
            return (story_data[0], story_data[1], story_data[2], None)

        # 14. BẠN CÓ KHỎE KHÔNG? / HOW ARE YOU?
        if any(k in raw for k in ["khoe khong", "how are you", "tam trang", "the nao"]):
            return (
                "BMO's battery is fully charged and my heart is warm! How are you doing today?",
                Expression.HAPPY,
                "chirp",
                None
            )

        # 15. TÂM SỰ BUỒN / VUI
        if any(k in raw for k in ["buon", "sad", "unhappy", "khoc", "met"]):
            return (
                "Don't be sad! When bad things happen, I know you want to believe they're a joke, but sometimes life is scary and dark. That is why we must find the light together!",
                Expression.SAD,
                "bloop",
                None
            )
        if any(k in raw for k in ["vui", "happy", "tuyet", "great", "awesome", "yeu ban", "love you", "i love you"]):
            return (
                "Yay! BMO loves you so much! You are my favorite human friend!",
                Expression.HEART_EYES,
                "win",
                None
            )

        # 16. HỎI GIỜ / THỜI GIAN
        if any(k in raw for k in ["may gio", "what time", "gio", "thoi gian", "time"]):
            now_str = datetime.datetime.now().strftime("%H:%M")
            return (
                f"It is {now_str}! And you know what time it really is? It's ADVENTURE TIME!",
                Expression.EXCITED,
                "coin",
                None
            )

        # 17. HỎI NGÀY THÁNG
        if any(k in raw for k in ["ngay may", "what date", "hom nay", "today"]):
            date_str = datetime.datetime.now().strftime("%d/%m/%Y")
            return (
                f"Today is {date_str}! Another wonderful day in the Land of Ooo!",
                Expression.HAPPY,
                "chirp",
                None
            )

        # 18. CHƠI MINI-GAMES QUA LỆNH CHAT
        if any(k in raw for k in ["choi game", "play game", "mini game", "video game"]):
            return (
                "Yay! Press keys 1 to 4 or press ESC/TAB to choose a retro mini-game from the Menu!",
                Expression.EXCITED,
                "win",
                "open_games_menu"
            )
        if "runner" in raw or "chop" in raw and "game" in raw:
            return ("Launching BMO Chop Runner!", Expression.EXCITED, "jump", "start_game_runner")
        if "bug" in raw or "space" in raw or "bo" in raw:
            return ("Launching Bug Catcher!", Expression.EXCITED, "laser", "start_game_bugs")
        if "simon" in raw or "memory" in raw:
            return ("Launching Chiptune Simon Memory!", Expression.EXCITED, "coin", "start_game_simon")
        if "rainicorn" in raw or "bay" in raw:
            return ("Launching Lady Rainicorn Sky Flap!", Expression.EXCITED, "win", "start_game_rainicorn")

        # 19. ĐỔI BIỂU CẢM QUA LỆNH
        if "vui" in raw or "happy" in raw:
            return ("BMO is super happy!", Expression.HAPPY, "chirp", None)
        if "cuoi" in raw or "laugh" in raw:
            return ("Hehehe haha!", Expression.LAUGH, "laugh", None)
        if "ngu" in raw or "sleep" in raw:
            return ("BMO is getting sleepy... Zzz...", Expression.SLEEPY, "bloop", None)
        if "ngac nhien" in raw or "shock" in raw:
            return ("Whoa! What was that?!", Expression.SHOCKED, "laser", None)
        if "glitch" in raw or "loi" in raw:
            return ("01000010 01001101 01001111 GLITCH!", Expression.GLITCH, "hit", None)

        # 20. CÂU TRẢ LỜI MẶC ĐỊNH THÂN THIỆN
        fallback_responses = [
            ("Yay BMO! I heard you say that! Tell me more or let's play a game!", Expression.HAPPY, "chirp"),
            ("That is fascinating! Did you know robots can feel happiness too?", Expression.EXCITED, "coin"),
            ("Hehe! You are so fun to talk to! Ask me about Finn, Jake, or ask for a joke!", Expression.HAPPY, "bloop"),
            ("BMO computes 100% friendship with you! Beep boop!", Expression.HEART_EYES, "chirp")
        ]
        fb_text, fb_expr, fb_snd = random.choice(fallback_responses)
        return (fb_text, fb_expr, fb_snd, None)

# Khởi tạo instance dùng chung
dialog_engine = DialogEngine()
