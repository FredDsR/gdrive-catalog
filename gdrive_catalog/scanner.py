"""Scanner for Google Drive files with metadata extraction."""

import logging
from typing import Any, Dict, Optional

from gdrive_catalog.drive_service import DriveService

logger = logging.getLogger(__name__)


class DriveScanner:
    """Scanner to catalog files from Google Drive."""

    # MIME types for audio and video files
    AUDIO_MIME_TYPES = {
        "audio/mpeg",
        "audio/mp3",
        "audio/mp4",
        "audio/wav",
        "audio/flac",
        "audio/ogg",
        "audio/aac",
        "audio/x-m4a",
        "audio/webm",
    }

    VIDEO_MIME_TYPES = {
        "video/mp4",
        "video/mpeg",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-matroska",
        "video/webm",
        "video/3gpp",
    }

    def __init__(self, drive_service: DriveService):
        """
        Initialize scanner with Drive service.

        Args:
            drive_service: Initialized DriveService instance
        """
        self.drive_service = drive_service
        self.folder_cache: Dict[str, Dict[str, Any]] = {}

    def scan_drive(self, folder_id: Optional[str] = None) -> list[Dict[str, Any]]:
        """
        Recursively scan Google Drive and collect file metadata.

        Args:
            folder_id: Optional folder ID to start scanning from

        Returns:
            List of dictionaries containing file metadata
        """
        all_files = []
        folders_to_scan = [folder_id] if folder_id else [None]
        scanned_folders = set()

        while folders_to_scan:
            current_folder = folders_to_scan.pop(0)

            # Avoid scanning the same folder twice
            if current_folder in scanned_folders:
                continue
            scanned_folders.add(current_folder)

            # Get files in current folder
            page_token = None
            while True:
                results = self.drive_service.list_files(
                    folder_id=current_folder, page_token=page_token
                )

                for file in results.get("files", []):
                    mime_type = file.get("mimeType", "")

                    # If it's a folder, add to scanning queue
                    if mime_type == "application/vnd.google-apps.folder":
                        folders_to_scan.append(file["id"])
                        continue

                    # Skip Google Workspace files (Docs, Sheets, etc.)
                    if mime_type.startswith("application/vnd.google-apps."):
                        continue

                    # Process regular files
                    file_data = self._extract_file_data(file)
                    all_files.append(file_data)

                page_token = results.get("nextPageToken")
                if not page_token:
                    break

        return all_files

    def _extract_file_data(self, file: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant metadata from a file.

        Args:
            file: File metadata from Drive API

        Returns:
            Dictionary with extracted and formatted metadata
        """
        file_id = file.get("id", "")
        mime_type = file.get("mimeType", "")

        # Get basic metadata
        data = {
            "id": file_id,
            "name": file.get("name", ""),
            "size_bytes": file.get("size", "0"),
            "duration_seconds": "",
            "path": self._build_file_path(file),
            "link": file.get(
                "webViewLink", f"https://drive.google.com/file/d/{file_id}/view"
            ),
            "created_at": file.get("createdTime", ""),
            "mime_type": mime_type,
        }

        # Try to extract duration for audio/video files
        if mime_type in self.AUDIO_MIME_TYPES or mime_type in self.VIDEO_MIME_TYPES:
            duration = self._extract_duration(file)
            if duration:
                data["duration_seconds"] = str(duration)

        return data

    def _extract_duration(self, file: Dict[str, Any]) -> Optional[float]:
        """
        Extract duration from audio/video file metadata.

        Args:
            file: File metadata from Drive API

        Returns:
            Duration in seconds, or None if not available
        """
        # Try to get duration from Drive API metadata for video files
        video_metadata = file.get("videoMediaMetadata", {})
        if "durationMillis" in video_metadata:
            return float(video_metadata["durationMillis"]) / 1000.0

        # Try to get duration from Drive API metadata for audio files
        audio_metadata = file.get("audioMediaMetadata", {})
        if "durationMillis" in audio_metadata:
            return float(audio_metadata["durationMillis"]) / 1000.0

        return None

    def _build_file_path(self, file: Dict[str, Any]) -> str:
        """
        Build the full path of a file within Drive.

        Args:
            file: File metadata from Drive API

        Returns:
            Full path string
        """
        parents = file.get("parents", [])
        if not parents:
            return f"/{file.get('name', '')}"

        path_parts = [file.get("name", "")]
        current_parent = parents[0]

        # Traverse up the folder hierarchy
        max_depth = 100  # Prevent infinite loops
        depth = 0
        visited_folders = set()

        while current_parent and depth < max_depth:
            depth += 1

            # Detect circular references
            if current_parent in visited_folders:
                break
            visited_folders.add(current_parent)

            # Check cache first
            if current_parent in self.folder_cache:
                folder_data = self.folder_cache[current_parent]
                folder_name = folder_data["name"]
                current_parent = folder_data.get("parent")
            else:
                # Fetch folder metadata
                try:
                    folder = (
                        self.drive_service.service.files()
                        .get(fileId=current_parent, fields="name, parents")
                        .execute()
                    )
                    folder_name = folder.get("name", "")

                    # Get parent's parent
                    folder_parents = folder.get("parents", [])
                    parent_id = folder_parents[0] if folder_parents else None

                    # Cache both name and parent
                    self.folder_cache[current_parent] = {
                        "name": folder_name,
                        "parent": parent_id,
                    }

                    current_parent = parent_id
                except Exception as e:
                    # If we can't fetch parent, log and stop here
                    logger.debug(
                        "Failed to fetch parent folder %s: %s", current_parent, e
                    )
                    break

            if folder_name:
                path_parts.insert(0, folder_name)

        # Build path
        path = "/" + "/".join(path_parts)
        return path
