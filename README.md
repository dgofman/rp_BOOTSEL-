# Raspberry Pi Pico BOOTSEL Mode Utility

This Python utility allows you to reset a **Raspberry Pi Pico** to **BOOTSEL** mode from a host via **USB**, eliminating the need to press the hardware '**BOOTSEL**' button.

The **Raspberry Pi Pico** has a **BOOTSEL** mode, where the board connects to a host via **USB** in device mode. In this mode, the flash storage on the board can be mounted on the host as a **USB** flash drive.

If you encounter any issues while using this utility, please reboot the **Raspberry Pi Pico** by manually pressing the '**BOOTSEL**' button.

### NOTE:
Make sure you are **not** connected to the serial **COM** port via any terminal, such as Putty or the Arduino IDE, before running this script.

**Currently, this utility is only tested on Windows. A version for Mac and Linux will be available soon.**

## Getting Started

### Prerequisites

Before using this utility, ensure that you have the following dependencies installed:

- **Python 3.x** (preferably 3.6 or newer)
- The following Python packages:
  - `pyserial`: for serial communication
  - `psutil`: for managing system resources
  - `pywin32`: for interacting with Windows-specific APIs

To install the required Python packages, run the following command:

```bash
pip install pyserial psutil pywin32
```

## Steps

- Download **flash.py** to your working directory.

- Compile your code.

- Find the resulting **.uf2** file under the **build** folder.

- Run the following command to flash the **.uf2** file to your **Raspberry Pi Pico**:

```bash
python flash.py build/{{FILENAME}}.uf2
```
Example:

```bash
python flash.py build/main.uf2
```
The script will automatically detect the **Raspberry Pi Pico** device, copy the **.uf2** file to the device, and monitor its output if specified.

## Customization

You can customize the script to fit your specific setup by adjusting the following variables:

### Partition Name

- By default, the script looks for the partition named **RPI-RP2**, which is the name used by the Raspberry Pi Pico's BOOTSEL mode.
- If your system assigns a different name to the partition, modify the following line in the script:

```python
partitionName = "RPI-RP2"  # Name of the partition to look for
```

### Serial Baud Rate

- After flashing the .uf2 file, the script can monitor the serial output from the **Raspberry Pi Pico**. If you wish to skip this step, set the serial_baudrate to **None**. Otherwise, update the baud rate to match your configuration.

```python
serial_baudrate = 115200  # Update the baud rate if needed
```

### COM Port Range

- The script allows manual checking for available **COM** ports to connect to the **Raspberry Pi Pico** by setting **comAutoScan to False**. By default, it scans ports from 1 to 15. You can adjust this range by modifying the following lines:

```python
initComPort = 3   # Minimum number of COM ports to check for device
maxComPorts = 15  # Maximum number of COM ports to check for device
```

For faster detection, you can limit the **COM** port range based on your system's configuration. On most **Windows** systems, **COM** ports 5 to 8 are commonly assigned for devices like the **Raspberry Pi Pico**.

## License

This code is open-source and free to use, modify, and distribute under the **MIT License**.

I appreciate any feedback, comments, or bug reports. If you find this utility useful, please consider **giving it a star**!
