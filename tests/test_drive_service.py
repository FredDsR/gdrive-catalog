"""Tests for the DriveService module."""

from unittest.mock import MagicMock, mock_open, patch

import pytest

from gdrive_catalog.drive_service import SCOPES, DriveService
from gdrive_catalog.exceptions import FileDownloadError, FileListError, FileMetadataError


class TestDriveServiceScopes:
    """Tests for API scopes configuration."""

    def test_scopes_contains_readonly(self):
        """Test that SCOPES contains the read-only Drive scope."""
        assert "https://www.googleapis.com/auth/drive.readonly" in SCOPES


class TestDriveServiceInit:
    """Tests for DriveService initialization."""

    @patch("gdrive_catalog.drive_service.DriveService._authenticate")
    def test_init_sets_credentials_path(self, mock_auth):
        """Test that initialization sets the credentials path."""
        mock_auth.return_value = MagicMock()
        service = DriveService(credentials_path="/path/to/creds.json")
        assert service.credentials_path == "/path/to/creds.json"

    @patch("gdrive_catalog.drive_service.DriveService._authenticate")
    def test_init_default_credentials_path(self, mock_auth):
        """Test that initialization uses default credentials path."""
        mock_auth.return_value = MagicMock()
        service = DriveService()
        assert service.credentials_path == "credentials.json"

    @patch("gdrive_catalog.drive_service.DriveService._authenticate")
    def test_init_sets_token_path(self, mock_auth):
        """Test that initialization sets the token path."""
        mock_auth.return_value = MagicMock()
        service = DriveService()
        assert service.token_path == "token.pickle"

    @patch("gdrive_catalog.drive_service.DriveService._authenticate")
    def test_init_calls_authenticate(self, mock_auth):
        """Test that initialization calls _authenticate."""
        mock_auth.return_value = MagicMock()
        DriveService()
        mock_auth.assert_called_once()


class TestDriveServiceAuthenticate:
    """Tests for the _authenticate method."""

    @patch("gdrive_catalog.drive_service.build")
    @patch("gdrive_catalog.drive_service.InstalledAppFlow")
    @patch("gdrive_catalog.drive_service.pickle")
    @patch("gdrive_catalog.drive_service.Path")
    def test_authenticate_new_credentials(self, mock_path, mock_pickle, mock_flow, mock_build):
        """Test authentication with no existing token."""
        # No existing token
        mock_path.return_value.exists.return_value = False

        # Mock the OAuth flow
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_flow.from_client_secrets_file.return_value.run_local_server.return_value = mock_creds

        mock_build.return_value = MagicMock()

        with patch("builtins.open", mock_open()):
            service = DriveService(credentials_path="creds.json")

        mock_flow.from_client_secrets_file.assert_called_once()
        mock_build.assert_called_once_with("drive", "v3", credentials=mock_creds)
        assert service.service is not None

    @patch("gdrive_catalog.drive_service.build")
    @patch("gdrive_catalog.drive_service.pickle")
    @patch("gdrive_catalog.drive_service.Path")
    def test_authenticate_with_valid_existing_token(self, mock_path, mock_pickle, mock_build):
        """Test authentication with valid existing token."""
        # Token exists
        mock_path.return_value.exists.return_value = True

        # Mock valid credentials
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_pickle.load.return_value = mock_creds

        mock_build.return_value = MagicMock()

        with patch("builtins.open", mock_open()):
            service = DriveService(credentials_path="creds.json")

        mock_build.assert_called_once_with("drive", "v3", credentials=mock_creds)
        assert service.service is not None

    @patch("gdrive_catalog.drive_service.build")
    @patch("gdrive_catalog.drive_service.Request")
    @patch("gdrive_catalog.drive_service.pickle")
    @patch("gdrive_catalog.drive_service.Path")
    def test_authenticate_refresh_expired_token(
        self, mock_path, mock_pickle, mock_request, mock_build
    ):
        """Test authentication refreshes expired token."""
        # Token exists
        mock_path.return_value.exists.return_value = True

        # Mock expired credentials with refresh token
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh_token_value"
        mock_pickle.load.return_value = mock_creds

        mock_build.return_value = MagicMock()

        with patch("builtins.open", mock_open()):
            service = DriveService(credentials_path="creds.json")

        mock_creds.refresh.assert_called_once()
        mock_build.assert_called_once()
        assert service.service is not None


class TestDriveServiceListFiles:
    """Tests for the list_files method."""

    @patch("gdrive_catalog.drive_service.DriveService._authenticate")
    def test_list_files_basic(self, mock_auth):
        """Test basic file listing."""
        mock_service = MagicMock()
        mock_auth.return_value = mock_service

        expected_result = {
            "files": [{"id": "file1", "name": "test.txt"}],
            "nextPageToken": None,
        }
        mock_service.files().list().execute.return_value = expected_result

        service = DriveService()
        result = service.list_files()

        assert result == expected_result

    @patch("gdrive_catalog.drive_service.DriveService._authenticate")
    def test_list_files_with_folder_id(self, mock_auth):
        """Test file listing with folder ID."""
        mock_service = MagicMock()
        mock_auth.return_value = mock_service

        expected_result = {"files": [], "nextPageToken": None}
        mock_service.files().list().execute.return_value = expected_result

        service = DriveService()
        service.list_files(folder_id="folder123")

        # Verify the query was constructed correctly
        mock_service.files().list.assert_called()

    @patch("gdrive_catalog.drive_service.DriveService._authenticate")
    def test_list_files_with_pagination(self, mock_auth):
        """Test file listing with pagination."""
        mock_service = MagicMock()
        mock_auth.return_value = mock_service

        expected_result = {"files": [], "nextPageToken": "next_token"}
        mock_service.files().list().execute.return_value = expected_result

        service = DriveService()
        service.list_files(page_token="current_token", page_size=500)

        mock_service.files().list.assert_called()

    @patch("gdrive_catalog.drive_service.DriveService._authenticate")
    def test_list_files_http_error(self, mock_auth):
        """Test file listing with HTTP error."""
        from googleapiclient.errors import HttpError

        mock_service = MagicMock()
        mock_auth.return_value = mock_service

        # Create a mock HttpError
        mock_resp = MagicMock()
        mock_resp.status = 403
        http_error = HttpError(resp=mock_resp, content=b"Access denied")

        mock_service.files().list().execute.side_effect = http_error

        service = DriveService()

        with pytest.raises(FileListError) as exc_info:
            service.list_files()

        assert exc_info.value.status_code == 403


class TestDriveServiceGetFileMetadata:
    """Tests for the get_file_metadata method."""

    @patch("gdrive_catalog.drive_service.DriveService._authenticate")
    def test_get_file_metadata_basic(self, mock_auth):
        """Test getting file metadata."""
        mock_service = MagicMock()
        mock_auth.return_value = mock_service

        expected_result = {
            "id": "file123",
            "name": "document.pdf",
            "mimeType": "application/pdf",
            "size": "2048",
        }
        mock_service.files().get().execute.return_value = expected_result

        service = DriveService()
        result = service.get_file_metadata("file123")

        assert result == expected_result

    @patch("gdrive_catalog.drive_service.DriveService._authenticate")
    def test_get_file_metadata_http_error(self, mock_auth):
        """Test getting file metadata with HTTP error."""
        from googleapiclient.errors import HttpError

        mock_service = MagicMock()
        mock_auth.return_value = mock_service

        mock_resp = MagicMock()
        mock_resp.status = 404
        http_error = HttpError(resp=mock_resp, content=b"Not found")

        mock_service.files().get().execute.side_effect = http_error

        service = DriveService()

        with pytest.raises(FileMetadataError) as exc_info:
            service.get_file_metadata("nonexistent_file")

        assert exc_info.value.status_code == 404
        assert exc_info.value.file_id == "nonexistent_file"


class TestDriveServiceDownloadFile:
    """Tests for the download_file method."""

    @patch("gdrive_catalog.drive_service.DriveService._authenticate")
    def test_download_file_basic(self, mock_auth):
        """Test downloading a file."""
        mock_service = MagicMock()
        mock_auth.return_value = mock_service

        expected_content = b"file content here"
        mock_service.files().get_media().execute.return_value = expected_content

        service = DriveService()
        result = service.download_file("file123")

        assert result == expected_content

    @patch("gdrive_catalog.drive_service.DriveService._authenticate")
    def test_download_file_http_error(self, mock_auth):
        """Test downloading a file with HTTP error."""
        from googleapiclient.errors import HttpError

        mock_service = MagicMock()
        mock_auth.return_value = mock_service

        mock_resp = MagicMock()
        mock_resp.status = 500
        http_error = HttpError(resp=mock_resp, content=b"Server error")

        mock_service.files().get_media().execute.side_effect = http_error

        service = DriveService()

        with pytest.raises(FileDownloadError) as exc_info:
            service.download_file("file123")

        assert exc_info.value.status_code == 500
        assert exc_info.value.file_id == "file123"
