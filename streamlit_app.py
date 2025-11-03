"""
MLOps Dashboard - Streamlit Cloud Entry Point
This file allows Streamlit Cloud to find and run the app.
"""

import sys
import os
from pathlib import Path

# Set API URL from Streamlit secrets or environment variable
# For Streamlit Cloud: use st.secrets
# For local: use environment variable
try:
    import streamlit as st
    if "API_URL" in st.secrets:
        os.environ["API_URL"] = st.secrets["API_URL"]
        print(f"Using API_URL from secrets: {st.secrets['API_URL']}")
except Exception as e:
    # Fallback to environment variable or default
    if "API_URL" not in os.environ:
        os.environ["API_URL"] = "http://localhost:8000"
        print(f"Using default API_URL: http://localhost:8000")

# Add the services/ui directory to the path
ui_path = Path(__file__).parent / "services" / "ui"
sys.path.insert(0, str(ui_path))
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the main app
from services.ui.app import *
