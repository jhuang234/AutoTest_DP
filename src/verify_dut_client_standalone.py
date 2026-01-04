import logging
import sys
from dut_control_client import DutControlClient

# Setup basic logging to console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StandaloneVerification")

def main():
    # 2. Start Client
    # Note: Server IP is currently hardcoded. Modify as needed or add arg parsing for IP.
    client = DutControlClient(server_ip='10.144.217.79', server_port=13000, logger=logger)

    if len(sys.argv) > 1:
        # User provided a custom command via CLI
        # Usage: python verify_dut_client_standalone.py eq 3
        cmd = " ".join(sys.argv[1:])
        logger.info(f"--- Sending Custom Command: '{cmd}' ---")
        resp = client.send_command(cmd)
        print(f"Command '{cmd}' Response: {resp}")
    else:
        # Default Verification Flow
        
        # 3. Test Write
        logger.info("--- Testing Write ---")
        resp = client.write_register(0x7c, 0x02, 0x01)
        print(f"Write Register Response: {resp}")
        if resp == "OK":
            print("PASS: Write Register successful")
        else:
            print("FAIL: Write Register failed")
            
        # 4. Test Custom Command (eq 3)
        # This verifies that we can send strings like 'eq 3' to the server
        logger.info("--- Testing Custom Command (eq 3) ---")
        cmd = "eq 3"
        resp = client.send_command(cmd)
        print(f"Custom Command '{cmd}' Response: {resp}")

if __name__ == "__main__":
    main()
