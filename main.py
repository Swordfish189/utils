import time
import datetime
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.config import Config
from kivy.graphics import Color, Rectangle
from kivy.uix.behaviors import DragBehavior

# --- Configuration ---
Config.set('graphics', 'borderless', 1)
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'always_on_top', 1)
Config.set('graphics', 'resizable', 1)

class DraggableResizableBoxLayout(DragBehavior, BoxLayout):
    """ A draggable and resizable BoxLayout. """
    def __init__(self, **kwargs):
        super(DraggableResizableBoxLayout, self).__init__(**kwargs)
        self.resize_border = 15
        self._resizing = False
        self._resize_dir = None
        self.drag_timeout = 10000000
        self.drag_distance = 0
        self.is_clock = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.is_clock and App.get_running_app().is_hover_mode and touch.button == 'right':
                App.get_running_app().toggle_hover_mode()
                return True

            x, y = touch.pos
            if abs(x - self.x) < self.resize_border or \
               abs(x - self.right) < self.resize_border or \
               abs(y - self.y) < self.resize_border or \
               abs(y - self.top) < self.resize_border:

                if abs(x - self.x) < self.resize_border: self._resize_dir = 'left'
                elif abs(x - self.right) < self.resize_border: self._resize_dir = 'right'
                elif abs(y - self.y) < self.resize_border: self._resize_dir = 'bottom'
                else: self._resize_dir = 'top'

                self._resizing = True
                return True

            return super(DraggableResizableBoxLayout, self).on_touch_down(touch)

        return False

    def on_touch_move(self, touch):
        if self._resizing:
            if self._resize_dir == 'right': self.width = max(50, touch.x - self.x)
            elif self._resize_dir == 'left':
                self.width = max(50, self.right - touch.x)
                self.x = touch.x
            elif self._resize_dir == 'top': self.height = max(50, touch.y - self.y)
            elif self._resize_dir == 'bottom':
                self.height = max(50, self.top - touch.y)
                self.y = touch.y
            return True
        return super(DraggableResizableBoxLayout, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self._resizing:
            self._resizing = False
            self._resize_dir = None
            return True
        return super(DraggableResizableBoxLayout, self).on_touch_up(touch)

class ClockApp(App):
    def build(self):
        """Build the main application widget."""
        Window.clearcolor = (0, 0, 0, 0)
        self.is_hover_mode = False
        self.saved_window_size = (Window.width, Window.height)
        self.saved_clock_pos = (0, 0)

        self.root_layout = FloatLayout()

        # --- Clock Widget ---
        self.clock_widget = DraggableResizableBoxLayout(
            orientation='vertical', size_hint=(None, None), size=(250, 80), pos=(100, 300)
        )
        self.clock_widget.is_clock = True
        self.clock_label = Label(text=time.strftime("%H:%M:%S"), bold=True, color=(0, 1, 0, 1))
        self.clock_widget.add_widget(self.clock_label)
        self.clock_widget.bind(size=self.update_font_size)
        self.root_layout.add_widget(self.clock_widget)

        # --- Menu Widget ---
        self.menu_widget = DraggableResizableBoxLayout(
            orientation='vertical', size_hint=(None, None), size=(250, 150), pos=(400, 300),
            spacing=5, padding=10
        )
        with self.menu_widget.canvas.before:
            Color(0.1, 0.1, 0.1, 0.8)
            self.menu_bg = Rectangle(size=self.menu_widget.size, pos=self.menu_widget.pos)
        self.menu_widget.bind(pos=lambda i,p: setattr(self.menu_bg, 'pos', p),
                              size=lambda i,s: setattr(self.menu_bg, 'size', s))

        # Toggles & Button
        self.setup_menu_widgets()

        self.root_layout.add_widget(self.menu_widget)

        self.update_font_size()
        return self.root_layout

    def setup_menu_widgets(self):
        clock_toggle = BoxLayout(orientation='horizontal')
        clock_toggle.add_widget(Label(text='Show Clock', color=(1,1,1,1)))
        self.clock_checkbox = CheckBox(active=True)
        self.clock_checkbox.bind(active=self.toggle_clock_visibility)
        clock_toggle.add_widget(self.clock_checkbox)
        self.menu_widget.add_widget(clock_toggle)

        chime_toggle = BoxLayout(orientation='horizontal')
        chime_toggle.add_widget(Label(text='Enable Chime', color=(1,1,1,1)))
        self.chime_checkbox = CheckBox(active=True)
        self.chime_checkbox.bind(active=self.toggle_chime)
        chime_toggle.add_widget(self.chime_checkbox)
        self.menu_widget.add_widget(chime_toggle)

        hover_button = Button(text='Hover')
        hover_button.bind(on_press=lambda x: self.toggle_hover_mode())
        self.menu_widget.add_widget(hover_button)

    def toggle_hover_mode(self):
        if not self.is_hover_mode:
            # Enter Hover Mode
            self.is_hover_mode = True
            self.saved_window_size = Window.size
            self.saved_clock_pos = self.clock_widget.pos
            self.root_layout.remove_widget(self.menu_widget)
            Window.size = self.clock_widget.size
            self.clock_widget.pos = (0,0)
        else:
            # Exit Hover Mode
            self.is_hover_mode = False
            Window.size = self.saved_window_size
            self.clock_widget.pos = self.saved_clock_pos
            self.root_layout.add_widget(self.menu_widget)

    def update_font_size(self, *args):
        self.clock_label.font_size = self.clock_widget.height * 0.6

    def on_start(self):
        Clock.schedule_interval(self.update_clock, 1)
        self.sound = SoundLoader.load('bell.wav')
        self.chime_event = None
        if self.chime_checkbox.active:
            self.play_chime_sound()
            self.toggle_chime(None, True)

    def update_clock(self, *args):
        self.clock_label.text = time.strftime("%H:%M:%S")

    def toggle_clock_visibility(self, checkbox, value):
        self.clock_widget.opacity = 1 if value else 0

    def toggle_chime(self, checkbox, value):
        if value and not self.chime_event:
            self.play_chime_sound()
            self.schedule_first_chime()
        elif not value and self.chime_event:
            self.chime_event.cancel()
            self.chime_event = None
            print("Hourly chime disabled.")

    def schedule_first_chime(self):
        now = datetime.datetime.now()
        next_hour = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
        seconds_until = (next_hour - now).total_seconds()

        print(f"Next chime in {seconds_until:.2f} seconds.")
        self.chime_event = Clock.schedule_once(self.start_hourly_chime, seconds_until)

    def start_hourly_chime(self, *args):
        self.play_chime_sound()
        self.chime_event = Clock.schedule_interval(self.play_chime_sound, 3600)

    def play_chime_sound(self, *args):
        print(f"Chime at {datetime.datetime.now().strftime('%H:%M:%S')}")
        if self.sound:
            self.sound.play()

if __name__ == '__main__':
    ClockApp().run()
