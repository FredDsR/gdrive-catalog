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

"""Google Drive API service wrapper."""

import pickle
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from gdrive_catalog.exceptions import FileDownloadError, FileListError, FileMetadataError

# If modifying these scopes, delete the token.pickle file.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


class DriveService:
    """Wrapper for Google Drive API service."""

    def __init__(self, credentials_path: str = "credentials.json"):
        """
        Initialize Drive service with authentication.

        Args:
            credentials_path: Path to OAuth2 credentials JSON file
        """
        self.credentials_path = credentials_path
        self.token_path = "token.pickle"
        self.service = self._authenticate()

    def _authenticate(self):
        """Authenticate and return Drive API service."""
        creds = None

        # Load token from file if it exists
        if Path(self.token_path).exists():
            with open(self.token_path, "rb") as token:
                creds = pickle.load(token)

        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for next time
            with open(self.token_path, "wb") as token:
                pickle.dump(creds, token)

        return build("drive", "v3", credentials=creds)

    def list_files(
        self,
        folder_id: str | None = None,
        page_size: int = 1000,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """
        List files in Google Drive.

        Args:
            folder_id: Optional folder ID to list files from
            page_size: Number of files per page
            page_token: Token for pagination

        Returns:
            Dictionary with 'files' and 'nextPageToken'
        """
        try:
            query = "trashed=false"
            if folder_id:
                query = f"'{folder_id}' in parents and trashed=false"

            results = (
                self.service.files()
                .list(
                    q=query,
                    pageSize=page_size,
                    pageToken=page_token,
                    fields=(
                        "nextPageToken, files(id, name, mimeType, size, "
                        "createdTime, parents, webViewLink, videoMediaMetadata)"
                    ),
                )
                .execute()
            )

            return results
        except HttpError as error:
            raise FileListError(
                message=str(error),
                folder_id=folder_id,
                original_error=error,
            ) from error

    def get_file_metadata(self, file_id: str) -> dict[str, Any]:
        """
        Get detailed metadata for a specific file.

        Args:
            file_id: Google Drive file ID

        Returns:
            File metadata dictionary
        """
        try:
            file = (
                self.service.files()
                .get(
                    fileId=file_id,
                    fields=(
                        "id, name, mimeType, size, createdTime, "
                        "parents, webViewLink, videoMediaMetadata"
                    ),
                )
                .execute()
            )
            return file
        except HttpError as error:
            raise FileMetadataError(
                message=str(error),
                file_id=file_id,
                original_error=error,
            ) from error

    def download_file(self, file_id: str) -> bytes:
        """
        Download file content.

        Args:
            file_id: Google Drive file ID

        Returns:
            File content as bytes
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            return request.execute()
        except HttpError as error:
            raise FileDownloadError(
                message=str(error),
                file_id=file_id,
                original_error=error,
            ) from error
