import socket
import sys
import logging
import threading

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("DutControlServer")

# --- MOCK DRIVER ---
# In a real scenario, this would import the USB-I2C driver DLL or Python wrapper.
class MockI2CDriver:
    def write(self, slave_addr, reg_offset, val):
        logger.info(f"[DRIVER] Write I2C: Slave=0x{slave_addr:02x}, Reg=0x{reg_offset:02x}, Val=0x{val:02x}")
        return True

    def read(self, slave_addr, reg_offset):
        logger.info(f"[DRIVER] Read I2C: Slave=0x{slave_addr:02x}, Reg=0x{reg_offset:02x}")
        return 0x00 # Mock return value

driver = MockI2CDriver()

# --- SERVER LOGIC ---

def handle_client(conn, addr):
    logger.info(f"Connected by {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            command = data.decode('utf-8').strip()
            logger.info(f"Received: {command}")
            
            response = process_command(command)
            conn.sendall(response.encode('utf-8'))
    logger.info(f"Connection closed by {addr}")

def process_command(cmd_str):
    """
    Parses command string and executes it.
    Supported:
    - write <addr_hex> <off_hex> <val_hex>
    - read <addr_hex> <off_hex>
    """
    try:
        parts = cmd_str.split()
        if not parts: return "Error: Empty command"
        
        op = parts[0].lower()
        
        if op == "write":
            # write 7c 02 01
            if len(parts) != 4: return "Error: Usage 'write <addr> <reg> <val>'"
            addr = int(parts[1], 16)
            reg = int(parts[2], 16)
            val = int(parts[3], 16)
            success = driver.write(addr, reg, val)
            return "OK" if success else "Fail"
            
        elif op == "read":
            # read 7c 02
            if len(parts) != 3: return "Error: Usage 'read <addr> <reg>'"
            addr = int(parts[1], 16)
            reg = int(parts[2], 16)
            val = driver.read(addr, reg)
            return f"0x{val:02x}"
            
        else:
            return f"Error: Unknown command '{op}'"
            
    except ValueError as e:
        return f"Error: Invalid number format ({e})"
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return f"Error: {e}"

def start_server(host='0.0.0.0', port=13000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        logger.info(f"Server listening on {host}:{port}")
        
        # Simple single-threaded accept loop for now (or multi-threaded if needed)
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

if __name__ == "__main__":
    start_server()
