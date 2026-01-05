import json
import os
import sys
import logging
import time

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.dirname(__file__))

from verify_instrument import run_instrument_tests
from dut_control_client import DutControlClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BatchRunner")

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def run_batch(config_path):
    config = load_config(config_path)
    common = config.get("common_settings", {})
    runs = config.get("runs", [])
    
    dut_ip = common.get("dut_server_ip")
    dut_port = common.get("dut_server_port", 13000)
    instrument_ip = common.get("instrument_ip")
    default_test_ids = common.get("default_test_ids", [])
    base_dir = common.get("base_directory")
    
    # Initialize DUT Configuration
    logger.info(f"Connecting to DUT Server at {dut_ip}:{dut_port}...")
    dut_client = DutControlClient(server_ip=dut_ip, server_port=dut_port, logger=logger)
    
    results_summary = []
    
    start_time_total = time.time()
    
    for run in runs:
        run_name = run["name"]
        logger.info(f"==================================================")
        logger.info(f"STARTING RUN: {run_name}")
        logger.info(f"==================================================")
        
        run_start_time = time.time()
        
        # 1. Configure DUT
        logger.info(f"[{run_name}] Configuring DUT...")
        for cmd in run.get("dut_commands", []):
            if cmd.strip().startswith("//") or cmd.strip().startswith("#"):
                continue

            logger.info(f"  Sending: {cmd}")
            # Check if it is a write_register convenience string or raw command
            if "write_register" in cmd:
                # Naive parsing for write_register(0x7c, 0x02, 0x01)
                # This expects specific format. 
                # Let's try to extract args.
                try:
                    args_str = cmd.split('(')[1].split(')')[0]
                    args = [int(x.strip(), 16) for x in args_str.split(',')]
                    if len(args) == 3:
                        resp = dut_client.write_register(args[0], args[1], args[2])
                    else:
                        resp = f"Error: Invalid args count in {cmd}"
                except Exception as e:
                    resp = f"Error parsing {cmd}: {e}"
            else:
                 resp = dut_client.send_command(cmd)
            
            logger.info(f"  Response: {resp}")
            if "Error" in str(resp):
                logger.warning(f"  Command failed, continuing run anyway...")

        # 2. Run Instrument Tests
        logger.info(f"[{run_name}] Running Instrument Tests...")
        project_name = run.get("project_name")
        report_name = run.get("report_name")
        test_ids = run.get("test_ids", default_test_ids)
        
        # We need to assume a config path for the instrument run. 
        # For now using default one in src/full_config.json as per verify_instrument logic
        
        try:
             run_results = run_instrument_tests(
                ip_address=instrument_ip,
                project_name=project_name,
                report_path=report_name,
                test_ids=test_ids,
                output_base_dir=base_dir
            )
        except Exception as e:
            logger.error(f"[{run_name}] Instrument Test Failed: {e}")
            run_results = []
        
        run_end_time = time.time()
        run_duration = run_end_time - run_start_time
        logger.info(f"[{run_name}] Run Complete. Duration: {run_duration:.2f}s\n")

        # 3. Collect Results
        if not run_results:
             results_summary.append({
                "Run": run_name,
                "TestID": "Error",
                "Pass": False,
                "Margin": "N/A",
                "Duration": run_duration,
                "Error": True
            })
        else:
            for res in run_results:
                results_summary.append({
                    "Run": run_name,
                    "TestID": res['test_id'],
                    "Pass": res['passed'],
                    "Margin": res['margin'],
                    "Duration": run_duration
                })
            
    total_duration = time.time() - start_time_total
        
    # 4. Print Summary
    print(f"\nTotal Duration: {total_duration:.2f} s\n")
    print(f"{'Run':<30} | {'Pass / Total':<12} | {'Status':<15} | {'Avg Duration (s)':<16} | {'Key Observation'}")
    print("-" * 110)

    # Group results by Run
    from collections import defaultdict
    run_map = defaultdict(list)
    for res in results_summary:
        run_map[res['Run']].append(res)
    
    # Iterate in order of config runs to maintain sequence
    processed_runs = []
    for run in runs:
        r_name = run["name"]
        if r_name in processed_runs: continue
        processed_runs.append(r_name)
        
        items = run_map.get(r_name, [])
        if not items:
            print(f"{r_name:<30} | {'0 / 0':<12} | {'❌ Skipped':<15} | {'0.00':<16} | {'Run skipped or output missing'}")
            continue

        # Check for execution error
        if len(items) == 1 and items[0].get('Error'):
             status = "❌ Exec Error"
             duration = items[0]['Duration']
             obs = "Instrument test failed to execute (Check logs)"
             print(f"{r_name:<30} | {'0 / 0':<12} | {status:<15} | {duration:<16.2f} | {obs}")
             continue

        total = len(items)
        passed = sum(1 for x in items if x['Pass'])
        failed_ids = [str(x['TestID']) for x in items if not x['Pass']]
        duration = items[0]['Duration']  # Run duration is same for all items in run
        
        # Determine Status and Observation
        if passed == total and total > 0:
            status = "✅ All Pass"
            obs = "All tests passed."
        elif passed == 0 and total > 0:
            status = "❌ All Fail"
            obs = "Systemic failure across all tests"
        else:
            status = "⚠ Partial Fail"
            if len(failed_ids) == 1:
                obs = f"Single failure (TestID {failed_ids[0]})"
            else:
                # Truncate if too long
                ids_str = ", ".join(failed_ids)
                if len(ids_str) > 30:
                     ids_str = ids_str[:27] + "..."
                obs = f"Failures on {ids_str}"

        print(f"{r_name:<30} | {f'{passed} / {total}':<12} | {status:<15} | {duration:<16.2f} | {obs}")
    print("==================================================")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        # Default to batch_config.json in project root
        config_file = os.path.join(os.path.dirname(__file__), '..', 'batch_config.json')
        
    if not os.path.exists(config_file):
        print(f"Error: Config file not found: {config_file}")
        sys.exit(1)
        
    run_batch(config_file)
