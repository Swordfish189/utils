import time
import datetime
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.config import Config

# --- Configuration ---
Config.set('graphics', 'borderless', 1)
Config.set('graphics', 'width', '300')
Config.set('graphics', 'height', '150')
Config.set('graphics', 'always_on_top', 1)

class DraggableLabel(Label):
    """ A custom Label widget that can be dragged to move the window. """
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.ud['click_x'] = Window.left - touch.x
            touch.ud['click_y'] = Window.top - touch.y
            return True
        return super(DraggableLabel, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if 'click_x' in touch.ud:
            Window.left = touch.x + touch.ud['click_x']
            Window.top = touch.y + touch.ud['click_y']
            return True
        return super(DraggableLabel, self).on_touch_move(touch)

class ClockApp(App):
    def build(self):
        """Build the main application widget."""
        Window.clearcolor = (0, 0, 0, 0.5)

        # --- Main Layout ---
        self.root_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # --- Clock Widget ---
        self.clock_label = DraggableLabel(
            text=time.strftime("%H:%M:%S"),
            font_size='30sp',
            bold=True,
            color=(0, 1, 0, 1)
        )
        self.root_layout.add_widget(self.clock_label)

        # --- Menu Layout ---
        menu_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)

        # Clock Toggle
        menu_layout.add_widget(Label(text='Show Clock'))
        self.clock_checkbox = CheckBox(active=True)
        self.clock_checkbox.bind(active=self.toggle_clock_visibility)
        menu_layout.add_widget(self.clock_checkbox)

        # Chime Toggle
        menu_layout.add_widget(Label(text='Enable Chime'))
        self.chime_checkbox = CheckBox(active=True)
        self.chime_checkbox.bind(active=self.toggle_chime)
        menu_layout.add_widget(self.chime_checkbox)

        self.root_layout.add_widget(menu_layout)
        return self.root_layout

    def on_start(self):
        """Called after the application window is created."""
        Clock.schedule_interval(self.update_clock, 1)
        self.sound = SoundLoader.load('bell.wav')
        self.chime_event = None
        if self.chime_checkbox.active:
            self.toggle_chime(None, True)

    def update_clock(self, *args):
        """Updates the clock label with the current time."""
        self.clock_label.text = time.strftime("%H:%M:%S")

    def toggle_clock_visibility(self, checkbox, value):
        """Shows or hides the clock label."""
        self.clock_label.opacity = 1 if value else 0

    def toggle_chime(self, checkbox, value):
        """Enables or disables the hourly chime."""
        if value:
            if not self.chime_event:
                self.schedule_first_chime()
        else:
            if self.chime_event:
                self.chime_event.cancel()
                self.chime_event = None
                print("Hourly chime disabled.")

    def schedule_first_chime(self):
        """Calculates the time until the next hour and schedules the first chime."""
        now = datetime.datetime.now()
        next_hour = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
        seconds_until = (next_hour - now).total_seconds()

        print(f"Next chime scheduled in {seconds_until:.2f} seconds.")
        self.chime_event = Clock.schedule_once(self.start_hourly_chime, seconds_until)

    def start_hourly_chime(self, *args):
        """Plays the first chime and schedules the recurring hourly chime."""
        self.play_chime_sound()
        # Schedule the chime to run every hour (3600 seconds) from now on.
        # This creates only one recurring event.
        self.chime_event = Clock.schedule_interval(self.play_chime_sound, 3600)

    def play_chime_sound(self, *args):
        """Plays the chime sound."""
        print(f"Chime played at {datetime.datetime.now().strftime('%H:%M:%S')}")
        if self.sound:
            self.sound.play()

if __name__ == '__main__':
    ClockApp().run()
