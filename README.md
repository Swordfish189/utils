# Simple Timekeeping Utilities

A cross-platform desktop application that provides a draggable, always-on-top clock and an optional hourly chime. This application is built with the Kivy framework in Python.

## Features

- **Draggable Clock:** A simple, transparent clock that stays on top of other windows.
- **Hourly Chime:** Plays a sound at the top of every hour.
- **Toggleable Features:** Both the clock and the chime can be enabled or disabled through a simple menu.

## Usage

### Prerequisites

- Python 3
- `pip`

### Installation and Running

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python3 main.py
    ```

    *Note: On headless systems or some Linux distributions, you may need to run the application with `xvfb-run` to provide a virtual display server:*
    ```bash
    xvfb-run python3 main.py
    ```
