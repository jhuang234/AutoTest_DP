import json
import os

def parse_register_cmd(cmd):
    """
    Parses a dut_command string.
    Returns (address, value, full_command_string) if it's a valid write_register command.
    Returns None otherwise.
    """
    if not isinstance(cmd, str):
        return None
    # Ignore comments
    if cmd.strip().startswith("//") or cmd.strip().startswith("#"):
        return None
    
    # Check for write_register
    if "write_register" not in cmd:
        return None
    
    try:
        # Expected format: "write_register(0x7c, 0x15, 0x01)"
        if '(' in cmd and ')' in cmd:
            args_part = cmd.split('(')[1].split(')')[0]
            args = [x.strip() for x in args_part.split(',')]
            if len(args) == 3:
                addr = int(args[1], 16)
                val = int(args[2], 16)
                return addr, val, cmd
    except Exception as e:
        pass
    
    return None

def main():
    config_path = 'batch_config.json'
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found.")
        return

    with open(config_path, 'r') as f:
        data = json.load(f)

    if "runs" not in data:
        print("No 'runs' found in config.")
        return

    runs = data["runs"]
    
    # 1. Find the reference run (the one with the most write_register commands)
    max_reg_count = -1
    ref_run = None
    ref_regs_map = {} # addr -> full_command_string (from reference run)

    for run in runs:
        cmds = run.get("dut_commands", [])
        reg_map = {} # addr -> cmd
        for cmd in cmds:
            parsed = parse_register_cmd(cmd)
            if parsed:
                addr, val, full_cmd = parsed
                reg_map[addr] = full_cmd
        
        if len(reg_map) > max_reg_count:
            max_reg_count = len(reg_map)
            ref_run = run
            ref_regs_map = reg_map

    if not ref_run:
        print("No runs with write_register commands found.")
        return

    print(f"Reference Run found: '{ref_run['name']}' with {max_reg_count} register writes.")

    # 2. Normalize other runs
    runs_updated = 0
    for run in runs:
        if run is ref_run:
            continue
            
        cmds = run.get("dut_commands", [])
        
        # Identify existing registers
        existing_addrs = set()
        last_reg_index = -1
        
        for i, cmd in enumerate(cmds):
            parsed = parse_register_cmd(cmd)
            if parsed:
                existing_addrs.add(parsed[0])
                last_reg_index = i
        
        # Determine missing commands
        missing_entries = [] # List of (command_string, comment_string)
        
        for addr, ref_cmd in ref_regs_map.items():
            if addr not in existing_addrs:
                # Add command AND comment
                missing_entries.append((ref_cmd, "//default value"))
        
        if missing_entries:
            print(f"Run '{run['name']}' is missing {len(missing_entries)} commands. Adding them with comments.")
            
            insert_pos = last_reg_index + 1
            
            for cmd_str, comment_str in missing_entries:
                cmds.insert(insert_pos, cmd_str)
                insert_pos += 1
                cmds.insert(insert_pos, comment_str)
                insert_pos += 1
            
            runs_updated += 1
        else:
            print(f"Run '{run['name']}' has all registers. No changes.")

    # 3. Save back to file
    if runs_updated > 0:
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Successfully updated {runs_updated} runs in {config_path}.")
    else:
        print("No updates needed.")

if __name__ == "__main__":
    main()
