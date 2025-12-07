import time
import datetime
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.config import Config
from kivy.graphics import Color, Rectangle

# --- Configuration ---
Config.set('graphics', 'borderless', 1)
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'always_on_top', 1)
Config.set('graphics', 'resizable', 1)

class DraggableWidget(BoxLayout):
    """ A custom draggable widget. """
    def __init__(self, **kwargs):
        super(DraggableWidget, self).__init__(**kwargs)
        self._touch_pos = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_pos = touch.pos
            return True
        return super(DraggableWidget, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._touch_pos:
            dx = touch.x - self._touch_pos[0]
            dy = touch.y - self._touch_pos[1]
            self.pos = (self.pos[0] + dx, self.pos[1] + dy)
            return True
        return super(DraggableWidget, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self._touch_pos:
            self._touch_pos = None
            return True
        return super(DraggableWidget, self).on_touch_up(touch)

class ResizableDraggableWidget(DraggableWidget):
    """ A draggable widget that can also be resized. """
    def __init__(self, **kwargs):
        super(ResizableDraggableWidget, self).__init__(**kwargs)
        self.resize_border = 15
        self._resizing = False
        self._resize_dir = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            x, y = touch.pos
            # Check if touch is on a border for resizing
            if abs(x - self.x) < self.resize_border:
                self._resize_dir = 'left'
            elif abs(x - self.right) < self.resize_border:
                self._resize_dir = 'right'
            elif abs(y - self.y) < self.resize_border:
                self._resize_dir = 'bottom'
            elif abs(y - self.top) < self.resize_border:
                self._resize_dir = 'top'
            else:
                self._resize_dir = None

            if self._resize_dir:
                self._resizing = True
                return True

        return super(ResizableDraggableWidget, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._resizing:
            if self._resize_dir == 'right':
                self.width = max(50, touch.x - self.x)
            elif self._resize_dir == 'left':
                self.width = max(50, self.right - touch.x)
                self.x = touch.x
            elif self._resize_dir == 'top':
                self.height = max(50, touch.y - self.y)
            elif self._resize_dir == 'bottom':
                self.height = max(50, self.top - touch.y)
                self.y = touch.y
            return True
        return super(ResizableDraggableWidget, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self._resizing:
            self._resizing = False
            self._resize_dir = None
            return True
        return super(ResizableDraggableWidget, self).on_touch_up(touch)

class ClockApp(App):
    def build(self):
        """Build the main application widget."""
        Window.clearcolor = (0, 0, 0, 0) # Fully transparent background

        root_layout = FloatLayout()

        # --- Clock Widget ---
        self.clock_widget = ResizableDraggableWidget(
            orientation='vertical',
            size_hint=(None, None),
            size=(250, 80),
            pos=(100, 300)
        )
        self.clock_label = Label(
            text=time.strftime("%H:%M:%S"),
            bold=True,
            color=(0, 1, 0, 1)
        )
        self.clock_widget.add_widget(self.clock_label)
        self.clock_widget.bind(size=self.update_font_size)
        root_layout.add_widget(self.clock_widget)

        # --- Menu Widget ---
        self.menu_widget = DraggableWidget(
            orientation='vertical',
            size_hint=(None, None),
            size=(250, 100),
            pos=(400, 300),
            spacing=5,
            padding=10
        )
        with self.menu_widget.canvas.before:
            Color(0.1, 0.1, 0.1, 0.8)
            self.menu_bg = Rectangle(size=self.menu_widget.size, pos=self.menu_widget.pos)
        self.menu_widget.bind(pos=lambda i,p: setattr(self.menu_bg, 'pos', p),
                              size=lambda i,s: setattr(self.menu_bg, 'size', s))

        # Clock Toggle
        clock_toggle = BoxLayout(orientation='horizontal')
        clock_toggle.add_widget(Label(text='Show Clock', color=(1,1,1,1)))
        self.clock_checkbox = CheckBox(active=True)
        self.clock_checkbox.bind(active=self.toggle_clock_visibility)
        clock_toggle.add_widget(self.clock_checkbox)
        self.menu_widget.add_widget(clock_toggle)

        # Chime Toggle
        chime_toggle = BoxLayout(orientation='horizontal')
        chime_toggle.add_widget(Label(text='Enable Chime', color=(1,1,1,1)))
        self.chime_checkbox = CheckBox(active=True)
        self.chime_checkbox.bind(active=self.toggle_chime)
        chime_toggle.add_widget(self.chime_checkbox)
        self.menu_widget.add_widget(chime_toggle)

        root_layout.add_widget(self.menu_widget)

        self.update_font_size() # Initial font size
        return root_layout

    def update_font_size(self, *args):
        # Adjust font size based on the widget's height
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
