import serial
import serial.tools.list_ports
import time
from typing import Dict, List, Optional, Union


# Serial settings
BAUDRATE = 115200
TIMEOUT = 1.0  # seconds


class ArduinoController:
    """A class that handles the serial communication between Python and Arduino"""
    def __init__(self):
        self.serial_connection: Optional[serial.Serial] = None
        self.is_connected_flag = False
        self.data_cache: Dict[str, Union[int, float, str, None]] = {}
        self.last_raw_data: str = ""
    
    @staticmethod
    def list_available_ports() -> List[str]:
        """Returns all available COM ports on the system"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def connect(self, port: str, baudrate: int = BAUDRATE) -> bool:
        """Attempts to connect to the Arduino on the specified port"""
        try:
            if self.is_connected_flag:
                self.disconnect()
            
            self.serial_connection = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=TIMEOUT
            )
            
            # Wait for Arduino to reset after connection
            time.sleep(2)
            
            # Clear any initial garbage data
            if self.serial_connection.in_waiting > 0:
                self.serial_connection.read_all()
            
            self.is_connected_flag = True
            print(f"Connected to Arduino on {port} at {baudrate} baud")
            return True
            
        except serial.SerialException as e:
            print(f"Failed to connect to {port}: {e}")
            self.is_connected_flag = False
            return False
        except Exception as e:
            print(f"Unexpected error during connection: {e}")
            self.is_connected_flag = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the Arduino"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Disconnected from Arduino")
        
        self.is_connected_flag = False
        self.serial_connection = None
    
    def is_connected(self) -> bool:
        """Check if currently connected to Arduino"""
        return self.is_connected_flag and \
               self.serial_connection is not None and \
               self.serial_connection.is_open
    
    def read_data(self) -> bool:
        """Read and parse incoming serial data from Arduino
            Example format: label1: value1, label2: value2
            Example input data: temp: 26, humidity: 10"""
        if not self.is_connected():
            return False
        
        try:
            # Check if data is available
            if self.serial_connection.in_waiting > 0:
                raw_line = self.serial_connection.readline()
                decoded_line = raw_line.decode('utf-8', errors='ignore').strip()
                
                if decoded_line:
                    self.last_raw_data = decoded_line
                    self._parse_data(decoded_line) # If any data was read, parse it
                    return True
            
            return False
            
        except serial.SerialException as e:
            print(f"Serial error while reading: {e}")
            self.is_connected_flag = False
            return False
        except Exception as e:
            print(f"Unexpected error while reading: {e}")
            return False
    
    def _parse_data(self, data_line: str) -> None:
        """Parse incoming data and update the cache
            Example format: label1: value1, label2: value2
            Example input data: temp: 26, humidity: 10"""
        try:
            # Parse "label: value" pairs separated by commas
            if ':' in data_line:
                pairs = data_line.split(',')
                for pair in pairs:
                    if ':' in pair:
                        label, value = pair.split(':', 1)
                        label = label.strip()
                        value = value.strip()
                        
                        # Try to convert to appropriate type
                        try:
                            # Try integer first
                            if '.' not in value:
                                self.data_cache[label] = int(value)
                            else:
                                # Try float
                                self.data_cache[label] = float(value)
                        except ValueError:
                            # Keep as string if not a number
                            self.data_cache[label] = value
            
        except Exception as e:
            print(f"Error parsing data '{data_line}': {e}")
    
    def get_value(self, label: str):
        """Get the latest reading for a specific label"""
        return self.data_cache.get(label)
    
    def get_all_values(self):
        """Get all current values"""
        return self.data_cache.copy()
    
    def get_last_raw_data(self) -> str:
        """Get the last raw data string received from Arduino"""
        return self.last_raw_data
    
    def write(self, command: str) -> bool:
        """Send a command/data to the Arduino"""
        if not self.is_connected():
            print("Cannot write: Not connected to Arduino")
            return False
        
        try:
            # Ensure command ends with newline
            if not command.endswith('\n'):
                command += '\n'
            
            # Encode and send
            self.serial_connection.write(command.encode('utf-8'))
            self.serial_connection.flush()
            
            print(f"Sent to Arduino: {command.strip()}")
            return True
            
        except serial.SerialException as e:
            print(f"Serial error while writing: {e}")
            self.is_connected_flag = False
            return False
        except Exception as e:
            print(f"Unexpected error while writing: {e}")
            return False
    
    def __del__(self):
        """Cleanup: ensure serial connection is closed."""
        self.disconnect()


if __name__ == "__main__":
    # List available ports
    print("Available COM ports:")
    ports = ArduinoController.list_available_ports()
    for port in ports:
        print(f"  - {port}")
    
    if not ports:
        print("No COM ports found!")
    else:
        # Try to connect to the first available port
        controller = ArduinoController()
        
        if controller.connect(ports[0]):
            print("\nReading data for 10 seconds...")
            print("Send 'test' command to Arduino after 2 seconds")
            print("(Press Ctrl+C to stop)\n")
            
            try:
                for i in range(100):  # 10 seconds at ~0.1s intervals
                    # Send a test command after 2 seconds
                    if i == 20:
                        controller.write("test")
                    
                    if controller.read_data():
                        print(f"Raw: {controller.get_last_raw_data()}")
                        print(f"Parsed data: {controller.get_all_values()}")
                        print("-" * 60)
                    
                    time.sleep(0.1)
                    
            except KeyboardInterrupt:
                print("\nStopped by user")
            finally:
                controller.disconnect()

