"""Basic tests for gdrive-catalog package."""

import pytest
from gdrive_catalog import __version__


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_imports():
    """Test that main modules can be imported."""
    from gdrive_catalog.cli import app
    from gdrive_catalog.drive_service import DriveService
    from gdrive_catalog.scanner import DriveScanner
    
    assert app is not None
    assert DriveService is not None
    assert DriveScanner is not None
