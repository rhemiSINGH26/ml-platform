#!/usr/bin/env python3
"""
Initialize the database - create tables and run initial migration.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.connection import init_database
from config import settings


def main():
    """Initialize database."""
    print(f"Initializing database at: {settings.DATABASE_URL}")
    
    try:
        # Create tables
        init_database()
        print("✓ Database initialized successfully!")
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
