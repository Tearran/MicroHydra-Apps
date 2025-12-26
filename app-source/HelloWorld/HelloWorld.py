"""Hello World App for MicroHydra.

A simple application that displays "Hello World" on the screen
and exits back to the main launcher when the GO or ENT key is pressed.

Author: MicroHydra Community
Version: 1.0
"""

from lib.display import Display
from lib.userinput import UserInput
from machine import reset

# Initialize display
display = Display()

# Initialize user input
kb = UserInput()

# Clear the screen and display "Hello World"
display.fill(0x0000)  # Black background
display.text("Hello World", 80, 60, 0xFFFF)  # White text, centered
display.show()

# Main loop - wait for GO or ENT key press
while True:
    keys = kb.get_new_keys()
    
    if keys:
        # Check for GO or ENT key to exit
        if "GO" in keys or "ENT" in keys:
            reset()
