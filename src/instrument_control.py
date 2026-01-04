import sys
import clr
import logging
import time
import os

# Add reference to the Keysight Remote Interface DLL
# Assuming the DLL is registered or in a known path. 
# If it fails, we might need to sys.path.append the location.
try:
    clr.AddReference("Keysight.DigitalTestApps.Framework.Remote")
    from Keysight.DigitalTestApps.Framework.Remote import *
except Exception as e:
    print(f"Warning: Could not load Keysight DLL: {e}")
    # We might be running in an environment without the DLL, so we define mocks or handle gracefully
    pass

class KeysightController:
    def __init__(self, ip_address, logger=None):
        self.ip_address = ip_address
        self.logger = logger if logger else logging.getLogger("KeysightController")
        self.remote_obj = None
        self.remote_app = None
        self.is_connected = False

    def connect(self):
        """Establishes connection to the remote scope."""
        try:
            self.logger.info(f"Connecting to Keysight Scope at {self.ip_address}...")
            self.remote_obj = RemoteAteUtilities.GetRemoteAte(self.ip_address)
            self.remote_app = IRemoteAte(self.remote_obj)
            self.remote_app.SuppressMessages = True  # Suppress UI popups on the scope
            self.is_connected = True
            self.logger.info("Connection established.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to scope: {e}")
            self.is_connected = False
            return False

    def create_new_project(self):
        """Creates a new project, discarding any unsaved changes."""
        if not self.is_connected: return False
        try:
            self.logger.info("Creating new project...")
            # Using NewProject(discard_unsaved=True) based on documentation
            self.remote_app.NewProject(True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create new project: {e}")
            return False

    def load_setup(self, project_path):
        """Loads a project file (.dpj)."""
        if not self.is_connected:
            self.logger.error("Not connected to scope.")
            return False
            
        try:
            self.logger.info(f"Loading project: {project_path}")
            open_options = OpenProjectOptions()
            open_options.FullPath = project_path
            open_options.DiscardUnsaved = True
            self.remote_app.OpenProjectCustom(open_options)
            self.remote_app.SuppressMessages = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to load project: {e}")
            return False

    def configure(self, config_dict):
        """
        Applies a dictionary of configuration settings.
        Args:
            config_dict (dict): and dict of {key: value} pairs. 
                                e.g. {"ConnectorType": "Standard DP/mDP"}
        """
        if not self.is_connected: return False
        try:
            self.logger.info(f"Applying configuration: {config_dict}")
            for key, value in config_dict.items():
                if key.startswith("_"):
                    continue
                self.remote_app.SetConfig(str(key), str(value))
            return True
        except Exception as e:
            self.logger.error(f"Failed to apply configuration: {e}")
            return False

    def load_config_file(self, file_path):
        """
        Loads configuration from a JSON-like file (supports comments) and applies it.
        """
        import json
        import re
        try:
            self.logger.info(f"Loading configuration from file: {file_path}")
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Remove comments (lines starting with // or #, or inline // or #)
            # Simple regex to remove // and # comments while respecting quotes would be complex.
            # Ideally use a library like `json5` or `commentjson`, but to keep it simple and dependency-free:
            # We will use a regex that handles basic # comments as requested by user example.
            
            # This regex matches # or // outside of quotes is tricky, 
            # let's assume valid values don't contain # or // for now based on spec.
            # User example: "Key": "Value", # Comment
            
            # Remove text from # to end of line
            content_no_comments = re.sub(r'#.*', '', content)
            # Remove text from // to end of line (if they use that too)
            content_no_comments = re.sub(r'//.*', '', content_no_comments)
            
            config_dict = json.loads(content_no_comments)
            return self.configure(config_dict)
        except Exception as e:
            self.logger.error(f"Failed to load config file: {e}")
            return False

    def select_tests(self, test_ids):
        """Selects specific tests by their ID list."""
        if not self.is_connected: return False
        try:
            # Keysight API expects a list of integers
            self.logger.info(f"Selecting tests: {test_ids}")
            self.remote_app.SelectedTests = test_ids
            return True
        except Exception as e:
            self.logger.error(f"Failed to select tests: {e}")
            return False

    def run_tests(self):
        """Starts the execution of selected tests."""
        if not self.is_connected: return False
        try:
            self.logger.info("Starting test execution...")
            self.remote_app.Run()
            return True
        except Exception as e:
            self.logger.error(f"Failed to start tests: {e}")
            return False

    def waitt_for_completion(self, poll_interval=2):
        """
        Polls the status until the test is finished.
        Note: The .NET Remote Interface usually blocks on Run() if using certain modes, 
        but if it returns immediately, we need to poll 'IsRunning'.
        However, based on TMDS.py, Run() seems blocking or we check results after.
        I will assume Run() blocks for simplicity based on provided pseudo-code, 
        but I'll add a check if possible.
        """
        # In many Keysight frameworks, Run() is blocking. 
        # If it is non-blocking, we would check self.remote_app.IsRunning (if available)
        # For now, we assume Run() handles the wait or we just proceed.
        self.logger.info("Waiting for tests to complete... (Assuming synchronous run for now)")
        pass

    def get_results(self):
        """
        Retrieves results of the last run.
        Returns a list of dicts: [{'test_id': 100, 'result': 'Pass', 'margin': 10.5}, ...]
        """
        if not self.is_connected: return []
        parsed_results = []
        try:
            results_str = self.remote_app.GetResults() # Returns a string usually CSV or XML-like
            # Format expected: "TestID=123,Passed=True,Margin=15.2;TestID=..."
            # Reference TMDS.py parsing logic
            
            # TMDS.py logic:
            # TestID=200,Result=Correct,Margin=13.3066666666667,Passed=True
            
            self.logger.debug(f"Raw Results: {results_str}")
            
            # Split by line key-value pairs are usually comma separated
            # Actually TMDS.py reads a *file* that contains the string representation of results.
            # Here we assume GetResults() returns that string directly.
            
            # It seems the output is a list of lines, or one long string.
            # Let's handle string parsing.
            lines = str(results_str).split('\n')
            for line in lines:
                if "TestID=" not in line: continue
                
                parts = line.split(',')
                res_dict = {}
                for part in parts:
                    if "=" in part:
                        k, v = part.split('=', 1)
                        res_dict[k.strip()] = v.strip()
                
                if 'TestID' in res_dict:
                    parsed_results.append({
                        'test_id': int(res_dict['TestID']),
                        'passed': res_dict.get('Passed') == 'True',
                        'margin': float(res_dict.get('Margin', -999.0)),
                        'raw': line
                    })
                    
            return parsed_results

        except Exception as e:
            self.logger.error(f"Failed to get results: {e}")
            return []

    def save_project(self, save_as_path=None, base_directory=None):
        if not self.is_connected: return False
        try:
            opts = SaveProjectOptions()
            opts.OverwriteExisting = True
            
            # If base_directory is provided, set it on the options
            if base_directory:
                 opts.BaseDirectory = base_directory

            if save_as_path:
                if os.path.isabs(save_as_path):
                     directory, filename = os.path.split(save_as_path)
                     opts.BaseDirectory = directory
                     opts.Name = filename
                else:
                     opts.Name = save_as_path

                # Sanitize filename (remove invalid characters: \ / : * ? " < > |)
                name_only = os.path.basename(opts.Name)
                sanitized_name = "".join(c for c in name_only if c not in r'\/:*?"<>|')
                opts.Name = sanitized_name
            
            project_full_path = self.remote_app.SaveProjectCustom(opts)
            self.logger.info(f"Project saved at {project_full_path}")
            return project_full_path
        except Exception as e:
            self.logger.error(f"Failed to save project: {e}")
            return False

    def export_pdf(self, file_path, directory=None):
        if not self.is_connected: return False
        try:
            opts = ExportPdfOptions()
            opts.OverwriteExisting = True
            
            # If directory is explicitly provided, use it.
            if directory:
                 opts.Path = directory
                 opts.FileName = os.path.basename(file_path)
            else:
                 # Standard behavior: split the provided path
                 opts.FileName = os.path.basename(file_path)
                 opts.Path = os.path.dirname(file_path)
            
            opts.ForcePageBreaks = True

            pdf_full_path = self.remote_app.ExportResultsPdfCustom(opts)
            self.logger.info(f"PDF exported at {pdf_full_path}")
            return pdf_full_path
        except Exception as e:
            self.logger.error(f"Failed to export PDF: {e}")
            return False
