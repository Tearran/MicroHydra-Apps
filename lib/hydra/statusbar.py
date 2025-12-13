"""
Shared status bar module for MicroHydra apps.

Provides a launcher-style top toolbar that shows time and battery status.
Can be imported by any app with: from lib.hydra.statusbar import StatusBar
"""

import time


class StatusBar:
    """
    A reusable status bar component that draws a compact top toolbar.
    
    Shows time (HH:MM) on the left and battery level on the right,
    using Config.palette colors. Caches last drawn values to reduce flicker.
    
    Args:
        height: Height of the status bar in pixels (default 16)
        use_12h: If True, use 12-hour format; if False, use 24-hour (default False)
    """
    
    def __init__(self, height=16, use_12h=False):
        self.height = height
        self.use_12h = use_12h
        self._last_time_str = ""
        self._last_batt_level = -1
        self._battery = None
        self._battery_icon = None
        
        # Try to import battery module
        try:
            from lib import battlevel
            self._battery = battlevel.Battery()
        except (ImportError, Exception):
            self._battery = None
        
        # Try to import battery icon
        try:
            from launcher.icons import battery
            self._battery_icon = battery
        except (ImportError, Exception):
            self._battery_icon = None
    
    def draw(self, tft):
        """
        Draw the status bar on the given display.
        
        Args:
            tft: Display object with drawing methods (lib.display.Display)
        """
        try:
            from lib.hydra.config import Config
            config = Config()
            bg_color = config.palette[1]
            fg_color = config.palette[0]
        except (ImportError, Exception):
            # Fallback colors if config not available
            bg_color = 0x0000  # black
            fg_color = 0xFFFF  # white
        
        # Get current time
        try:
            current_time = time.localtime()
            hour = current_time[3]
            minute = current_time[4]
            
            if self.use_12h:
                # Convert to 12-hour format
                if hour == 0:
                    hour = 12
                elif hour > 12:
                    hour -= 12
            
            time_str = f"{hour:02d}:{minute:02d}"
        except Exception:
            time_str = "--:--"
        
        # Only redraw time if it changed
        if time_str != self._last_time_str:
            # Clear time area
            tft.fill_rect(0, 0, 60, self.height, bg_color)
            # Draw time text
            try:
                from font import vga1_8x16 as small_font
                tft.text(time_str, 2, 0, fg_color, font=small_font)
            except ImportError:
                # Fallback to default font if available
                tft.text(time_str, 2, 2, fg_color)
            
            self._last_time_str = time_str
        
        # Get battery level
        try:
            if self._battery:
                batt_level = self._battery.read_level()
            else:
                batt_level = -1
        except Exception:
            batt_level = -1
        
        # Only redraw battery if it changed
        if batt_level != self._last_batt_level:
            # Battery area is on the right side
            batt_x = tft.width - 30
            
            # Clear battery area
            tft.fill_rect(batt_x, 0, 30, self.height, bg_color)
            
            # Draw battery indicator
            if batt_level >= 0 and self._battery_icon:
                # Use battery icon
                try:
                    icon_x = tft.width - 20
                    icon_y = 2
                    tft.bitmap(self._battery_icon, icon_x, icon_y, 
                              palette=(bg_color, fg_color), index=batt_level)
                except Exception:
                    # Fallback to text
                    batt_text = f"{batt_level}%"
                    tft.text(batt_text, batt_x + 2, 2, fg_color)
            elif batt_level >= 0:
                # Use text percentage
                batt_text = f"{batt_level}%"
                try:
                    from font import vga1_8x8 as tiny_font
                    tft.text(batt_text, batt_x + 2, 4, fg_color, font=tiny_font)
                except ImportError:
                    tft.text(batt_text, batt_x + 2, 2, fg_color)
            
            self._last_batt_level = batt_level
