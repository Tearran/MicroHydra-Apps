"""
IMU Live Readout - MicroHydra App

Displays live accelerometer and gyroscope data from MPU-family IMU sensors.
Shows accel X/Y/Z (g), gyro X/Y/Z (deg/s), and computed pitch/roll angles.

Auto-detects MPU sensors at I2C addresses 0x68 or 0x69.
Uses the shared status bar for time and battery display.
"""

import time
import math
from machine import Pin, I2C, reset

from lib.display import Display
from lib.hydra.config import Config
from lib.hydra.statusbar import StatusBar
from lib.userinput import UserInput
from font import vga1_8x16 as font


# MPU register addresses (common for MPU6050/MPU6500 family)
MPU_PWR_MGMT_1 = 0x6B
MPU_ACCEL_XOUT_H = 0x3B
MPU_GYRO_XOUT_H = 0x43

# MPU I2C addresses to try
MPU_ADDRESSES = [0x68, 0x69]

# I2C timeout in microseconds (8ms = 8000us, allows time for slow I2C transactions)
I2C_TIMEOUT_US = 8000

# Scale factors (assuming default config: ±2g accel, ±250deg/s gyro)
ACCEL_SCALE = 16384.0  # LSB/g for ±2g range
GYRO_SCALE = 131.0     # LSB/(deg/s) for ±250deg/s range

# Display constants
MAX_ERROR_CHARS = 28  # Maximum characters for error message to fit on screen


class MPUReader:
    """Simple MPU-family IMU reader."""
    
    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address
        self._buffer = bytearray(14)
        
        # Wake up the MPU (set PWR_MGMT_1 to 0)
        try:
            self.i2c.writeto_mem(self.address, MPU_PWR_MGMT_1, bytes([0x00]))
            time.sleep_ms(100)  # Wait for sensor to wake up
        except Exception as e:
            raise RuntimeError(f"Failed to initialize MPU: {e}")
    
    def read_raw_data(self):
        """Read raw accel and gyro data from MPU registers."""
        try:
            # Read 14 bytes starting from ACCEL_XOUT_H
            # Format: ACCEL_X_H, ACCEL_X_L, ACCEL_Y_H, ACCEL_Y_L, ACCEL_Z_H, ACCEL_Z_L,
            #         TEMP_H, TEMP_L, GYRO_X_H, GYRO_X_L, GYRO_Y_H, GYRO_Y_L, GYRO_Z_H, GYRO_Z_L
            self.i2c.readfrom_mem_into(self.address, MPU_ACCEL_XOUT_H, self._buffer)
            
            # Convert to signed 16-bit integers
            accel_x = self._bytes_to_int16(self._buffer[0], self._buffer[1])
            accel_y = self._bytes_to_int16(self._buffer[2], self._buffer[3])
            accel_z = self._bytes_to_int16(self._buffer[4], self._buffer[5])
            
            gyro_x = self._bytes_to_int16(self._buffer[8], self._buffer[9])
            gyro_y = self._bytes_to_int16(self._buffer[10], self._buffer[11])
            gyro_z = self._bytes_to_int16(self._buffer[12], self._buffer[13])
            
            return accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z
        except Exception as e:
            return None
    
    @staticmethod
    def _bytes_to_int16(high_byte, low_byte):
        """Convert two bytes to signed 16-bit integer."""
        value = (high_byte << 8) | low_byte
        if value >= 0x8000:  # If negative (two's complement)
            value -= 0x10000
        return value
    
    def read_scaled_data(self):
        """Read and scale accel (g) and gyro (deg/s) data."""
        raw = self.read_raw_data()
        if raw is None:
            return None
        
        accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z = raw
        
        # Scale to physical units
        ax = accel_x / ACCEL_SCALE
        ay = accel_y / ACCEL_SCALE
        az = accel_z / ACCEL_SCALE
        
        gx = gyro_x / GYRO_SCALE
        gy = gyro_y / GYRO_SCALE
        gz = gyro_z / GYRO_SCALE
        
        return ax, ay, az, gx, gy, gz


def compute_pitch_roll(ax, ay, az):
    """
    Compute pitch and roll from accelerometer data.
    
    Simple calculation assuming static or slowly moving sensor.
    Returns (pitch, roll) in degrees.
    """
    try:
        # Pitch: rotation around X axis
        pitch = math.atan2(ay, math.sqrt(ax * ax + az * az)) * 180.0 / math.pi
        
        # Roll: rotation around Y axis
        roll = math.atan2(-ax, az) * 180.0 / math.pi
        
        return pitch, roll
    except Exception:
        return 0.0, 0.0


def try_init_imu():
    """Try to initialize IMU on standard Cardputer I2C pins."""
    # Initialize I2C with Cardputer pins (SDA=2, SCL=1)
    try:
        i2c = I2C(0, sda=Pin(2), scl=Pin(1), freq=100000, timeout=I2C_TIMEOUT_US)
    except Exception as e:
        return None, f"I2C init failed: {e}"
    
    # Scan for devices
    try:
        devices = i2c.scan()
    except Exception as e:
        return None, f"I2C scan failed: {e}"
    
    if not devices:
        return None, "No I2C devices found"
    
    # Try to initialize MPU at known addresses
    for addr in MPU_ADDRESSES:
        if addr in devices:
            try:
                mpu = MPUReader(i2c, addr)
                return mpu, None
            except Exception as e:
                continue
    
    # Found devices but no MPU
    device_list = ", ".join([f"0x{d:02X}" for d in devices])
    return None, f"No MPU found. Devices: {device_list}"


def main():
    """Main app loop."""
    # Initialize display and config
    display = Display()
    config = Config()
    kb = UserInput()
    
    # Initialize status bar
    status_bar = StatusBar(height=16, use_12h=False)
    
    # Colors from config
    bg_color = config.palette[2]
    fg_color = config.palette[0]
    highlight_color = config.palette[10]
    
    # Try to initialize IMU
    display.fill(bg_color)
    status_bar.draw(display)
    display.text("Initializing IMU...", 5, 20, fg_color, font=font)
    display.show()
    
    mpu, error = try_init_imu()
    
    if mpu is None:
        # Display error and wait for exit
        display.fill(bg_color)
        status_bar.draw(display)
        display.text("IMU Error:", 5, 20, highlight_color, font=font)
        display.text(error[:MAX_ERROR_CHARS], 5, 40, fg_color, font=font)
        display.text("Press G0 to exit", 5, 100, fg_color, font=font)
        display.show()
        
        while True:
            keys = kb.get_new_keys()
            if "G0" in keys:
                reset()
            time.sleep_ms(50)
    
    # Main loop - display IMU data
    y_offset = status_bar.height + 4
    
    while True:
        # Check for exit
        keys = kb.get_new_keys()
        if "G0" in keys:
            reset()
        
        # Read IMU data
        data = mpu.read_scaled_data()
        
        if data is not None:
            ax, ay, az, gx, gy, gz = data
            pitch, roll = compute_pitch_roll(ax, ay, az)
            
            # Clear display (except status bar)
            display.fill_rect(0, status_bar.height, display.width, 
                            display.height - status_bar.height, bg_color)
            
            # Draw status bar
            status_bar.draw(display)
            
            # Display data
            line_height = 16
            y = y_offset
            
            display.text("Accelerometer (g):", 5, y, highlight_color, font=font)
            y += line_height
            display.text(f" X: {ax:6.2f}", 5, y, fg_color, font=font)
            y += line_height
            display.text(f" Y: {ay:6.2f}", 5, y, fg_color, font=font)
            y += line_height
            display.text(f" Z: {az:6.2f}", 5, y, fg_color, font=font)
            
            # Second column for gyro
            y = y_offset
            x2 = 130
            display.text("Gyro (deg/s):", x2, y, highlight_color, font=font)
            y += line_height
            display.text(f"X:{gx:6.1f}", x2, y, fg_color, font=font)
            y += line_height
            display.text(f"Y:{gy:6.1f}", x2, y, fg_color, font=font)
            y += line_height
            display.text(f"Z:{gz:6.1f}", x2, y, fg_color, font=font)
            
            # Orientation at bottom
            y = display.height - line_height * 2 - 2
            display.text(f"Pitch: {pitch:6.1f} deg", 5, y, highlight_color, font=font)
            y += line_height
            display.text(f"Roll:  {roll:6.1f} deg", 5, y, highlight_color, font=font)
            
        else:
            # Read error
            display.fill_rect(0, status_bar.height, display.width,
                            display.height - status_bar.height, bg_color)
            status_bar.draw(display)
            display.text("Read error!", 5, y_offset, highlight_color, font=font)
        
        display.show()
        time.sleep_ms(100)  # Update at ~10 Hz


if __name__ == "__main__":
    main()
