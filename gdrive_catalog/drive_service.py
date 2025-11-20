"""Google Drive API service wrapper."""

import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next time
            with open(self.token_path, "wb") as token:
                pickle.dump(creds, token)

        return build("drive", "v3", credentials=creds)

    def list_files(
        self,
        folder_id: Optional[str] = None,
        page_size: int = 1000,
        page_token: Optional[str] = None,
    ) -> Dict[str, Any]:
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
                        "createdTime, parents, webViewLink)"
                    ),
                )
                .execute()
            )

            return results
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")

    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
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
                        "parents, webViewLink, videoMediaMetadata, "
                        "audioMediaMetadata"
                    ),
                )
                .execute()
            )
            return file
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")

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
            raise Exception(f"An error occurred: {error}")
