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

"""CSV validation for Google Drive catalog files.

This module provides reusable validation functionality for CSV files
used by the gdrive-catalog application. It defines the expected schema
and provides validation functions that can be used throughout the application.
"""

import csv
from pathlib import Path
from typing import Any

from gdrive_catalog.exceptions import CSVValidationError

# Expected CSV schema for catalog files
# This defines the columns that must be present in a valid catalog CSV
CATALOG_REQUIRED_COLUMNS = frozenset({"id"})

# All columns that are expected in a standard catalog CSV file
# Used for writing CSV files and for validation reference
CATALOG_FIELDNAMES = (
    "id",
    "name",
    "size_bytes",
    "duration_milliseconds",
    "path",
    "link",
    "created_at",
    "mime_type",
)


def validate_csv_headers(
    headers: list[str] | None,
    required_columns: frozenset[str] = CATALOG_REQUIRED_COLUMNS,
    file_path: str | None = None,
) -> None:
    """
    Validate that CSV headers contain all required columns.

    This function checks that the provided headers include all columns
    required for processing catalog data. It raises a CSVValidationError
    with detailed information if validation fails.

    Args:
        headers: List of column names from the CSV file.
        required_columns: Set of column names that must be present.
        file_path: Optional path to the CSV file (for error messages).

    Raises:
        CSVValidationError: If headers are None/empty or missing required columns.

    Example:
        >>> validate_csv_headers(["id", "name", "size_bytes"])  # OK
        >>> validate_csv_headers(["name", "size_bytes"])  # Raises CSVValidationError
    """
    if headers is None:
        raise CSVValidationError(
            "CSV file is empty or has no headers",
            file_path=file_path,
            missing_columns=required_columns,
            actual_columns=set(),
        )

    actual_columns = set(headers)
    missing_columns = required_columns - actual_columns

    if missing_columns:
        raise CSVValidationError(
            "CSV file is missing required columns",
            file_path=file_path,
            missing_columns=missing_columns,
            actual_columns=actual_columns,
        )


def load_catalog_csv(file_path: Path | str) -> dict[str, dict[str, Any]]:
    """
    Load and validate a catalog CSV file, returning entries indexed by ID.

    This function reads a CSV file, validates it has the required schema,
    and returns its contents as a dictionary keyed by the 'id' column.
    This is the recommended way to load existing catalog data.

    Args:
        file_path: Path to the CSV file to load.

    Returns:
        Dictionary mapping file IDs to their row data.

    Raises:
        CSVValidationError: If the CSV file is invalid or missing required columns.
        FileNotFoundError: If the file doesn't exist.
        UnicodeDecodeError: If the file contains invalid UTF-8 content.

    Example:
        >>> data = load_catalog_csv("catalog.csv")
        >>> print(data["file123"]["name"])
        "document.pdf"
    """
    file_path = Path(file_path)
    str_path = str(file_path)

    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Validate headers before processing rows
        validate_csv_headers(reader.fieldnames, file_path=str_path)

        # Process rows and build dictionary keyed by ID
        data: dict[str, dict[str, Any]] = {}
        for row in reader:
            file_id = row.get("id")
            if file_id:
                data[file_id] = row

        return data
