import sys
import os
import logging

# Setup path to find src modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from instrument_control import KeysightController

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestSaveFix")

def test_save_and_export():
    # Configuration
    instrument_ip = "10.144.211.47"
    base_directory = "C:\\Users\\Administrator\\Desktop\\Jason\\OneDrive - ANALOGIX\\HDMI_projects"
    test_name = "Verification_Test_Save_Fix"
    
    logger.info(f"Connecting to {instrument_ip}...")
    controller = KeysightController(instrument_ip, logger=logger)
    
    if not controller.connect():
        logger.error("Could not connect to instrument.")
        return

    # 1. Create New Project (Mock setup)
    logger.info("Creating new project...")
    controller.create_new_project()
    
    # 2. Save Project
    logger.info(f"Testing Save Project to: {base_directory}\\{test_name}")
    # Using the new signature: save_as_path=name, base_directory=base_dir
    res = controller.save_project(save_as_path=test_name, base_directory=base_directory)
    if res:
        logger.info("Save Project: SUCCESS")
    else:
        logger.error("Save Project: FAILED")

    # 3. Export PDF
    pdf_name = f"{test_name}.pdf"
    logger.info(f"Testing Export PDF to: {base_directory}\\{pdf_name}")
    # Using the new signature: file_path=name, directory=base_dir
    res = controller.export_pdf(file_path=pdf_name, directory=base_directory)
    if res:
        logger.info("Export PDF: SUCCESS")
    else:
        logger.error("Export PDF: FAILED")

if __name__ == "__main__":
    test_save_and_export()
