
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import NumericProperty, ListProperty, BooleanProperty, StringProperty
from kivy.core.text import LabelBase
from kivy.core.audio import SoundLoader
from kivy.metrics import dp
from random import shuffle, randint
import json
import os
from io import BytesIO
import time

# === بارگذاری فونت Aviny ===
AVINY_FONT = 'Aviny.ttf'
if os.path.exists(AVINY_FONT):
    LabelBase.register(name='Aviny', fn_regular=AVINY_FONT)
    DEFAULT_FONT = 'Aviny'
    LANGUAGE = 'fa'
else:
    DEFAULT_FONT = None
    LANGUAGE = 'en'
    print("⚠️ فونت Aviny.ttf یافت نشد. از فونت سیستم و زبان انگلیسی استفاده می‌شود.")

# === تصاویر image1 تا image20 ===
def get_available_images(folder='.', max_count=100):  # ✅ تغییر پیش‌فرض به 100
    images = []
    extensions = ('.png', '.jpg', '.jpeg')
    for i in range(1, max_count + 1):
        for ext in extensions:
            name = f"image{i}{ext}"
            full_path = os.path.join(folder, name)
            if os.path.exists(full_path):
                images.append(name)
                break
    return images if images else ['image1.png', 'image2.png', 'image3.png']

IMAGE_FOLDER = '.'
DEFAULT_IMAGES = get_available_images(IMAGE_FOLDER, max_count=100)  # ✅ تا 100 تصویر

# === فایل‌های ذخیره‌سازی ===
SAVE_FILE = 'puzzle_save.json'
LEADERBOARD_FILE = 'leaderboard.json'

# === صداها ===
click_sound = SoundLoader.load('click.wav') if os.path.exists('click.wav') else None
complete_sound = SoundLoader.load('complete.wav') if os.path.exists('complete.wav') else None
success_sound = complete_sound  # اصلاح تکرار بارگذاری

# === موسیقی پس‌زمینه ===
bg_music = SoundLoader.load('bgm.wav') if os.path.exists('bgm.wav') else None
if bg_music:
    bg_music.volume = 0.4
    bg_music.loop = True

Window.clearcolor = (0.88, 0.96, 0.99, 1)

# === تنظیمات ===
class SettingsManager:
    def __init__(self, filename=SAVE_FILE):
        self.filename = filename
        self.data = {
            'language': LANGUAGE,
            'mode': 'easy',
            'enable_rotation': False,
            'sfx': True,
            'sensitivity': 1.0,
            'last_level': 1
        }
        self.load()
    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                    if DEFAULT_FONT is None:
                        d.pop('language', None)
                    self.data.update(d)
            except Exception:
                pass
    def save(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

settings = SettingsManager()

# === ترجمه ===
def tr(text):
    if LANGUAGE == 'fa':
        t = {
            'Easy Mode': 'حالت آسان',
            'Medium Mode': 'حالت متوسط',
            'Hard Mode': 'حالت سخت',
            'Help': 'راهنما',
            'Settings': 'تنظیمات',
            'Next Level': 'سطح بعدی',
            'Level {} Complete!': 'مرحله {} کامل شد!',
            'How to Play': 'نحوه بازی',
            'Easy Mode Help': 'قطعات را بکشید و در خانهٔ درست رها کنید. چرخشی وجود ندارد.',
            'Hard Mode Help': 'قطعات را جابجا کنید و با ضربه بچرخانید تا درست شوند.',
            'Back': 'بازگشت',
            'Congratulations!': 'تبریک!',
            'Time Up!': 'زمان تمام شد!',
            'Restart': 'شروع دوباره',
            'Preview': 'پیش‌نمایش',
            'Leaderboard': 'رتبه‌بندی',
            'Sound': 'صدا',
            'Sensitivity': 'حساسیت',
            'Select Level': 'انتخاب مرحله',
            'Moves: {}': 'حرکت: {}',
            'Score: {}': 'امتیاز: {}',
        }
        return t.get(text, text)
    return text

# === Puzzle Engine ===
class PuzzleEngine:
    def __init__(self, image_path, grid_size):
        self.image_path = image_path
        self.grid_size = grid_size
        self.texture = None
        self._load_texture()
    def _load_texture(self):
        if os.path.exists(self.image_path):
            from kivy.core.image import Image as CoreImage
            img = CoreImage(self.image_path)
            original_tex = img.texture
            w, h = original_tex.size
            min_dim = min(w, h)
            crop_x = (w - min_dim) // 2
            crop_y = (h - min_dim) // 2
            try:
                self.texture = original_tex.get_region(crop_x, crop_y, min_dim, min_dim)
            except Exception:
                self.texture = original_tex
        else:
            try:
                from PIL import Image as PILImage
                size = 600
                pil = PILImage.new('RGB', (size, size), (randint(50, 200), randint(50, 200), randint(50, 200)))
                bio = BytesIO()
                pil.save(bio, format='PNG')
                bio.seek(0)
                from kivy.core.image import Image as CoreImage
                self.texture = CoreImage(bio, ext='png').texture
            except Exception:
                self.texture = None
    def get_region_texture(self, col, row, patch_size):
        if not self.texture:
            return None
        x = int(col * patch_size)
        y = int(row * patch_size)
        try:
            return self.texture.get_region(x, y, int(patch_size), int(patch_size))
        except Exception:
            return self.texture

# === Puzzle Piece ===
class PuzzlePiece(Widget):
    correct_pos = ListProperty([0, 0])
    grid_pos = ListProperty([0, 0])
    is_locked = BooleanProperty(False)
    rotation_step = NumericProperty(0)
    size_hint = (None, None)
    def __init__(self, texture, size, correct_pos, grid_pos, enable_rotation=False, **kwargs):
        super().__init__(**kwargs)
        self.size = size
        self.correct_pos = list(correct_pos)
        self.grid_pos = list(grid_pos)
        self.enable_rotation = enable_rotation
        self.dragging = False
        self.touch_offset = (0, 0)
        self.img = KivyImage(
    texture=texture,
    size=size,
    size_hint=(None, None),
    allow_stretch=True,
    keep_ratio=False
)
        self.add_widget(self.img)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_graphics, size=self._update_graphics)
        if enable_rotation:
            self.rotation_step = randint(0, 3)
            self.update_visual_rotation()
        else:
            self.rotation_step = 0
    def _update_graphics(self, *a):
        self.img.pos = self.pos
        self.img.size = self.size
    def update_visual_rotation(self):
        self.img.angle = self.rotation_step * 90
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.is_locked:
            self.dragging = True
            self.touch_offset = (touch.x - self.x, touch.y - self.y)
            parent = self.parent
            if parent is not None and self in parent.children:
                parent.remove_widget(self)
                parent.add_widget(self)
            if hasattr(parent.parent, 'increment_move'):
                parent.parent.increment_move()
            return True
        return False
    def on_touch_move(self, touch):
        if self.dragging:
            new_x = touch.x - self.touch_offset[0]
            new_y = touch.y - self.touch_offset[1]
            self.pos = (new_x, new_y)
            return True
        return False
    def on_touch_up(self, touch):
        if self.dragging:
            self.dragging = False
            dx = abs(touch.x - (self.x + self.size[0] / 2))
            dy = abs(touch.y - (self.y + self.size[1] / 2))
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance < dp(10) and self.enable_rotation:
                self.rotation_step = (self.rotation_step + 1) % 4
                self.update_visual_rotation()
                if settings.data.get('sfx', True) and click_sound:
                    click_sound.play()
                self.try_snap()
                return True
            self.try_snap()
            return True
        return False
    def try_snap(self):
        dx = self.correct_pos[0] - self.x
        dy = self.correct_pos[1] - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        sensitivity = settings.data.get('sensitivity', 1.0)
        tolerance = dp(30) * sensitivity  # ✅ استفاده از sensitivity
        correct_rot = (not self.enable_rotation) or (self.rotation_step == 0)
        if dist <= tolerance and correct_rot:
            Animation(x=self.correct_pos[0], y=self.correct_pos[1], d=0.12, t='out_quad').start(self)
            self.is_locked = True
            if settings.data.get('sfx', True) and click_sound:
                click_sound.play()
            current_parent = self.parent
            if current_parent and hasattr(current_parent, 'parent'):
                game = current_parent.parent
                if isinstance(game, PuzzleGame) and hasattr(game, 'locked_layer'):
                    current_parent.remove_widget(self)
                    game.locked_layer.add_widget(self)

# === Puzzle Game ===
class PuzzleGame(Widget):
    level = NumericProperty(1)
    grid_size = NumericProperty(2)
    time_left = NumericProperty(0)
    image_path = StringProperty('')
    score = NumericProperty(0)
    moves = NumericProperty(0)

    def __init__(self, image_paths=None, start_level=1, **kwargs):
        super().__init__(**kwargs)
        self.locked_layer = FloatLayout(size_hint=(1, 1))
        self.unlocked_layer = FloatLayout(size_hint=(1, 1))
        self.add_widget(self.locked_layer)
        self.add_widget(self.unlocked_layer)
        self.image_paths = image_paths or DEFAULT_IMAGES
        self.level = start_level
        self.grid_size = 2
        self.pieces = []
        self.timer_event = None
        self.check_event = None
        self.hud_layout = None
        self.start_time = None
        self.time_label = None
        self.score_label = None
        self.moves_label = None
        Clock.schedule_once(lambda dt: self.load_level())

    def load_level(self, *a):
        # ✅ پاکسازی کامل
        self.clear_widgets()
        self.locked_layer.clear_widgets()
        self.unlocked_layer.clear_widgets()
        self.canvas.before.clear()

        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
        if self.check_event:
            self.check_event.cancel()
            self.check_event = None

        self.pieces.clear()
        self.score = 0
        self.moves = 0
        self.start_time = None

        self.add_widget(self.locked_layer)
        self.add_widget(self.unlocked_layer)

        with self.canvas.before:
            if os.path.exists('bg.jpg'):
                Rectangle(source='bg.jpg', pos=(0, 0), size=Window.size)
            else:
                Color(1, 1, 1, 1)
                Rectangle(pos=(0, 0), size=Window.size)

        idx = (self.level - 1) % len(self.image_paths)
        self.image_path = os.path.join(IMAGE_FOLDER, self.image_paths[idx])
        mode = settings.data.get('mode', 'easy')

        if mode in ('easy', 'medium'):
            self.grid_size = min(5, 2 + (self.level - 1))
        else:
            self.grid_size = min(6, 2 + (self.level - 1))

        enable_rotation = (mode == 'hard')
        settings.data['enable_rotation'] = enable_rotation
        settings.save()

        engine = PuzzleEngine(self.image_path, self.grid_size)
        if not engine.texture:
            self.unlocked_layer.add_widget(Label(text='تصویر بارگذاری نشد', pos_hint={'center_x':0.5,'center_y':0.5}))
            return

        grid_area_size = min(self.width or Window.width, self.height or Window.height) * 0.82
        piece_size_val = grid_area_size / self.grid_size
        piece_size = (piece_size_val, piece_size_val)
        start_x = (Window.width - grid_area_size) / 2
        start_y = (Window.height - grid_area_size) / 2

        correct_positions = [(start_x + col * piece_size_val, start_y + row * piece_size_val)
                             for row in range(self.grid_size) for col in range(self.grid_size)]
        initial_positions = correct_positions[:]
        shuffle(initial_positions)

        patch_size = engine.texture.size[0] / self.grid_size
        for idx, (correct_pos, init_pos) in enumerate(zip(correct_positions, initial_positions)):
            row = idx // self.grid_size
            col = idx % self.grid_size
            tex = engine.get_region_texture(col, row, patch_size)
            piece = PuzzlePiece(texture=tex, size=piece_size, correct_pos=correct_pos,
                                grid_pos=[col, row], enable_rotation=enable_rotation)
            piece.pos = init_pos
            self.unlocked_layer.add_widget(piece)
            self.pieces.append(piece)

        with self.canvas.before:
            Color(0.6, 0.6, 0.6, 0.5)
            Line(rectangle=(start_x, start_y, grid_area_size, grid_area_size), width=2)

        preview_btn = Button(text=tr('Preview'), size_hint=(None, None), size=(dp(90), dp(40)),
                             pos=(dp(10), Window.height - dp(55)))
        preview_btn.bind(on_release=lambda x: self.show_preview())
        self.add_widget(preview_btn)

        # ✅ ساخت HUD
        self.setup_hud(mode)

        # ✅ شروع زمان‌سنج
        if mode in ('medium', 'hard') and self.level >= 5:
            self.time_left = 180 if mode == 'medium' else 150
            self.timer_event = Clock.schedule_interval(self.update_timer, 1.0)
            if self.time_label:
                self.time_label.text = f"{int(self.time_left)}"

        self.check_event = Clock.schedule_interval(self.check_complete, 0.5)
        self.start_time = time.time()

    def setup_hud(self, mode):
        self.hud_layout = FloatLayout(size_hint=(1, None), height=dp(50))
        self.score_label = Label(text=tr('Score: {}').format(self.score), color=(0, 0, 0, 1),
                                 size_hint=(None, None), size=(dp(120), dp(40)),
                                 pos=(dp(10), Window.height - dp(50)))
        self.moves_label = Label(text=tr('Moves: {}').format(self.moves), color=(0, 0, 0, 1),
                                 size_hint=(None, None), size=(dp(120), dp(40)),
                                 pos=(dp(140), Window.height - dp(50)))
        self.add_widget(self.score_label)
        self.add_widget(self.moves_label)

        if mode in ('medium', 'hard') and self.level >= 5:
            self.time_label = Label(
                text=f"{int(self.time_left)}",
                color=(1, 0, 0, 1),
                font_size='22sp',
                size_hint=(None, None),
                size=(dp(60), dp(30)),
                pos=(Window.width - dp(70), Window.height - dp(40))
            )
            self.add_widget(self.time_label)

    def increment_move(self):
        self.moves += 1
        if self.moves_label:
            self.moves_label.text = tr('Moves: {}').format(self.moves)

    def update_timer(self, dt):
        self.time_left -= 1
        if self.time_label:
            self.time_label.text = f"{int(self.time_left)}"
        if self.time_left <= 0:
            self.on_time_up()

    def on_time_up(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
        if self.check_event:
            self.check_event.cancel()
            self.check_event = None
        self.show_popup(tr('Time Up!'), tr('Restart'), self.restart_level)

    def restart_level(self):
        self.load_level()

    def check_complete(self, dt):
        if not self.pieces:
            return
        for p in self.pieces:
            if not p.is_locked:
                return
        if self.check_event:
            self.check_event.cancel()
            self.check_event = None
        if self.timer_event:
            self.timer_event.cancel()
            self.check_event = None
        self.on_level_complete()

    def calculate_score(self):
        base = 1000
        time_bonus = max(0, int(self.time_left) * (10 if settings.data.get('mode') == 'hard' else 5))
        move_penalty = self.moves * 10
        return max(base + time_bonus - move_penalty, 100)

    def on_level_complete(self):
        self.score = self.calculate_score()
        if settings.data.get('sfx', True) and success_sound:
            success_sound.play()
        settings.data['last_level'] = max(settings.data.get('last_level', 1), self.level)
        settings.save()

        self.update_leaderboard(self.score)

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=tr('Level {} Complete!').format(self.level)))
        content.add_widget(Label(text=f"{tr('Score: {}').format(self.score)}"))
        btn = Button(text=tr('Next Level'), size_hint=(1, None), height=dp(40))
        content.add_widget(btn)
        popup = Popup(title=tr('Congratulations!'), content=content, size_hint=(0.8, 0.45), auto_dismiss=False)
        btn.bind(on_release=lambda x: (popup.dismiss(), self.next_level()))
        popup.open()

    def update_leaderboard(self, score):
        board = []
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
                    board = json.load(f)
            except Exception:
                board = []
        board.append({
            'level': self.level,
            'mode': settings.data.get('mode'),
            'score': score,
            'timestamp': int(time.time())
        })
        board.sort(key=lambda x: -x['score'])
        board = board[:100]  # فقط 100 رکورد بالا
        try:
            with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
                json.dump(board, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def next_level(self):
        self.level += 1
        self.load_level()

    def show_preview(self):
        content = FloatLayout()
        if os.path.exists(self.image_path):
            img = KivyImage(source=self.image_path, allow_stretch=True, keep_ratio=True,
                            size_hint=(0.95, 0.95), pos_hint={'center_x':0.5,'center_y':0.5})
        else:
            img = Label(text='(بدون تصویر)')
        content.add_widget(img)
        popup = Popup(title=tr('Preview'), content=content, size_hint=(0.9, 0.9))
        popup.open()

    def show_popup(self, title, msg, callback):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=msg))
        btn = Button(text=tr('Restart'), size_hint=(1, None), height=dp(40))
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4), auto_dismiss=False)
        btn.bind(on_release=lambda x: (popup.dismiss(), callback()))
        popup.open()

# === منوی اصلی — بدون تغییر ===
class MainMenu(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.build_ui())
    def build_ui(self):
        self.clear_widgets()
        with self.canvas.before:
            if os.path.exists('bg.jpg'):
                self.bg_rect = Rectangle(source='bg.jpg', pos=(0, 0), size=Window.size)
            else:
                Color(0.88, 0.96, 0.99, 1)
                self.bg_rect = Rectangle(pos=(0, 0), size=Window.size)
        Window.bind(size=self._update_bg)
        title_text = 'Puzzle IQ' if LANGUAGE == 'en' else 'پازل هوش'
        title = Label(text=title_text, font_size='34sp', pos_hint={'center_x': 0.5, 'top': 0.95})
        if DEFAULT_FONT:
            title.font_name = DEFAULT_FONT
        self.add_widget(title)
        layout = BoxLayout(orientation='vertical', size_hint=(0.8, 0.6), pos_hint={'center_x': 0.5, 'center_y': 0.45}, spacing=12)
        btn_easy = Button(text=tr('Easy Mode'), size_hint=(1, None), height=dp(52))
        btn_medium = Button(text=tr('Medium Mode'), size_hint=(1, None), height=dp(52))
        btn_hard = Button(text=tr('Hard Mode'), size_hint=(1, None), height=dp(52))
        btn_select_level = Button(text=tr('Select Level'), size_hint=(1, None), height=dp(52))
        btn_help = Button(text=tr('Help'), size_hint=(1, None), height=dp(52))
        btn_settings = Button(text=tr('Settings'), size_hint=(1, None), height=dp(52))
        btn_leader = Button(text=tr('Leaderboard'), size_hint=(1, None), height=dp(52))
        layout.add_widget(btn_easy)
        layout.add_widget(btn_medium)
        layout.add_widget(btn_hard)
        layout.add_widget(btn_select_level)
        layout.add_widget(btn_help)
        layout.add_widget(btn_leader)
        layout.add_widget(btn_settings)
        self.add_widget(layout)
        btn_easy.bind(on_release=lambda x: self.start_game('easy'))
        btn_medium.bind(on_release=lambda x: self.start_game('medium'))
        btn_hard.bind(on_release=lambda x: self.start_game('hard'))
        btn_select_level.bind(on_release=lambda x: self.select_level())
        btn_help.bind(on_release=lambda x: self.show_help())
        btn_settings.bind(on_release=lambda x: self.show_settings())
        btn_leader.bind(on_release=lambda x: self.show_leaderboard())
    def _update_bg(self, *args):
        self.bg_rect.pos = (0, 0)
        self.bg_rect.size = Window.size
    def start_game(self, mode):
        settings.data['mode'] = mode
        settings.save()
        if bg_music:
            bg_music.play()
        app = App.get_running_app()
        app.root.clear_widgets()
        pg = PuzzleGame(image_paths=DEFAULT_IMAGES, start_level=settings.data.get('last_level', 1))
        app.root.add_widget(pg)
    def select_level(self):
        content = GridLayout(cols=5, spacing=5, padding=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
    def select_level(self):
        last_unlocked = settings.data.get('last_level', 1)
        max_available = len(DEFAULT_IMAGES)
        # فقط مراحلی که کاربر دسترسی دارد: 1 تا last_unlocked
        levels_to_show = min(last_unlocked, max_available)

        content = GridLayout(cols=5, spacing=5, padding=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        for level in range(1, levels_to_show + 1):
            btn_kwargs = {'text': str(level), 'size_hint_y': None, 'height': dp(40)}
            if DEFAULT_FONT:
                btn_kwargs['font_name'] = DEFAULT_FONT
            btn = Button(**btn_kwargs)
            btn.bind(on_release=lambda x, lvl=level: self.start_level(lvl))
            content.add_widget(btn)

        # نمایش تعداد کل مراحل در دسترس
        total_label = Label(
            text=f"{tr('Unlocked:')} {levels_to_show}/{max_available}",
            size_hint_y=None,
            height=dp(30),
            color=(0, 0, 0, 1)
        )
        scroll = ScrollView(size_hint=(1, 0.75))
        scroll.add_widget(content)

        close_btn = Button(text=tr('Back'), size_hint=(1, None), height=dp(45))
        close_btn.bind(on_release=lambda x: popup.dismiss())

        popup_layout = BoxLayout(orientation='vertical', padding=[10, 0, 10, 10])
        popup_layout.add_widget(scroll)
        popup_layout.add_widget(total_label)
        popup_layout.add_widget(close_btn)

        popup = Popup(title=tr('Select Level'), content=popup_layout, size_hint=(0.9, 0.8))
        popup.open()
    def start_level(self, level):
        settings.data['last_level'] = level
        settings.save()
        if bg_music:
            bg_music.play()
        app = App.get_running_app()
        app.root.clear_widgets()
        pg = PuzzleGame(image_paths=DEFAULT_IMAGES, start_level=level)
        app.root.add_widget(pg)
    def show_help(self):
        mode = settings.data.get('mode', 'easy')
        text = tr('Hard Mode Help') if mode == 'hard' else tr('Easy Mode Help')
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=text))
        btn = Button(text=tr('Back'), size_hint=(1, None), height=dp(40))
        content.add_widget(btn)
        popup = Popup(title=tr('How to Play'), content=content, size_hint=(0.8, 0.5))
        btn.bind(on_release=popup.dismiss)
        popup.open()
    def show_settings(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=8)
        sfx_btn = Button(text=f"{tr('Sound')}: {'On' if settings.data.get('sfx', True) else 'Off'}", size_hint=(1, None), height=dp(42))
        sfx_btn.bind(on_release=lambda x: self.toggle_sfx(x))
        content.add_widget(sfx_btn)
        sens_btn = Button(text=f"{tr('Sensitivity')}: {settings.data.get('sensitivity',1.0):.1f}", size_hint=(1, None), height=dp(42))
        sens_btn.bind(on_release=lambda x: self.adjust_sensitivity())
        content.add_widget(sens_btn)
        close = Button(text=tr('Back'), size_hint=(1, None), height=dp(42))
        content.add_widget(close)
        popup = Popup(title=tr('Settings'), content=content, size_hint=(0.8, 0.5))
        close.bind(on_release=lambda x: (settings.save(), popup.dismiss()))
        popup.open()
    def toggle_sfx(self, btn):
        settings.data['sfx'] = not settings.data.get('sfx', True)
        btn.text = f"{tr('Sound')}: {'On' if settings.data['sfx'] else 'Off'}"
    def adjust_sensitivity(self):
        val = settings.data.get('sensitivity', 1.0)
        val += 0.2
        if val > 1.4:
            val = 0.6
        settings.data['sensitivity'] = round(val, 1)
    def show_leaderboard(self):
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
                    board = json.load(f)
            except Exception:
                board = []
        else:
            board = []
        content = BoxLayout(orientation='vertical', padding=8)
        layout = GridLayout(cols=1, spacing=6, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        if not board:
            layout.add_widget(Label(text='(empty)'))
        else:
            for item in board[:20]:
                layout.add_widget(Label(text=f"L{item.get('level')}-{item.get('mode')} • {item.get('score',0)}"))
        content.add_widget(layout)
        close = Button(text=tr('Back'), size_hint=(1, None), height=dp(40))
        content.add_widget(close)
        popup = Popup(title=tr('Leaderboard'), content=content, size_hint=(0.9, 0.7))
        close.bind(on_release=popup.dismiss)
        popup.open()

# === اپلیکیشن اصلی ===
class PuzzleApp(App):
    def build(self):
        root = FloatLayout()
        root.add_widget(MainMenu())
        return root
    def on_stop(self):
        if bg_music and bg_music.state == 'play':
            bg_music.stop()

if __name__ == '__main__':
    PuzzleApp().run()