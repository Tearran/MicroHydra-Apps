"""
LiveClock - Simple Live Clock App for MicroHydra

Displays a large live clock (HH:MM:SS) in the center of the screen.
Uses the shared status bar to show time and battery at the top.

Demonstrates usage of the lib.hydra.statusbar module.
"""

import time
from machine import reset

from lib.display import Display
from lib.hydra.config import Config
from lib.hydra.statusbar import StatusBar
from lib.userinput import UserInput
from font import vga2_16x32 as large_font
from font import vga1_8x16 as medium_font


def main():
    """Main clock app loop."""
    # Initialize display and config
    display = Display()
    config = Config()
    kb = UserInput()
    
    # Initialize status bar (16px high, 24-hour format)
    status_bar = StatusBar(height=16, use_12h=False)
    
    # Colors from config
    bg_color = config.palette[2]
    fg_color = config.palette[0]
    clock_color = config.palette[10]
    
    last_time_str = ""
    
    while True:
        # Check for exit
        keys = kb.get_new_keys()
        if "G0" in keys:
            reset()
        
        # Get current time
        try:
            current_time = time.localtime()
            hour = current_time[3]
            minute = current_time[4]
            second = current_time[5]
            time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
        except Exception:
            time_str = "--:--:--"
        
        # Only update display if time changed
        if time_str != last_time_str:
            # Clear main area (below status bar)
            display.fill_rect(0, status_bar.height, display.width,
                            display.height - status_bar.height, bg_color)
            
            # Draw status bar at top
            status_bar.draw(display)
            
            # Calculate position to center the large clock
            # Large font is 16x32, time string is 8 chars = 128px wide
            time_width = len(time_str) * 16
            clock_x = (display.width - time_width) // 2
            
            # Center vertically in remaining space below status bar
            available_height = display.height - status_bar.height
            clock_y = status_bar.height + (available_height - 32) // 2
            
            # Draw the large clock
            display.text(time_str, clock_x, clock_y, clock_color, font=large_font)
            
            # Add a small label
            label = "Press G0 to exit"
            label_width = len(label) * 8
            label_x = (display.width - label_width) // 2
            label_y = display.height - 20
            display.text(label, label_x, label_y, fg_color, font=medium_font)
            
            # Update display
            display.show()
            
            last_time_str = time_str
        
        # Sleep for a short time before checking again
        time.sleep_ms(100)


if __name__ == "__main__":
    main()
