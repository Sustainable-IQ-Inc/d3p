import os
import sys
import psutil
import time
import gc
from memory_profiler import profile as mprofile

# Add current directory to path so we can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from post_processing import run_script_master
    import post_processing
except ImportError as e:
    print(f"Error: Could not import D3P backend modules: {e}")
    sys.exit(1)

# Apply memory profiler to the target functions
# We wrap them so we don't have to modify the original source files more than necessary
run_script_master_profiled = mprofile(run_script_master)
post_process_profiled = mprofile(post_processing.post_process)

import requests
from io import BytesIO

# Mock Response object for local files
class MockResponse:
    def __init__(self, content):
        self.content = content
        self.status_code = 200
    def raise_for_status(self):
        pass

def get_mem_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def run_profile(url, report_type=None):
    # Check if URL is actually a local file
    if os.path.exists(url):
        print(f"--- Detected local file: {url} ---")
        # Monkeypatch requests.get to return local file content
        original_get = requests.get
        def mock_get(target_url, *args, **kwargs):
            if target_url == url:
                with open(url, 'rb') as f:
                    return MockResponse(f.read())
            return original_get(target_url, *args, **kwargs)
        requests.get = mock_get
        print("Note: requests.get has been monkeypatched to handle this local file.")

    print(f"--- Starting Profile for URL: {url} ---")
    print(f"Initial Memory: {get_mem_usage():.2f} MB")
    
    start_time = time.time()
    
    # We replace the global post_process with the profiled version
    # so that run_script_master calls the profiled one internally
    original_post_process = post_processing.post_process
    post_processing.post_process = post_process_profiled
    
    try:
        # Run the full parsing pipeline
        results = run_script_master_profiled(url, report_type=report_type)
        
        end_time = time.time()
        print(f"\n--- Profile Complete ---")
        print(f"Total Duration: {end_time - start_time:.2f} seconds")
        print(f"Final Memory: {get_mem_usage():.2f} MB")
        
        if isinstance(results, dict) and results.get('status') == 'success':
            print("Status: SUCCESS")
            if 'df' in results:
                print(f"DataFrame Shape: {results['df'].shape}")
        else:
            print(f"Status: FAILED or PENDING")
            print(f"Results: {results}")

    finally:
        # Restore original functions
        post_processing.post_process = original_post_process
        if 'original_get' in locals():
            requests.get = original_get

    # Force garbage collection and check memory again
    gc.collect()
    print(f"Memory after gc.collect(): {get_mem_usage():.2f} MB")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python profile_d3p_memory.py [FILE_URL] [OPTIONAL_REPORT_TYPE]")
        sys.exit(1)
    
    file_url = sys.argv[1]
    rpt_type = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    run_profile(file_url, rpt_type)
