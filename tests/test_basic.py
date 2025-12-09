"""Basic tests for gdrive-cli package."""

from gdrive_cli import __version__


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_imports():
    """Test that main modules can be imported."""
    from gdrive_cli.cli import app
    from gdrive_cli.drive_service import DriveService
    from gdrive_cli.exceptions import (
        DriveServiceError,
        FileDownloadError,
        FileListError,
        FileMetadataError,
    )
    from gdrive_cli.scanner import DriveScanner

    assert app is not None
    assert DriveService is not None
    assert DriveScanner is not None
    assert DriveServiceError is not None
    assert FileListError is not None
    assert FileMetadataError is not None
    assert FileDownloadError is not None
