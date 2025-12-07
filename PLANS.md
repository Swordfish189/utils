# Application Development Plan

This document tracks the features and progress of the timekeeping utility application.

## Phase 1: Unify Scripts and Core Functionality
- [x] Unify `clock.py` and `hourly.py` into a single application.
- [x] Migrate from `tkinter` to the cross-platform `Kivy` framework.
- [x] Create a main menu to toggle the clock and chime features.
- [x] Implement "always on top" functionality for the clock.
- [x] Implement chime audio feedback on startup and when toggled on.
- [x] Separate the clock into its own floating window.
- [x] Implement "Hover Mode" to hide the menu.

## Phase 2: Customization Features
- [x] Make the clock window resizable.
- [ ] Add a color picker to customize the clock's color.
- [ ] Allow the user to select different chime sounds (from a bundled list or a local file).
- [ ] Allow the user to customize the chime interval.

## Phase 3: Future Goals (Mobile)
- [ ] Plan for deployment to iOS and Android.
