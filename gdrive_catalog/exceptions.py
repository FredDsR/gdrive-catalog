# gdrive-catalog - CLI tool to scan Google Drive storage and create CSV catalogs
# Copyright (C) 2024 gdrive-catalog contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Custom exceptions for Google Drive catalog operations."""

from googleapiclient.errors import HttpError


class DriveServiceError(Exception):
    """
    Base exception for Google Drive service operations.

    This exception wraps errors from the Google Drive API to provide
    more context about what operation failed and why. It preserves
    the original HttpError for debugging purposes.

    Attributes:
        message: Human-readable description of what went wrong.
        operation: The operation that was being performed when the error occurred.
        original_error: The original HttpError from the Google API, if available.
    """

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        original_error: HttpError | None = None,
    ):
        """
        Initialize the DriveServiceError.

        Args:
            message: Human-readable description of the error.
            operation: The operation that failed (e.g., "list_files", "get_file_metadata").
            original_error: The original HttpError from the Google API.
        """
        self.message = message
        self.operation = operation
        self.original_error = original_error

        # Build a descriptive error message
        full_message = message
        if operation:
            full_message = f"Failed to {operation}: {message}"
        if original_error:
            full_message = f"{full_message} (HTTP {original_error.resp.status})"

        super().__init__(full_message)

    @property
    def status_code(self) -> int | None:
        """Return the HTTP status code from the original error, if available."""
        if self.original_error:
            return self.original_error.resp.status
        return None


class FileListError(DriveServiceError):
    """
    Exception raised when listing files in Google Drive fails.

    This typically occurs due to:
    - Invalid folder ID
    - Insufficient permissions to access the folder
    - API rate limiting
    - Network connectivity issues
    """

    def __init__(
        self,
        message: str,
        folder_id: str | None = None,
        original_error: HttpError | None = None,
    ):
        """
        Initialize the FileListError.

        Args:
            message: Human-readable description of the error.
            folder_id: The folder ID that was being listed, if any.
            original_error: The original HttpError from the Google API.
        """
        self.folder_id = folder_id
        operation = "list files"
        if folder_id:
            operation = f"list files in folder '{folder_id}'"
        super().__init__(message, operation=operation, original_error=original_error)


class FileMetadataError(DriveServiceError):
    """
    Exception raised when retrieving file metadata fails.

    This typically occurs due to:
    - Invalid file ID
    - File has been deleted or moved
    - Insufficient permissions to access the file
    - API rate limiting
    """

    def __init__(
        self,
        message: str,
        file_id: str,
        original_error: HttpError | None = None,
    ):
        """
        Initialize the FileMetadataError.

        Args:
            message: Human-readable description of the error.
            file_id: The file ID that metadata was requested for.
            original_error: The original HttpError from the Google API.
        """
        self.file_id = file_id
        operation = f"get metadata for file '{file_id}'"
        super().__init__(message, operation=operation, original_error=original_error)


class FileDownloadError(DriveServiceError):
    """
    Exception raised when downloading a file from Google Drive fails.

    This typically occurs due to:
    - Invalid file ID
    - File is too large
    - File has been deleted or moved
    - Insufficient permissions to download the file
    - API rate limiting
    """

    def __init__(
        self,
        message: str,
        file_id: str,
        original_error: HttpError | None = None,
    ):
        """
        Initialize the FileDownloadError.

        Args:
            message: Human-readable description of the error.
            file_id: The file ID that was being downloaded.
            original_error: The original HttpError from the Google API.
        """
        self.file_id = file_id
        operation = f"download file '{file_id}'"
        super().__init__(message, operation=operation, original_error=original_error)


class CSVValidationError(Exception):
    """
    Exception raised when CSV file validation fails.

    This exception is raised when a CSV file does not match the expected
    catalog schema. It provides detailed information about what validation
    failed to help users fix their CSV files.

    Attributes:
        message: Human-readable description of the validation failure.
        file_path: Path to the CSV file that failed validation.
        missing_columns: Set of required columns that are missing from the CSV.
        actual_columns: Set of columns found in the CSV file.
    """

    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        missing_columns: set[str] | None = None,
        actual_columns: set[str] | None = None,
    ):
        """
        Initialize the CSVValidationError.

        Args:
            message: Human-readable description of the validation failure.
            file_path: Path to the CSV file that failed validation.
            missing_columns: Set of required columns missing from the CSV.
            actual_columns: Set of columns found in the CSV file.
        """
        self.message = message
        self.file_path = file_path
        self.missing_columns = missing_columns or set()
        self.actual_columns = actual_columns or set()

        # Build a descriptive error message
        full_message = message
        if file_path:
            full_message = f"Invalid CSV file '{file_path}': {message}"
        if missing_columns:
            full_message = f"{full_message}. Missing columns: {sorted(missing_columns)}"

        super().__init__(full_message)
