"""
Database migration utilities using Alembic.
"""

import os
from pathlib import Path
from alembic import command
from alembic.config import Config

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent


def get_alembic_config() -> Config:
    """Get Alembic configuration.
    
    Returns:
        Alembic Config object.
    """
    alembic_cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    return alembic_cfg


def create_migration(message: str):
    """Create a new migration.
    
    Args:
        message: Migration message.
    """
    alembic_cfg = get_alembic_config()
    command.revision(alembic_cfg, autogenerate=True, message=message)
    print(f"Created migration: {message}")


def upgrade_database(revision: str = "head"):
    """Upgrade database to a revision.
    
    Args:
        revision: Target revision. Default is 'head' (latest).
    """
    alembic_cfg = get_alembic_config()
    command.upgrade(alembic_cfg, revision)
    print(f"Upgraded database to revision: {revision}")


def downgrade_database(revision: str = "-1"):
    """Downgrade database to a revision.
    
    Args:
        revision: Target revision. Default is '-1' (previous).
    """
    alembic_cfg = get_alembic_config()
    command.downgrade(alembic_cfg, revision)
    print(f"Downgraded database to revision: {revision}")


def show_current_revision():
    """Show current database revision."""
    alembic_cfg = get_alembic_config()
    command.current(alembic_cfg)


def show_migration_history():
    """Show migration history."""
    alembic_cfg = get_alembic_config()
    command.history(alembic_cfg)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m database.migrations create <message>  - Create new migration")
        print("  python -m database.migrations upgrade [revision] - Upgrade database")
        print("  python -m database.migrations downgrade [revision] - Downgrade database")
        print("  python -m database.migrations current            - Show current revision")
        print("  python -m database.migrations history            - Show migration history")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "create":
        if len(sys.argv) < 3:
            print("Error: Migration message required")
            sys.exit(1)
        message = " ".join(sys.argv[2:])
        create_migration(message)
    
    elif action == "upgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "head"
        upgrade_database(revision)
    
    elif action == "downgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "-1"
        downgrade_database(revision)
    
    elif action == "current":
        show_current_revision()
    
    elif action == "history":
        show_migration_history()
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
