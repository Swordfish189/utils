import tkinter as tk
import time


class TransparentClock(tk.Tk):
    def __init__(self):
        super().__init__()

        # Remove window border and title bar
        self.overrideredirect(True)

        # Keep the window always on top
        self.wm_attributes("-topmost", True)

        # Set the window background color (the same color used for transparency)
        self.config(bg="black")

        # Make the chosen background color transparent
        self.wm_attributes("-transparentcolor", "black")

        # Create a label to display the clock
        self.label = tk.Label(
            self,
            text="",
            font=("Consolas", 20),  # "Courier New", "Lucida Console", etc.
            fg="lime",  # Hacker green color
            bg="black",  # Must match the window's background for transparency
        )
        self.label.pack(padx=10, pady=10)

        # Create a resize handle
        self.resize_handle = tk.Frame(self, width=10, height=10, bg="lime", cursor="sizing")
        self.resize_handle.place(relx=1.0, rely=1.0, anchor="se")

        # Enable dragging the window by clicking on the label
        self.label.bind("<Button-1>", self.start_move)
        self.label.bind("<B1-Motion>", self.do_move)

        # Enable resizing by clicking on the handle
        self.resize_handle.bind("<Button-1>", self.start_resize)
        self.resize_handle.bind("<B1-Motion>", self.do_resize)

        # Start updating the clock
        self.update_clock()

    def update_clock(self):
        """Update the clock label every second."""
        current_time = time.strftime("%H:%M:%S")
        self.label.config(text=current_time)
        self.after(1000, self.update_clock)

    def start_move(self, event):
        """Remember the offset when a left-click starts."""
        self.click_x = event.x
        self.click_y = event.y

    def do_move(self, event):
        """Move the window based on mouse drag."""
        x = self.winfo_pointerx() - self.click_x
        y = self.winfo_pointery() - self.click_y
        self.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        """Remember the initial size and position when a resize starts."""
        self.start_width = self.winfo_width()
        self.start_height = self.winfo_height()
        self.start_x = event.x_root
        self.start_y = event.y_root

    def do_resize(self, event):
        """Resize the window proportionally based on mouse drag."""
        delta_x = event.x_root - self.start_x
        new_width = self.start_width + delta_x

        # Enforce minimum and maximum size
        min_width = 50
        max_width = 1920
        new_width = max(min_width, min(new_width, max_width))

        # Calculate proportional height
        aspect_ratio = self.start_height / self.start_width
        new_height = int(new_width * aspect_ratio)

        self.geometry(f"{new_width}x{new_height}")

        # Scale the font size
        new_font_size = int(new_width / 10) # Adjust the divisor for best results
        self.label.config(font=("Consolas", new_font_size))


if __name__ == "__main__":
    TransparentClock().mainloop()
