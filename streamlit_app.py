"""
MLOps Dashboard - Streamlit Cloud Entry Point
This file allows Streamlit Cloud to find and run the app.
"""

import sys
from pathlib import Path

# Add the services/ui directory to the path
ui_path = Path(__file__).parent / "services" / "ui"
sys.path.insert(0, str(ui_path))
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the main app
from services.ui.app import *
