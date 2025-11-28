"""Tests for the CLI module."""

import csv
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from gdrive_catalog.cli import app

runner = CliRunner()


class TestVersionCommand:
    """Tests for the version command."""

    def test_version_command(self):
        """Test that version command shows the correct version."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.stdout

    def test_version_command_help(self):
        """Test that version command has help text."""
        result = runner.invoke(app, ["version", "--help"])
        assert result.exit_code == 0
        assert "version" in result.stdout.lower()


class TestScanCommand:
    """Tests for the scan command."""

    def test_scan_missing_credentials(self, tmp_path):
        """Test scan fails when credentials file is missing."""
        # Use a non-existent credentials path
        result = runner.invoke(app, ["scan", "--credentials", str(tmp_path / "nonexistent.json")])
        assert result.exit_code == 1
        assert "Credentials file not found" in result.stdout

    def test_scan_help(self):
        """Test scan command help is displayed."""
        import re

        result = runner.invoke(app, ["scan", "--help"])
        assert result.exit_code == 0
        # Strip ANSI escape codes for checking
        ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
        clean_output = ansi_escape.sub("", result.stdout)
        assert "--folder-id" in clean_output
        assert "--output" in clean_output
        assert "--credentials" in clean_output
        assert "--update" in clean_output

    @patch("gdrive_catalog.cli.DriveScanner")
    @patch("gdrive_catalog.cli.DriveService")
    def test_scan_basic(self, mock_drive_service_class, mock_scanner_class, tmp_path):
        """Test basic scan command execution."""
        # Create fake credentials file
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text("{}")

        output_file = tmp_path / "catalog.csv"

        # Mock scanner to return some files
        mock_scanner = MagicMock()
        mock_scanner.scan_drive.return_value = [
            {
                "id": "file1",
                "name": "test.pdf",
                "size_bytes": "1024",
                "duration_milliseconds": "",
                "path": "/test.pdf",
                "link": "https://drive.google.com/file/d/file1/view",
                "created_at": "2024-01-15T10:00:00.000Z",
                "mime_type": "application/pdf",
            }
        ]
        mock_scanner_class.return_value = mock_scanner

        result = runner.invoke(
            app,
            [
                "scan",
                "--credentials",
                str(creds_file),
                "--output",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify CSV content
        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["id"] == "file1"
            assert rows[0]["name"] == "test.pdf"

    @patch("gdrive_catalog.cli.DriveScanner")
    @patch("gdrive_catalog.cli.DriveService")
    def test_scan_with_folder_id(self, mock_drive_service_class, mock_scanner_class, tmp_path):
        """Test scan with specific folder ID."""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text("{}")

        output_file = tmp_path / "catalog.csv"

        mock_scanner = MagicMock()
        mock_scanner.scan_drive.return_value = []
        mock_scanner_class.return_value = mock_scanner

        result = runner.invoke(
            app,
            [
                "scan",
                "--credentials",
                str(creds_file),
                "--output",
                str(output_file),
                "--folder-id",
                "test_folder_123",
            ],
        )

        assert result.exit_code == 0
        mock_scanner.scan_drive.assert_called_once_with(folder_id="test_folder_123")

    @patch("gdrive_catalog.cli.DriveScanner")
    @patch("gdrive_catalog.cli.DriveService")
    def test_scan_update_existing_catalog(
        self, mock_drive_service_class, mock_scanner_class, tmp_path
    ):
        """Test scan with update flag merges with existing catalog."""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text("{}")

        output_file = tmp_path / "catalog.csv"

        # Create existing catalog with one file
        with open(output_file, "w", newline="") as f:
            fieldnames = [
                "id",
                "name",
                "size_bytes",
                "duration_milliseconds",
                "path",
                "link",
                "created_at",
                "mime_type",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(
                {
                    "id": "existing_file",
                    "name": "old.pdf",
                    "size_bytes": "512",
                    "duration_milliseconds": "",
                    "path": "/old.pdf",
                    "link": "https://drive.google.com/file/d/existing_file/view",
                    "created_at": "2024-01-01T00:00:00.000Z",
                    "mime_type": "application/pdf",
                }
            )

        # Mock scanner to return a new file
        mock_scanner = MagicMock()
        mock_scanner.scan_drive.return_value = [
            {
                "id": "new_file",
                "name": "new.pdf",
                "size_bytes": "2048",
                "duration_milliseconds": "",
                "path": "/new.pdf",
                "link": "https://drive.google.com/file/d/new_file/view",
                "created_at": "2024-01-15T10:00:00.000Z",
                "mime_type": "application/pdf",
            }
        ]
        mock_scanner_class.return_value = mock_scanner

        result = runner.invoke(
            app,
            [
                "scan",
                "--credentials",
                str(creds_file),
                "--output",
                str(output_file),
                "--update",
            ],
        )

        assert result.exit_code == 0

        # Verify merged catalog
        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            ids = [r["id"] for r in rows]
            # Should contain both existing and new files
            assert "existing_file" in ids
            assert "new_file" in ids

    @patch("gdrive_catalog.cli.DriveScanner")
    @patch("gdrive_catalog.cli.DriveService")
    def test_scan_update_replaces_existing_entry(
        self, mock_drive_service_class, mock_scanner_class, tmp_path
    ):
        """Test scan with update flag replaces existing entries."""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text("{}")

        output_file = tmp_path / "catalog.csv"

        # Create existing catalog
        with open(output_file, "w", newline="") as f:
            fieldnames = [
                "id",
                "name",
                "size_bytes",
                "duration_milliseconds",
                "path",
                "link",
                "created_at",
                "mime_type",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(
                {
                    "id": "file1",
                    "name": "old_name.pdf",
                    "size_bytes": "512",
                    "duration_milliseconds": "",
                    "path": "/old_name.pdf",
                    "link": "https://drive.google.com/file/d/file1/view",
                    "created_at": "2024-01-01T00:00:00.000Z",
                    "mime_type": "application/pdf",
                }
            )

        # Mock scanner returns same file with updated metadata
        mock_scanner = MagicMock()
        mock_scanner.scan_drive.return_value = [
            {
                "id": "file1",
                "name": "new_name.pdf",
                "size_bytes": "1024",
                "duration_milliseconds": "",
                "path": "/new_name.pdf",
                "link": "https://drive.google.com/file/d/file1/view",
                "created_at": "2024-01-15T10:00:00.000Z",
                "mime_type": "application/pdf",
            }
        ]
        mock_scanner_class.return_value = mock_scanner

        result = runner.invoke(
            app,
            [
                "scan",
                "--credentials",
                str(creds_file),
                "--output",
                str(output_file),
                "--update",
            ],
        )

        assert result.exit_code == 0

        # Verify the file was updated
        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["id"] == "file1"
            assert rows[0]["name"] == "new_name.pdf"
            assert rows[0]["size_bytes"] == "1024"

    @patch("gdrive_catalog.cli.DriveScanner")
    @patch("gdrive_catalog.cli.DriveService")
    def test_scan_creates_output_directory(
        self, mock_drive_service_class, mock_scanner_class, tmp_path
    ):
        """Test scan creates output directory if it doesn't exist."""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text("{}")

        output_file = tmp_path / "nested" / "dir" / "catalog.csv"

        mock_scanner = MagicMock()
        mock_scanner.scan_drive.return_value = []
        mock_scanner_class.return_value = mock_scanner

        result = runner.invoke(
            app,
            [
                "scan",
                "--credentials",
                str(creds_file),
                "--output",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
        assert output_file.parent.exists()
        assert output_file.exists()

    @patch("gdrive_catalog.cli.DriveScanner")
    @patch("gdrive_catalog.cli.DriveService")
    def test_scan_handles_exception(self, mock_drive_service_class, mock_scanner_class, tmp_path):
        """Test scan handles exceptions gracefully."""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text("{}")

        mock_scanner = MagicMock()
        mock_scanner.scan_drive.side_effect = Exception("API Error")
        mock_scanner_class.return_value = mock_scanner

        result = runner.invoke(
            app,
            [
                "scan",
                "--credentials",
                str(creds_file),
            ],
        )

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch("gdrive_catalog.cli.DriveScanner")
    @patch("gdrive_catalog.cli.DriveService")
    def test_scan_displays_file_count(self, mock_drive_service_class, mock_scanner_class, tmp_path):
        """Test scan displays correct file counts."""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text("{}")

        output_file = tmp_path / "catalog.csv"

        mock_scanner = MagicMock()
        mock_scanner.scan_drive.return_value = [
            {
                "id": f"file{i}",
                "name": f"file{i}.pdf",
                "size_bytes": "1024",
                "duration_milliseconds": "",
                "path": f"/file{i}.pdf",
                "link": f"https://drive.google.com/file/d/file{i}/view",
                "created_at": "2024-01-15T10:00:00.000Z",
                "mime_type": "application/pdf",
            }
            for i in range(5)
        ]
        mock_scanner_class.return_value = mock_scanner

        result = runner.invoke(
            app,
            [
                "scan",
                "--credentials",
                str(creds_file),
                "--output",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
        assert "5" in result.stdout


class TestAppConfiguration:
    """Tests for CLI app configuration."""

    def test_app_name(self):
        """Test that the app has the correct name."""
        assert app.info.name == "gdrive-catalog"

    def test_app_help_text(self):
        """Test that the app has help text."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Google Drive" in result.stdout
        assert "catalog" in result.stdout.lower()

    def test_app_commands_available(self):
        """Test that expected commands are available."""
        result = runner.invoke(app, ["--help"])
        assert "scan" in result.stdout
        assert "version" in result.stdout


class TestScanCSVValidation:
    """Tests for CSV validation in the scan command."""

    @patch("gdrive_catalog.cli.DriveScanner")
    @patch("gdrive_catalog.cli.DriveService")
    def test_scan_update_rejects_csv_missing_id_column(
        self, mock_drive_service_class, mock_scanner_class, tmp_path
    ):
        """Test scan with --update rejects CSV file missing 'id' column."""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text("{}")

        output_file = tmp_path / "invalid.csv"

        # Create invalid CSV without 'id' column
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "size_bytes", "path"])
            writer.writeheader()
            writer.writerow({"name": "test.pdf", "size_bytes": "1024", "path": "/test.pdf"})

        result = runner.invoke(
            app,
            [
                "scan",
                "--credentials",
                str(creds_file),
                "--output",
                str(output_file),
                "--update",
            ],
        )

        assert result.exit_code == 1
        assert "Error" in result.stdout
        assert "missing required columns" in result.stdout.lower() or "id" in result.stdout.lower()

    @patch("gdrive_catalog.cli.DriveScanner")
    @patch("gdrive_catalog.cli.DriveService")
    def test_scan_update_rejects_empty_csv(
        self, mock_drive_service_class, mock_scanner_class, tmp_path
    ):
        """Test scan with --update rejects completely empty CSV file."""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text("{}")

        output_file = tmp_path / "empty.csv"
        output_file.write_text("")

        result = runner.invoke(
            app,
            [
                "scan",
                "--credentials",
                str(creds_file),
                "--output",
                str(output_file),
                "--update",
            ],
        )

        assert result.exit_code == 1
        assert "Error" in result.stdout

    @patch("gdrive_catalog.cli.DriveScanner")
    @patch("gdrive_catalog.cli.DriveService")
    def test_scan_update_shows_helpful_message_for_invalid_csv(
        self, mock_drive_service_class, mock_scanner_class, tmp_path
    ):
        """Test that helpful guidance is shown when CSV validation fails."""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text("{}")

        output_file = tmp_path / "invalid.csv"

        # Create invalid CSV
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "size_bytes"])
            writer.writeheader()
            writer.writerow({"name": "test.pdf", "size_bytes": "1024"})

        result = runner.invoke(
            app,
            [
                "scan",
                "--credentials",
                str(creds_file),
                "--output",
                str(output_file),
                "--update",
            ],
        )

        assert result.exit_code == 1
        # Should show helpful options to the user
        assert "invalid format" in result.stdout.lower() or "options" in result.stdout.lower()

    @patch("gdrive_catalog.cli.DriveScanner")
    @patch("gdrive_catalog.cli.DriveService")
    def test_scan_update_accepts_valid_csv_with_only_id(
        self, mock_drive_service_class, mock_scanner_class, tmp_path
    ):
        """Test scan with --update accepts CSV with at least 'id' column."""
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text("{}")

        output_file = tmp_path / "minimal.csv"

        # Create valid CSV with only 'id' column
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id"])
            writer.writeheader()
            writer.writerow({"id": "file1"})

        mock_scanner = MagicMock()
        mock_scanner.scan_drive.return_value = []
        mock_scanner_class.return_value = mock_scanner

        result = runner.invoke(
            app,
            [
                "scan",
                "--credentials",
                str(creds_file),
                "--output",
                str(output_file),
                "--update",
            ],
        )

        assert result.exit_code == 0
        # Should show that existing entries were loaded
        assert "1 existing entries" in result.stdout
