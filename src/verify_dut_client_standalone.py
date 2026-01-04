import logging
import sys
from dut_control_client import DutControlClient

# Setup basic logging to console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StandaloneVerification")

def main():
    # 2. Start Client
    client = DutControlClient(server_ip='10.144.217.79', server_port=13000, logger=logger)
    
    # 3. Test Write
    logger.info("--- Testing Write ---")
    resp = client.write_register(0x7c, 0x02, 0x01)
    print(f"Write Register Response: {resp}")
    if resp == "OK":
        print("PASS: Write Register successful")
    else:
        print("FAIL: Write Register failed")

if __name__ == "__main__":
    main()
