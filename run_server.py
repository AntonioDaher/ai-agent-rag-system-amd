"""Persistent server wrapper - runs without crashing"""
import os
import sys
import subprocess
import time

# Set environment to avoid Fortran crashes
os.environ['OPENBLAS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_THREADING_LAYER'] = 'GNU'

def run_server():
    """Run the server in a subprocess"""
    print("="*60)
    print("AI Agent RAG System - Server")
    print("="*60)
    print("\nStarting server...")
    print("Access at: http://127.0.0.1:8000/docs")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        # Run uvicorn without reload
        result = subprocess.run(
            [
                sys.executable, '-m', 'uvicorn',
                'src.api.server:app',
                '--host', '127.0.0.1',
                '--port', '8000',
                '--workers', '1'
            ],
            cwd=os.getcwd(),
            capture_output=False
        )
        return result.returncode
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_server()
    sys.exit(exit_code)
