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

"""Google Drive Catalog - CLI tool to catalog files in Google Drive storage."""

__version__ = "0.1.0"

from gdrive_catalog.exceptions import (
    CSVValidationError,
    DriveServiceError,
    FileDownloadError,
    FileListError,
    FileMetadataError,
)

__all__ = [
    "__version__",
    "CSVValidationError",
    "DriveServiceError",
    "FileDownloadError",
    "FileListError",
    "FileMetadataError",
]
