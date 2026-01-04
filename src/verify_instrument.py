import sys
import logging
import time
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("VerifyInstrument")

# Append src to path to import the module
sys.path.append('src')

# --- IMPORT LOGIC ---
# Try importing assuming we are in the src directory or it's in path
try:
    import instrument_control as ic
    from instrument_control import KeysightController
except ImportError:
    # If that fails, try importing as a package from root
    try:
        import src.instrument_control as ic
        from src.instrument_control import KeysightController
    except ImportError as e:
        logger.error(f"Could not import instrument_control: {e}")
        sys.exit(1)

# --- MOCKING INFRASTRUCTURE ---
# Check if the DLL loaded successfully by checking for one of the expected classes
if not hasattr(ic, 'RemoteAteUtilities'):
    logger.warning("Keysight DLL classes not found in instrument_control. Using MOCK objects for verification.")
    
    class MockRemoteApp:
        def __init__(self, remote_obj):
            self.SelectedTests = []
            self.SuppressMessages = False
            self.IsRunning = False
        
        def SetConfig(self, key, value):
            logger.info(f"[MOCK] SetConfig: {key} = {value}")

        def OpenProjectCustom(self, options):
            logger.info(f"[MOCK] OpenProject: {options.FullPath}")

        def NewProject(self, discard_unsaved):
            logger.info(f"[MOCK] NewProject: DiscardUnsaved={discard_unsaved}")

        def Run(self):
            logger.info("[MOCK] Run() called. Tests starting...")
            time.sleep(1) # Simulate test duration
            logger.info("[MOCK] Run() finished.")

        def GetResults(self):
            # Return a realistic looking result string
            return "TestID=100,Passed=True,Margin=15.5;TestID=101,Passed=False,Margin=5.0"

        def SaveProjectCustom(self, options):
            logger.info(f"[MOCK] SaveProject: {options.Name}")
            return "C:\\MockPath\\Project.dpj"

        def ExportResultsPdfCustom(self, options):
            logger.info(f"[MOCK] Export PDF: {options.FileName}")
            return "C:\\MockPath\\Report.pdf"

        def Wait(self, ms):
             pass

    class MockRemoteObj:
        pass

    class MockRemoteAteUtilities:
        @staticmethod
        def GetRemoteAte(ip):
            logger.info(f"[MOCK] GetRemoteAte({ip}) called.")
            return MockRemoteObj()
    
    class MockOptions:
        FullPath = ""
        DiscardUnsaved = False
        Name = ""
        OverwriteExisting = False
        FileName = ""
        Path = ""

    # Inject Mocks into the instrument_control module namespace
    logger.info("Injecting Mocks into instrument_control module...")
    ic.RemoteAteUtilities = MockRemoteAteUtilities
    ic.IRemoteAte = MockRemoteApp
    ic.OpenProjectOptions = MockOptions
    ic.SaveProjectOptions = MockOptions
    ic.ExportPdfOptions = MockOptions
else:
    logger.info("Keysight DLL loaded successfully.")

# --- VERIFICATION TEST ---

def test_instrument_control():
    ip_address = "10.144.211.47" # Default from TMDS.py
    
    logger.info("--- Initializing Controller ---")
    scope = KeysightController(ip_address, logger=logger)
    
    logger.info("--- Testing Connect ---")
    if not scope.connect():
        logger.error("Failed to connect. Aborting test.")
        return

    logger.info("--- Testing Create New Project ---")
    # Create new project instead of loading one
    scope.create_new_project()
    
    logger.info("--- Testing Load Config ---")
    # Use absolute path tailored to script location
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'full_config.json')
    scope.load_config_file(config_path)
    
    logger.info("--- Testing Select Tests ---")
    scope.select_tests([119042])
    
    logger.info("--- Testing Run Tests ---")
    scope.run_tests()
    
    logger.info("--- Testing Get Results ---")
    results = scope.get_results()
    print("Results Received:")
    for r in results:
        print(f"  ID: {r['test_id']}, Pass: {r['passed']}, Margin: {r['margin']}")

    logger.info("--- Testing Save Project ---")
    scope.save_project("VerifiedProject")
    
    logger.info("--- Testing Export PDF ---")
    scope.export_pdf("C:\\proj\\AutoTest_DP\\Report.pdf")
    


    logger.info("--- Verification Complete ---")

if __name__ == "__main__":
    test_instrument_control()
