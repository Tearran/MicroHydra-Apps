# IMU Live Readout

A MicroHydra app that displays live IMU (Inertial Measurement Unit) sensor data from MPU-family accelerometer and gyroscope sensors.

## Features

- **Live Data Display**: Shows real-time readings from accelerometer and gyroscope
- **Computed Orientation**: Calculates pitch and roll angles from accelerometer data
- **Auto-Detection**: Automatically detects MPU sensors at I2C addresses 0x68 or 0x69
- **Status Bar**: Uses the shared status bar showing time and battery level
- **Clear Feedback**: Displays helpful messages if no IMU sensor is found

## Data Shown

- **Accel X/Y/Z**: Acceleration in g (gravitational units)
- **Gyro X/Y/Z**: Angular velocity in deg/s (degrees per second)
- **Pitch**: Rotation around X axis (computed from accelerometer)
- **Roll**: Rotation around Y axis (computed from accelerometer)

## Hardware Requirements

- M5Stack Cardputer (or compatible MicroHydra device)
- MPU-family IMU sensor (MPU6050, MPU6500, or compatible)
- I2C connection: SDA=Pin 2, SCL=Pin 1 (Cardputer standard)

## Installation

1. Copy the `IMU_Live` folder to your device's `/apps` directory
2. Ensure your IMU sensor is connected via I2C
3. Launch from the MicroHydra launcher

## Usage

- The app will automatically detect and initialize the IMU sensor
- If no sensor is found, a clear message will be displayed
- Press **G0** button to exit and return to the launcher
- The status bar at the top shows current time and battery level

## Notes

- Time display requires the device RTC to be set (via launcher or NTP)
- Pitch/roll are computed from accelerometer only (simple calculation)
- For more accurate orientation, sensor fusion algorithms would be needed
- The driver uses standard MPU register mapping and assumes default scales

## Troubleshooting

If the sensor is not detected:
1. Check I2C connections (SDA=Pin 2, SCL=Pin 1 for Cardputer)
2. Verify your sensor is an MPU6050/MPU6500 compatible device
3. Try using a different I2C address (0x68 or 0x69)
4. Check sensor power supply

If readings seem incorrect:
- Ensure the sensor is properly calibrated
- Check that the sensor is mounted correctly
- Verify the sensor scale settings match expectations

## License

MIT License - See repository LICENSE file for details.
