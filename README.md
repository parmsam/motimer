# motimer

An anywidget timer and stopwatch built for [marimo](https://marimo.io/) notebooks. Useful for productivity, time management, trainings, and interactive demos.

## Features

- **Timer Widget**: Countdown timer with customizable duration and audio alerts
- **Stopwatch Widget**: Precision stopwatch with start, stop, and reset functionality  
- **Multiple Themes**: Light, dark, and auto themes to match your environment
- **Interactive Controls**: Easy-to-use buttons with modern UI design
- **Real-time Updates**: Live synchronization between widget state and Python variables
- **Seamless Integration**: Built as anywidgets for smooth marimo notebook integration

## Installation

```bash
pip install motimer

# Or install from Github repository (development version)
pip install git+https://github.com/parmsam/motimer.git
```

## Usage

### Timer Widget

![](https://github.com/parmsam/motimer/raw/main/images/result_timer.jpg)

```python
import marimo as mo
from motimer import TimerWidget

# Create a timer with default 5-minute duration
timer = TimerWidget()
timer_ui = mo.ui.anywidget(timer)

# Or set a custom initial time (10 minutes = 600 seconds)
timer = TimerWidget(initial_time=600)
timer_ui = mo.ui.anywidget(timer)

# Set time programmatically
timer.set_time(hours=0, minutes=2, seconds=30)

# Set theme
timer.theme = 'dark'  # 'light', 'dark', or 'auto'

# Display the widget
timer_ui
```

### Stopwatch Widget

![](https://github.com/parmsam/motimer/raw/main/images/result_stopwatch.jpg)

```python
import marimo as mo
from motimer import StopwatchWidget

# Create and display a stopwatch
stopwatch = StopwatchWidget()
stopwatch.theme = 'light'  # 'light', 'dark', or 'auto'
stopwatch_ui = mo.ui.anywidget(stopwatch)

# Display the widget
stopwatch_ui
```

### Accessing Widget State

You can access the current state of both widgets from Python:

```python
# Timer state
mo.md(f"""
**Timer Status:**
- Time remaining: {timer.remaining_time // 60}m {timer.remaining_time % 60}s
- Is running: {timer.is_running}
- Timer finished: {'Yes' if timer.remaining_time == 0 and not timer.is_running else 'No'}
""")

# Stopwatch state  
mo.md(f"""
**Stopwatch Status:**
- Elapsed time: {stopwatch.elapsed_time / 1000:.2f} seconds
- Is running: {stopwatch.is_running}
""")
```

## Widget Features

### Timer Widget
- **Customizable Duration**: Set initial time via constructor or `set_time()` method
- **Audio Alerts**: Plays a beep sound when timer reaches zero
- **Visual Feedback**: Modern gradient design with smooth animations
- **Theme Support**: Adapts to light/dark themes
- **Python Integration**: Access remaining time and running state from Python

### Stopwatch Widget  
- **High Precision**: Tracks time in milliseconds with centisecond display
- **Start/Stop/Reset**: Full control over timing operations
- **Real-time Updates**: Smooth 10ms update intervals for precise timing
- **State Synchronization**: Elapsed time and running state accessible from Python
- **Theme Support**: Matches your preferred color scheme

## API Reference

### TimerWidget

```python
TimerWidget(initial_time=300)  # 300 seconds = 5 minutes default

# Properties
timer.remaining_time  # int: remaining seconds
timer.is_running      # bool: whether timer is active
timer.initial_time    # int: initial duration in seconds
timer.theme          # str: 'light', 'dark', or 'auto'

# Methods
timer.set_time(hours=0, minutes=5, seconds=0)  # Set timer duration
```

### StopwatchWidget

```python
StopwatchWidget()

# Properties  
stopwatch.elapsed_time  # int: elapsed time in milliseconds
stopwatch.is_running    # bool: whether stopwatch is active
stopwatch.last_updated  # float: timestamp of last update
stopwatch.theme        # str: 'light', 'dark', or 'auto'
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*Built with ❤️ using [marimo](https://marimo.io/) and [anywidget](https://anywidget.dev/)*