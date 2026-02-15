#!/usr/bin/env python3
"""Start the server"""
import uvicorn
from pathlib import Path
import sys
import os

# Set working directory
os.chdir(Path(__file__).parent)

# Start uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "src.api.server_minimal:app",
        host="127.0.0.1",
        port=9011,
        log_level="info"
    )
