import json
import os
import re

# Defaults provided by user
# Format: address -> value
NEW_DEFAULTS = {
    0x18: 0xEE,
    0x15: 0x00,
    0x16: 0xC3,
    0x2c: 0xEE,
    0x2a: 0xC3,
    0x40: 0xEE,
    0x3e: 0xC3,
    0x54: 0xEE,
    0x52: 0xC3,
    0x1a: 0x53,
    0x2e: 0x53,
    0x42: 0x53,
    0x56: 0x53
}

def parse_register_cmd(cmd):
    """
    Returns (address, value) if strictly a write_register on 0x7c.
    Otherwise None.
    """
    # Pattern: write_register(0x7c, 0x15, 0x01)
    # Flexible on spacing
    match = re.search(r'write_register\(\s*0x7c\s*,\s*(0x[0-9a-fA-F]+)\s*,\s*(0x[0-9a-fA-F]+)\s*\)', cmd)
    if match:
        addr = int(match.group(1), 16)
        val = int(match.group(2), 16)
        return addr, val
    return None

def main():
    config_path = 'batch_config.json'
    if not os.path.exists(config_path):
        print("Config file not found.")
        return

    with open(config_path, 'r') as f:
        data = json.load(f)

    updated_count = 0

    for run in data.get("runs", []):
        commands = run.get("dut_commands", [])
        # We iterate and modify in place if needed
        # Structure is [Cmd, Comment, Cmd, Comment...] ideally for the default valued ones.
        
        for i in range(len(commands)):
            cmd = commands[i]
            # Check if this line is the comment marker
            if cmd == "//default value":
                # Look at previous command
                if i > 0:
                    prev_cmd = commands[i-1]
                    # Parse it
                    parsed = parse_register_cmd(prev_cmd)
                    if parsed:
                        addr, current_val = parsed
                        if addr in NEW_DEFAULTS:
                            new_val = NEW_DEFAULTS[addr]
                            if new_val != current_val:
                                # Update the command string
                                new_cmd_str = f"write_register(0x7c, 0x{addr:02X}, 0x{new_val:02X})"
                                commands[i-1] = new_cmd_str
                                print(f"Run '{run['name']}': Updated {prev_cmd} -> {new_cmd_str}")
                                updated_count += 1

    if updated_count > 0:
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Updates saved. Total variables updated: {updated_count}")
    else:
        print("No matching default values needed update.")

if __name__ == "__main__":
    main()
