"""Tests for the CSV validator module."""

import csv

import pytest

from gdrive_catalog.csv_validator import (
    CATALOG_FIELDNAMES,
    CATALOG_REQUIRED_COLUMNS,
    load_catalog_csv,
    validate_csv_headers,
)
from gdrive_catalog.exceptions import CSVValidationError


class TestCatalogSchema:
    """Tests for the catalog schema constants."""

    def test_required_columns_contains_id(self):
        """Test that 'id' is in the required columns."""
        assert "id" in CATALOG_REQUIRED_COLUMNS

    def test_required_columns_is_frozen_set(self):
        """Test that required columns is a frozenset (immutable)."""
        assert isinstance(CATALOG_REQUIRED_COLUMNS, frozenset)

    def test_fieldnames_contains_all_expected_columns(self):
        """Test that fieldnames contains all expected columns."""
        expected = {
            "id",
            "name",
            "size_bytes",
            "duration_milliseconds",
            "path",
            "link",
            "created_at",
            "mime_type",
        }
        assert set(CATALOG_FIELDNAMES) == expected

    def test_fieldnames_is_tuple(self):
        """Test that fieldnames is a tuple (ordered and immutable)."""
        assert isinstance(CATALOG_FIELDNAMES, tuple)

    def test_required_columns_subset_of_fieldnames(self):
        """Test that all required columns are in the fieldnames."""
        assert CATALOG_REQUIRED_COLUMNS <= set(CATALOG_FIELDNAMES)


class TestValidateCsvHeaders:
    """Tests for the validate_csv_headers function."""

    def test_valid_headers_with_all_columns(self):
        """Test validation passes with all expected columns."""
        headers = list(CATALOG_FIELDNAMES)
        # Should not raise
        validate_csv_headers(headers)

    def test_valid_headers_with_minimum_required(self):
        """Test validation passes with only required columns."""
        headers = ["id"]
        # Should not raise
        validate_csv_headers(headers)

    def test_valid_headers_with_extra_columns(self):
        """Test validation passes with extra columns beyond required."""
        headers = ["id", "extra_column", "another_extra"]
        # Should not raise
        validate_csv_headers(headers)

    def test_invalid_headers_none(self):
        """Test validation fails when headers are None."""
        with pytest.raises(CSVValidationError) as exc_info:
            validate_csv_headers(None)

        assert "empty or has no headers" in str(exc_info.value)
        assert exc_info.value.missing_columns == CATALOG_REQUIRED_COLUMNS

    def test_invalid_headers_missing_id(self):
        """Test validation fails when 'id' column is missing."""
        headers = ["name", "size_bytes", "path"]

        with pytest.raises(CSVValidationError) as exc_info:
            validate_csv_headers(headers)

        assert "missing required columns" in str(exc_info.value)
        assert "id" in exc_info.value.missing_columns
        assert exc_info.value.actual_columns == {"name", "size_bytes", "path"}

    def test_invalid_headers_empty_list(self):
        """Test validation fails when headers list is empty (missing id)."""
        headers = []

        with pytest.raises(CSVValidationError) as exc_info:
            validate_csv_headers(headers)

        assert "id" in exc_info.value.missing_columns

    def test_file_path_in_error_message(self):
        """Test that file path is included in error message."""
        with pytest.raises(CSVValidationError) as exc_info:
            validate_csv_headers(["name"], file_path="/path/to/file.csv")

        assert "/path/to/file.csv" in str(exc_info.value)
        assert exc_info.value.file_path == "/path/to/file.csv"

    def test_custom_required_columns(self):
        """Test validation with custom required columns."""
        headers = ["id", "name"]
        custom_required = frozenset({"id", "name", "custom"})

        with pytest.raises(CSVValidationError) as exc_info:
            validate_csv_headers(headers, required_columns=custom_required)

        assert "custom" in exc_info.value.missing_columns
        assert "id" not in exc_info.value.missing_columns
        assert "name" not in exc_info.value.missing_columns


class TestLoadCatalogCsv:
    """Tests for the load_catalog_csv function."""

    def test_load_valid_csv(self, tmp_path):
        """Test loading a valid catalog CSV file."""
        csv_file = tmp_path / "catalog.csv"

        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CATALOG_FIELDNAMES)
            writer.writeheader()
            writer.writerow(
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
            )

        data = load_catalog_csv(csv_file)

        assert len(data) == 1
        assert "file1" in data
        assert data["file1"]["name"] == "test.pdf"
        assert data["file1"]["size_bytes"] == "1024"

    def test_load_csv_with_multiple_rows(self, tmp_path):
        """Test loading a CSV with multiple entries."""
        csv_file = tmp_path / "catalog.csv"

        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CATALOG_FIELDNAMES)
            writer.writeheader()
            for i in range(3):
                writer.writerow(
                    {
                        "id": f"file{i}",
                        "name": f"file{i}.pdf",
                        "size_bytes": str(1024 * (i + 1)),
                        "duration_milliseconds": "",
                        "path": f"/file{i}.pdf",
                        "link": f"https://drive.google.com/file/d/file{i}/view",
                        "created_at": "2024-01-15T10:00:00.000Z",
                        "mime_type": "application/pdf",
                    }
                )

        data = load_catalog_csv(csv_file)

        assert len(data) == 3
        assert "file0" in data
        assert "file1" in data
        assert "file2" in data

    def test_load_csv_missing_id_column(self, tmp_path):
        """Test that loading a CSV without 'id' column raises error."""
        csv_file = tmp_path / "invalid.csv"

        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "size_bytes"])
            writer.writeheader()
            writer.writerow({"name": "test.pdf", "size_bytes": "1024"})

        with pytest.raises(CSVValidationError) as exc_info:
            load_catalog_csv(csv_file)

        assert "id" in exc_info.value.missing_columns
        assert str(csv_file) in str(exc_info.value)

    def test_load_empty_csv_with_headers(self, tmp_path):
        """Test loading an empty CSV file (headers only) returns empty dict."""
        csv_file = tmp_path / "empty.csv"

        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CATALOG_FIELDNAMES)
            writer.writeheader()

        data = load_catalog_csv(csv_file)

        assert data == {}

    def test_load_csv_empty_file(self, tmp_path):
        """Test loading a completely empty CSV file raises error."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        with pytest.raises(CSVValidationError) as exc_info:
            load_catalog_csv(csv_file)

        assert "empty or has no headers" in str(exc_info.value)

    def test_load_csv_file_not_found(self, tmp_path):
        """Test that loading non-existent file raises FileNotFoundError."""
        csv_file = tmp_path / "nonexistent.csv"

        with pytest.raises(FileNotFoundError):
            load_catalog_csv(csv_file)

    def test_load_csv_with_extra_columns(self, tmp_path):
        """Test loading a CSV with extra columns works."""
        csv_file = tmp_path / "extra.csv"

        fieldnames = ["id", "name", "extra_column"]
        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({"id": "file1", "name": "test.pdf", "extra_column": "value"})

        data = load_catalog_csv(csv_file)

        assert len(data) == 1
        assert data["file1"]["extra_column"] == "value"

    def test_load_csv_skips_rows_without_id(self, tmp_path):
        """Test that rows with empty 'id' are skipped."""
        csv_file = tmp_path / "mixed.csv"

        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "name"])
            writer.writeheader()
            writer.writerow({"id": "file1", "name": "valid.pdf"})
            writer.writerow({"id": "", "name": "empty_id.pdf"})
            writer.writerow({"id": "file2", "name": "another.pdf"})

        data = load_catalog_csv(csv_file)

        assert len(data) == 2
        assert "file1" in data
        assert "file2" in data

    def test_load_csv_path_as_string(self, tmp_path):
        """Test that load_catalog_csv accepts string paths."""
        csv_file = tmp_path / "catalog.csv"

        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "name"])
            writer.writeheader()
            writer.writerow({"id": "file1", "name": "test.pdf"})

        # Pass as string, not Path
        data = load_catalog_csv(str(csv_file))

        assert len(data) == 1
        assert "file1" in data


class TestCSVValidationErrorAttributes:
    """Tests for CSVValidationError exception attributes."""

    def test_error_has_message_attribute(self):
        """Test that error stores the message."""
        error = CSVValidationError("Test message")
        assert error.message == "Test message"

    def test_error_has_file_path_attribute(self):
        """Test that error stores the file path."""
        error = CSVValidationError("Test", file_path="/path/to/file.csv")
        assert error.file_path == "/path/to/file.csv"

    def test_error_has_missing_columns_attribute(self):
        """Test that error stores missing columns."""
        error = CSVValidationError("Test", missing_columns={"id", "name"})
        assert error.missing_columns == {"id", "name"}

    def test_error_has_actual_columns_attribute(self):
        """Test that error stores actual columns."""
        error = CSVValidationError("Test", actual_columns={"name", "size"})
        assert error.actual_columns == {"name", "size"}

    def test_error_defaults_for_optional_attributes(self):
        """Test that optional attributes default to empty values."""
        error = CSVValidationError("Test")
        assert error.file_path is None
        assert error.missing_columns == set()
        assert error.actual_columns == set()

    def test_error_message_includes_file_path(self):
        """Test that error message includes file path when provided."""
        error = CSVValidationError("Invalid format", file_path="/data/file.csv")
        assert "Invalid CSV file '/data/file.csv'" in str(error)

    def test_error_message_includes_missing_columns(self):
        """Test that error message includes missing columns when provided."""
        error = CSVValidationError("Missing columns", missing_columns={"id", "name"})
        assert "['id', 'name']" in str(error)

    def test_error_inheritance(self):
        """Test that CSVValidationError inherits from Exception."""
        error = CSVValidationError("Test")
        assert isinstance(error, Exception)

    def test_error_can_be_raised_and_caught(self):
        """Test that exception can be raised and caught properly."""
        with pytest.raises(CSVValidationError, match=r"Test error"):
            raise CSVValidationError("Test error")
