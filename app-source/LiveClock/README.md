# LiveClock

A simple live clock app for MicroHydra that demonstrates the use of the shared status bar module.

## Features

- **Large Clock Display**: Shows current time in large HH:MM:SS format centered on screen
- **Live Updates**: Updates every second to show current time
- **Status Bar**: Uses the shared status bar showing time and battery level at the top
- **Clean Design**: Minimalist interface using theme colors from MicroHydra config

## Installation

1. Copy the `LiveClock` folder to your device's `/apps` directory
2. Launch from the MicroHydra launcher

## Usage

- The clock will start automatically and display the current time
- Press **G0** button to exit and return to the launcher
- The status bar at the top shows time (HH:MM) and battery level

## Notes

- The app displays time in 24-hour format (HH:MM:SS)
- The status bar shows time in HH:MM format
- Requires device RTC to be set for accurate time (via launcher or NTP)
- This app serves as a simple example of using the shared status bar module

## For Developers

This app demonstrates how to:
- Import and use the shared `StatusBar` class from `lib.hydra.statusbar`
- Combine the status bar with custom app content
- Update the display at regular intervals
- Handle user input for app exit

Example usage:
```python
from lib.hydra.statusbar import StatusBar

# Create status bar instance
status_bar = StatusBar(height=16, use_12h=False)

# In your draw loop
status_bar.draw(display)
display.show()
```

## License

MIT License - See repository LICENSE file for details.
