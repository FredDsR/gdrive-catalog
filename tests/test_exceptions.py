"""Tests for custom exception classes."""

from unittest.mock import MagicMock

import pytest

from gdrive_catalog.exceptions import (
    DriveServiceError,
    FileDownloadError,
    FileListError,
    FileMetadataError,
)


class TestDriveServiceError:
    """Tests for DriveServiceError base exception."""

    def test_basic_message(self):
        """Test exception with just a message."""
        error = DriveServiceError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.operation is None
        assert error.original_error is None
        assert error.status_code is None

    def test_with_operation(self):
        """Test exception with operation context."""
        error = DriveServiceError("API error", operation="list files")
        assert str(error) == "Failed to list files: API error"
        assert error.operation == "list files"

    def test_with_mock_http_error(self):
        """Test exception with mocked HttpError."""
        mock_error = MagicMock()
        mock_error.resp.status = 404

        error = DriveServiceError(
            "Not found",
            operation="get file",
            original_error=mock_error,
        )

        assert str(error) == "Failed to get file: Not found (HTTP 404)"
        assert error.status_code == 404
        assert error.original_error is mock_error

    def test_inheritance(self):
        """Test that DriveServiceError inherits from Exception."""
        error = DriveServiceError("Test error")
        assert isinstance(error, Exception)

    def test_can_be_raised_and_caught(self):
        """Test that exception can be raised and caught properly."""
        with pytest.raises(DriveServiceError) as exc_info:
            raise DriveServiceError("Test error", operation="test")
        assert "Failed to test: Test error" in str(exc_info.value)


class TestFileListError:
    """Tests for FileListError exception."""

    def test_without_folder_id(self):
        """Test error when listing root files."""
        error = FileListError("Access denied")
        assert "list files" in str(error)
        assert error.folder_id is None

    def test_with_folder_id(self):
        """Test error when listing specific folder."""
        error = FileListError("Not found", folder_id="abc123")
        assert "list files in folder 'abc123'" in str(error)
        assert error.folder_id == "abc123"

    def test_with_http_error(self):
        """Test error with HTTP status code."""
        mock_error = MagicMock()
        mock_error.resp.status = 403

        error = FileListError(
            "Permission denied",
            folder_id="xyz789",
            original_error=mock_error,
        )

        assert "(HTTP 403)" in str(error)
        assert error.status_code == 403

    def test_inheritance(self):
        """Test that FileListError inherits from DriveServiceError."""
        error = FileListError("Test")
        assert isinstance(error, DriveServiceError)
        assert isinstance(error, Exception)


class TestFileMetadataError:
    """Tests for FileMetadataError exception."""

    def test_basic_usage(self):
        """Test basic file metadata error."""
        error = FileMetadataError("File not found", file_id="file123")
        assert "get metadata for file 'file123'" in str(error)
        assert error.file_id == "file123"

    def test_with_http_error(self):
        """Test error with HTTP status code."""
        mock_error = MagicMock()
        mock_error.resp.status = 404

        error = FileMetadataError(
            "Not found",
            file_id="file456",
            original_error=mock_error,
        )

        assert "(HTTP 404)" in str(error)
        assert error.status_code == 404

    def test_inheritance(self):
        """Test that FileMetadataError inherits from DriveServiceError."""
        error = FileMetadataError("Test", file_id="abc")
        assert isinstance(error, DriveServiceError)
        assert isinstance(error, Exception)


class TestFileDownloadError:
    """Tests for FileDownloadError exception."""

    def test_basic_usage(self):
        """Test basic file download error."""
        error = FileDownloadError("Download failed", file_id="download123")
        assert "download file 'download123'" in str(error)
        assert error.file_id == "download123"

    def test_with_http_error(self):
        """Test error with HTTP status code."""
        mock_error = MagicMock()
        mock_error.resp.status = 500

        error = FileDownloadError(
            "Server error",
            file_id="file789",
            original_error=mock_error,
        )

        assert "(HTTP 500)" in str(error)
        assert error.status_code == 500

    def test_inheritance(self):
        """Test that FileDownloadError inherits from DriveServiceError."""
        error = FileDownloadError("Test", file_id="abc")
        assert isinstance(error, DriveServiceError)
        assert isinstance(error, Exception)


class TestExceptionChaining:
    """Tests for exception chaining behavior."""

    def test_can_catch_all_with_base_class(self):
        """Test that all specific exceptions can be caught with base class."""
        errors = [
            FileListError("list error"),
            FileMetadataError("metadata error", file_id="abc"),
            FileDownloadError("download error", file_id="xyz"),
        ]

        for error in errors:
            with pytest.raises(DriveServiceError):
                raise error

    def test_exception_chain_preserved(self):
        """Test that exception chaining preserves the original error."""
        mock_original = MagicMock()
        mock_original.resp.status = 401

        try:
            try:
                raise ValueError("Original cause")
            except ValueError as e:
                raise FileListError(
                    "API error",
                    original_error=mock_original,
                ) from e
        except FileListError as e:
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)
            assert e.original_error is mock_original
