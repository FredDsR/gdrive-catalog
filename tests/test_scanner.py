"""Tests for the DriveScanner module."""

from unittest.mock import MagicMock

from gdrive_catalog.scanner import DriveScanner


class TestDriveScannerInit:
    """Tests for DriveScanner initialization."""

    def test_init_with_drive_service(self):
        """Test that scanner initializes with a drive service."""
        mock_service = MagicMock()
        scanner = DriveScanner(mock_service)
        assert scanner.drive_service is mock_service
        assert scanner.folder_cache == {}


class TestDriveScannerMimeTypes:
    """Tests for MIME type constants."""

    def test_audio_mime_types_defined(self):
        """Test that audio MIME types are properly defined."""
        assert "audio/mpeg" in DriveScanner.AUDIO_MIME_TYPES
        assert "audio/mp3" in DriveScanner.AUDIO_MIME_TYPES
        assert "audio/wav" in DriveScanner.AUDIO_MIME_TYPES
        assert "audio/flac" in DriveScanner.AUDIO_MIME_TYPES

    def test_video_mime_types_defined(self):
        """Test that video MIME types are properly defined."""
        assert "video/mp4" in DriveScanner.VIDEO_MIME_TYPES
        assert "video/mpeg" in DriveScanner.VIDEO_MIME_TYPES
        assert "video/quicktime" in DriveScanner.VIDEO_MIME_TYPES
        assert "video/webm" in DriveScanner.VIDEO_MIME_TYPES


class TestExtractDuration:
    """Tests for the _extract_duration method."""

    def test_extract_duration_from_video_metadata(self):
        """Test extracting duration from video metadata."""
        mock_service = MagicMock()
        scanner = DriveScanner(mock_service)

        file = {"videoMediaMetadata": {"durationMillis": "120000"}}
        duration = scanner._extract_duration(file)
        assert duration == 120000

    def test_extract_duration_missing_metadata(self):
        """Test duration extraction when metadata is missing."""
        mock_service = MagicMock()
        scanner = DriveScanner(mock_service)

        file = {}
        duration = scanner._extract_duration(file)
        assert duration is None

    def test_extract_duration_empty_video_metadata(self):
        """Test duration extraction when video metadata is empty."""
        mock_service = MagicMock()
        scanner = DriveScanner(mock_service)

        file = {"videoMediaMetadata": {}}
        duration = scanner._extract_duration(file)
        assert duration is None


class TestExtractFileData:
    """Tests for the _extract_file_data method."""

    def test_extract_basic_file_data(self):
        """Test extracting basic file data."""
        mock_service = MagicMock()
        scanner = DriveScanner(mock_service)

        file = {
            "id": "file123",
            "name": "test_file.txt",
            "mimeType": "text/plain",
            "size": "1024",
            "createdTime": "2024-01-15T10:30:00.000Z",
            "webViewLink": "https://drive.google.com/file/d/file123/view",
        }

        data = scanner._extract_file_data(file)

        assert data["id"] == "file123"
        assert data["name"] == "test_file.txt"
        assert data["size_bytes"] == "1024"
        assert data["mime_type"] == "text/plain"
        assert data["created_at"] == "2024-01-15T10:30:00.000Z"
        assert data["link"] == "https://drive.google.com/file/d/file123/view"
        assert data["duration_milliseconds"] == ""

    def test_extract_file_data_with_video_duration(self):
        """Test extracting file data with video duration."""
        mock_service = MagicMock()
        scanner = DriveScanner(mock_service)

        file = {
            "id": "video123",
            "name": "test_video.mp4",
            "mimeType": "video/mp4",
            "size": "10485760",
            "createdTime": "2024-01-15T10:30:00.000Z",
            "webViewLink": "https://drive.google.com/file/d/video123/view",
            "videoMediaMetadata": {"durationMillis": "60000"},
        }

        data = scanner._extract_file_data(file)

        assert data["id"] == "video123"
        assert data["duration_milliseconds"] == "60000"
        assert data["mime_type"] == "video/mp4"

    def test_extract_file_data_with_audio_no_duration(self):
        """Test extracting file data for audio without duration metadata."""
        mock_service = MagicMock()
        scanner = DriveScanner(mock_service)

        file = {
            "id": "audio123",
            "name": "song.mp3",
            "mimeType": "audio/mpeg",
            "size": "5242880",
            "createdTime": "2024-01-15T10:30:00.000Z",
        }

        data = scanner._extract_file_data(file)

        assert data["id"] == "audio123"
        assert data["duration_milliseconds"] == ""
        assert data["mime_type"] == "audio/mpeg"

    def test_extract_file_data_default_link_fallback(self):
        """Test that default link is generated when webViewLink is missing."""
        mock_service = MagicMock()
        scanner = DriveScanner(mock_service)

        file = {
            "id": "file456",
            "name": "file.txt",
            "mimeType": "text/plain",
        }

        data = scanner._extract_file_data(file)

        assert data["link"] == "https://drive.google.com/file/d/file456/view"

    def test_extract_file_data_missing_fields(self):
        """Test extracting data when optional fields are missing."""
        mock_service = MagicMock()
        scanner = DriveScanner(mock_service)

        file = {"id": "minimal123"}

        data = scanner._extract_file_data(file)

        assert data["id"] == "minimal123"
        assert data["name"] == ""
        assert data["size_bytes"] == "0"
        assert data["created_at"] == ""
        assert data["mime_type"] == ""


class TestBuildFilePath:
    """Tests for the _build_file_path method."""

    def test_build_path_file_at_root(self):
        """Test building path for file at root level."""
        mock_service = MagicMock()
        scanner = DriveScanner(mock_service)

        file = {"name": "root_file.txt"}

        path = scanner._build_file_path(file)
        assert path == "/root_file.txt"

    def test_build_path_with_parent_folder(self):
        """Test building path with parent folder from cache."""
        mock_service = MagicMock()
        scanner = DriveScanner(mock_service)

        # Pre-populate folder cache
        scanner.folder_cache["parent123"] = {"name": "Documents", "parent": None}

        file = {"name": "report.pdf", "parents": ["parent123"]}

        path = scanner._build_file_path(file)
        assert path == "/Documents/report.pdf"

    def test_build_path_with_nested_folders(self):
        """Test building path with nested folders from cache."""
        mock_service = MagicMock()
        scanner = DriveScanner(mock_service)

        # Pre-populate folder cache
        scanner.folder_cache["child_folder"] = {"name": "Reports", "parent": "parent_folder"}
        scanner.folder_cache["parent_folder"] = {"name": "Work", "parent": None}

        file = {"name": "annual.pdf", "parents": ["child_folder"]}

        path = scanner._build_file_path(file)
        assert path == "/Work/Reports/annual.pdf"

    def test_build_path_fetches_uncached_folder(self):
        """Test that path building fetches uncached folder metadata."""
        mock_drive_service = MagicMock()
        mock_drive_service.service.files().get().execute.return_value = {
            "name": "NewFolder",
            "parents": [],
        }

        scanner = DriveScanner(mock_drive_service)

        file = {"name": "file.txt", "parents": ["new_folder_id"]}

        path = scanner._build_file_path(file)

        assert "NewFolder" in path
        assert "file.txt" in path
        # Verify folder was cached
        assert "new_folder_id" in scanner.folder_cache

    def test_build_path_handles_api_error(self):
        """Test that path building handles API errors gracefully."""
        mock_drive_service = MagicMock()
        mock_drive_service.service.files().get().execute.side_effect = Exception("API Error")

        scanner = DriveScanner(mock_drive_service)

        file = {"name": "file.txt", "parents": ["error_folder_id"]}

        # Should not raise, should return partial path
        path = scanner._build_file_path(file)
        assert "file.txt" in path

    def test_build_path_detects_circular_reference(self):
        """Test that path building detects and handles circular references."""
        mock_service = MagicMock()
        scanner = DriveScanner(mock_service)

        # Create circular reference in cache
        scanner.folder_cache["folder_a"] = {"name": "FolderA", "parent": "folder_b"}
        scanner.folder_cache["folder_b"] = {"name": "FolderB", "parent": "folder_a"}

        file = {"name": "file.txt", "parents": ["folder_a"]}

        # Should not hang, should return a path
        path = scanner._build_file_path(file)
        assert "file.txt" in path


class TestScanDrive:
    """Tests for the scan_drive method."""

    def test_scan_drive_empty_results(self):
        """Test scanning drive with no files."""
        mock_drive_service = MagicMock()
        mock_drive_service.list_files.return_value = {"files": [], "nextPageToken": None}

        scanner = DriveScanner(mock_drive_service)
        result = scanner.scan_drive()

        assert result == []
        mock_drive_service.list_files.assert_called_once()

    def test_scan_drive_single_file(self):
        """Test scanning drive with a single file."""
        mock_drive_service = MagicMock()
        mock_drive_service.list_files.return_value = {
            "files": [
                {
                    "id": "file1",
                    "name": "document.pdf",
                    "mimeType": "application/pdf",
                    "size": "2048",
                    "createdTime": "2024-01-15T10:00:00.000Z",
                    "webViewLink": "https://drive.google.com/file/d/file1/view",
                }
            ],
            "nextPageToken": None,
        }

        scanner = DriveScanner(mock_drive_service)
        result = scanner.scan_drive()

        assert len(result) == 1
        assert result[0]["id"] == "file1"
        assert result[0]["name"] == "document.pdf"

    def test_scan_drive_with_folder_id(self):
        """Test scanning specific folder."""
        mock_drive_service = MagicMock()
        mock_drive_service.list_files.return_value = {"files": [], "nextPageToken": None}

        scanner = DriveScanner(mock_drive_service)
        scanner.scan_drive(folder_id="folder123")

        mock_drive_service.list_files.assert_called_with(folder_id="folder123", page_token=None)

    def test_scan_drive_skips_folders(self):
        """Test that scanning skips folder entries from results (adds to queue)."""
        mock_drive_service = MagicMock()
        # First call returns a folder and a file
        # Second call returns empty (for scanning the folder)
        mock_drive_service.list_files.side_effect = [
            {
                "files": [
                    {
                        "id": "folder1",
                        "name": "My Folder",
                        "mimeType": "application/vnd.google-apps.folder",
                    },
                    {
                        "id": "file1",
                        "name": "document.pdf",
                        "mimeType": "application/pdf",
                        "size": "1024",
                    },
                ],
                "nextPageToken": None,
            },
            {
                "files": [],
                "nextPageToken": None,
            },
        ]

        scanner = DriveScanner(mock_drive_service)
        result = scanner.scan_drive()

        # Should only return the file, not the folder (folder is queued for scanning)
        assert len(result) == 1
        assert result[0]["id"] == "file1"

    def test_scan_drive_skips_google_workspace_files(self):
        """Test that scanning skips Google Workspace files."""
        mock_drive_service = MagicMock()
        mock_drive_service.list_files.return_value = {
            "files": [
                {
                    "id": "doc1",
                    "name": "My Document",
                    "mimeType": "application/vnd.google-apps.document",
                },
                {
                    "id": "sheet1",
                    "name": "My Spreadsheet",
                    "mimeType": "application/vnd.google-apps.spreadsheet",
                },
                {
                    "id": "file1",
                    "name": "real_file.pdf",
                    "mimeType": "application/pdf",
                    "size": "1024",
                },
            ],
            "nextPageToken": None,
        }

        scanner = DriveScanner(mock_drive_service)
        result = scanner.scan_drive()

        # Should only return the real file
        assert len(result) == 1
        assert result[0]["id"] == "file1"

    def test_scan_drive_recursive_folder_scanning(self):
        """Test that scanning discovers and scans subfolders."""
        mock_drive_service = MagicMock()

        # First call returns a folder and a file
        # Second call (for subfolder) returns another file
        mock_drive_service.list_files.side_effect = [
            {
                "files": [
                    {
                        "id": "subfolder1",
                        "name": "Subfolder",
                        "mimeType": "application/vnd.google-apps.folder",
                    },
                    {
                        "id": "file1",
                        "name": "root_file.pdf",
                        "mimeType": "application/pdf",
                        "size": "1024",
                    },
                ],
                "nextPageToken": None,
            },
            {
                "files": [
                    {
                        "id": "file2",
                        "name": "subfolder_file.pdf",
                        "mimeType": "application/pdf",
                        "size": "2048",
                    },
                ],
                "nextPageToken": None,
            },
        ]

        scanner = DriveScanner(mock_drive_service)
        result = scanner.scan_drive()

        # Should return both files
        assert len(result) == 2
        file_ids = [f["id"] for f in result]
        assert "file1" in file_ids
        assert "file2" in file_ids

    def test_scan_drive_pagination(self):
        """Test that scanning handles pagination correctly."""
        mock_drive_service = MagicMock()

        # First page with continuation token
        # Second page (final)
        mock_drive_service.list_files.side_effect = [
            {
                "files": [
                    {
                        "id": "file1",
                        "name": "page1_file.pdf",
                        "mimeType": "application/pdf",
                        "size": "1024",
                    },
                ],
                "nextPageToken": "token_page2",
            },
            {
                "files": [
                    {
                        "id": "file2",
                        "name": "page2_file.pdf",
                        "mimeType": "application/pdf",
                        "size": "2048",
                    },
                ],
                "nextPageToken": None,
            },
        ]

        scanner = DriveScanner(mock_drive_service)
        result = scanner.scan_drive()

        assert len(result) == 2
        # Verify pagination token was used
        calls = mock_drive_service.list_files.call_args_list
        assert len(calls) == 2
        assert calls[1][1]["page_token"] == "token_page2"

    def test_scan_drive_avoids_duplicate_folder_scans(self):
        """Test that scanning doesn't scan the same folder twice."""
        mock_drive_service = MagicMock()

        # First call returns a folder that references back to root
        mock_drive_service.list_files.side_effect = [
            {
                "files": [
                    {
                        "id": "subfolder1",
                        "name": "Subfolder",
                        "mimeType": "application/vnd.google-apps.folder",
                    },
                ],
                "nextPageToken": None,
            },
            {
                "files": [],
                "nextPageToken": None,
            },
        ]

        scanner = DriveScanner(mock_drive_service)
        scanner.scan_drive()

        # Should only call list_files twice (root + subfolder)
        assert mock_drive_service.list_files.call_count == 2
