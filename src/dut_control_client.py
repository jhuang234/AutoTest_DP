import socket
import logging

class DutControlClient:
    def __init__(self, server_ip, server_port, logger=None):
        self.server_ip = server_ip
        self.server_port = server_port
        self.logger = logger if logger else logging.getLogger("DutControlClient")

    def send_command(self, command):
        """Sends a raw string command to the server."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5) # 5 seconds timeout
                #self.logger.debug(f"Connecting to {self.server_ip}:{self.server_port}...")
                s.connect((self.server_ip, self.server_port))
                
                #self.logger.debug(f"Sending command: {command}")
                s.sendall(command.encode('utf-8'))
                
                response = s.recv(1024).decode('utf-8')
                #self.logger.debug(f"Received response: {response}")
                return response
        except ConnectionRefusedError:
            self.logger.error(f"Connection refused to {self.server_ip}:{self.server_port}")
            return None
        except socket.timeout:
            self.logger.error("Connection timed out.")
            return None
        except Exception as e:
            self.logger.error(f"Error sending command: {e}")
            return None

    def write_register(self, slave_addr, reg_offset, value):
        """
        Sends a write command.
        Format: "write <slave_addr> <reg_offset> <value>"
        All inputs should be integers or hex strings.
        """
        # Ensure format is 2-digit hex
        if isinstance(slave_addr, int): slave_addr = f"{slave_addr:02x}"
        if isinstance(reg_offset, int): reg_offset = f"{reg_offset:02x}"
        if isinstance(value, int): value = f"{value:02x}"
        
        command = f"write {slave_addr} {reg_offset} {value}"
        self.logger.info(f"Writing Register: {command}")
        return self.send_command(command)

    def read_register(self, slave_addr, reg_offset):
        """
        Sends a read command.
        Format: "read <slave_addr> <reg_offset>"
        """
        if isinstance(slave_addr, int): slave_addr = f"{slave_addr:02x}"
        if isinstance(reg_offset, int): reg_offset = f"{reg_offset:02x}"
        
        command = f"read {slave_addr} {reg_offset}"
        self.logger.info(f"Reading Register: {command}")
        return self.send_command(command)

    def set_dp_mode(self):
        """
        Helper command to switch to DP mode based on user requirement:
        'dpaddr' command to set a DP I2C slave address.
        """
        # Assuming 'dpaddr' is implemented on server or we mimic it
        # Based on spec: "dpaddr command to set a DP I2C slave address... effectively switching the system into 'DP mode'"
        # But this might be from previous conversation context, spec.txt says:
        # "Parameter Sweep... use i2c write slave address..."
        # I will implement a generic 'dpaddr' wrapper just in case.
        return self.send_command("dpaddr")
