import os
import re
import time
import shutil
import sys
import shelve
import winreg
import subprocess
import serial # pip install pyserial
import psutil # pip install psutil
import win32api # pip install pywin32

# Define the serial communication baudrate and other constants
serial_baudrate = 115200 
raspberryPiVID = "VID_2E8A" # Unique to Raspberry Pi Ltd.
raspberryPiPID =  "PID_0004" # USB-to-UART bridges on Raspberry Pi boards.
partitionName = "RPI-RP2"  # Name of the partition to look for
initComPort = 3   # Minimum number of COM ports to check for device
maxComPorts = 15  # Maximum number of COM ports to check for device
comAutoScan = True # Auto scan COM ports

# Shelve storage to remember the last used COM port
storage_name = "flash_partition_shelve"
storage_key = "comPort"

def find_rpi_rp2_drive():
    """
    This function looks for the 'RPI-RP2' partition by checking all mounted partitions
    and returns the device associated with it, if found.
    """
    partitions = psutil.disk_partitions()

    # Loop through all partitions and check for the correct volume label
    for partition in partitions:
        volume_label = win32api.GetVolumeInformation(partition.device)[0]
        if partitionName == volume_label:
            print(f"The '{partitionName}' drive is mounted at: {partition.device}")
            return partition.device
    
    return None

def get_com_and_partition(comPort):
    savePort = None
    """Check if the given COM port is associated with a Raspberry Pi device using PowerShell."""
    command = f'Get-WmiObject -Class Win32_PnPEntity | Where-Object {{$_.Name -match "{comPort}"}} | Format-List PNPDeviceID'
    result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
    if raspberryPiVID in result.stdout:
        savePort = comPort

    try:
        print(f"Opening serial connection on {comPort} ...")
        serial.Serial(f"{comPort}", 1200, timeout=1)
    except:
        # If the COM port cannot be opened, wait for 3 seconds before retrying
        time.sleep(3)

    # Try to find the RPI-RP2 drive partition
    partition = find_rpi_rp2_drive()
    if partition:
        # Store the COM port in shelve storage for later use
        with shelve.open(storage_name) as db:
            db[storage_key] = savePort
        return [comPort, partition]

def is_raspberry_pi_com():
    command = f"""
    $raspberryPiVID = "{raspberryPiVID}"
    Get-WmiObject -Class Win32_PnPEntity | Where-Object {{ $_.PNPClass -eq "Ports" }} | ForEach-Object {{
        if ($_.DeviceID -match $raspberryPiVID) {{
            Write-Output $_.Name
        }}
    }}
    """
    try:
        # Execute PowerShell command
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)
        out = result.stdout.strip()
        match = re.search(r"COM(\d+)", out)
        if match:
            port = match.group(1)
            data = get_com_and_partition(f'COM{port}')
            if data:
                return data
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

def find_raspberry_pi_com():
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM") as key:
            i = 0
            while True:
                try:
                    # Enumerate each value under the key
                    _, port, _ = winreg.EnumValue(key, i)
                    data = get_com_and_partition(port)
                    if data:
                        return data
                    i += 1
                except OSError:
                    # No more values to enumerate
                    break
    except FileNotFoundError:
        print("Registry key not found.")
    return None

def wait_for_device_reconnect():
    """
    This function waits for the Raspberry Pi Pico to reconnect by attempting to open
    serial connections on different COM ports within the range.
    """
    print("Waiting for Raspberry Pi Pico to reconnect...")
    if comAutoScan:
        data = is_raspberry_pi_com() or find_raspberry_pi_com()
        if data:
            return data

    # Try to find the device by opening serial connections on each COM port
    for port in range(initComPort, maxComPorts + 1):
        data = get_com_and_partition(f'COM{port}')
        if data:
            return data
    return None

def copyFile(partition):
    """
    This function copies a file (specified in command-line arguments) to the given partition.
    It also checks if the file exists and prints the file size before copying.
    """
    file_path = sys.argv[1]
    try:
        # Get the file size and print it
        file_size = os.path.getsize(file_path)
        print(f"Copying file {file_path} to {partition}. File size: {file_size} bytes")
        
        # Copy the file to the RPI-RP2 device
        shutil.copy(file_path, partition)
        print("File copied successfully.")
        print(f"Wait connecting to {partition} ({partitionName}) ...")
        time.sleep(5)
    except Exception as e:
        # If an error occurs during file copy, print the error
        print(f"Error copying file: {e}")
            

def read_com(comPort):
    """
    This function opens a serial connection on the specified COM port and continuously 
    reads data from the serial interface, printing the received data.
    """
    if serial_baudrate is None:
        sys.exit(0)

    try:
        print(f"Opening serial connection on {comPort} ...")
        ser = serial.Serial(comPort, serial_baudrate, timeout=1)
        # Read data from the serial port
        while True:
            try:
                # Try to read a line of data (assuming the data ends with a newline character)
                data = ser.readline()
                if data:
                    print(data.decode('utf-8').strip())  # Print the received data after decoding it
            except:
                # Ctrl+C, exit the loop
                sys.exit(0)
    except Exception as e:
        # If there is an error opening the serial port, print the exception
        print(e)

# Main function to handle the logic of connecting to the Raspberry Pi Pico and copying files
def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if not os.path.exists(file_path):
            print(f"Error: The file '{file_path}' does not exist. Please check the path and try again.")
            sys.exit(1)
    else:
        print("Error: No file argument provided. Please provide the file path as an argument.")
        sys.exit(2)

    # Open shelve storage to get the last used COM port
    with shelve.open(storage_name) as db:
        comPort = db.get(storage_key, None)

    # Attempt to find the RPI-RP2 partition on the system
    partition = find_rpi_rp2_drive()
    if partition:
        # If the partition is found, copy the file to it
        copyFile(partition)
        
        # If we have a stored COM port, try reading data from the serial port
        if comPort:
            read_com(comPort)
    else:
        print("No partitions found.")

    # If no partition was found earlier, try to get the device again
    data = None
    if comPort:
        data = get_com_and_partition(comPort)
    
    if not data:
        # Wait for the device to reconnect if no data was found
        data = wait_for_device_reconnect()

    if data:
        # If a connection was established, proceed with the file copy and serial communication
        comPort, partition = data
        copyFile(partition)
        print("Connecting to Raspberry Pi Pico...")
        read_com(comPort)

    print("Could not establish connection to the Raspberry Pi Pico.")

# Execute the main function
if __name__ == "__main__":
    main()
