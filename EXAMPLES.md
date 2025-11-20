# Example Usage

This document provides example usage scenarios for the gdrive-catalog tool.

## Setup

Before running the examples, make sure you have:

1. Installed the tool:
```bash
uv sync
uv pip install -e .
```

2. Set up Google Drive API credentials:
   - Created a project in Google Cloud Console
   - Enabled Google Drive API
   - Downloaded OAuth credentials as `credentials.json`

## Basic Examples

### Example 1: Scan Entire Drive

Scan your entire Google Drive and create a catalog:

```bash
uv run gdrive-catalog scan
```

This creates `catalog.csv` with all your files.

### Example 2: Scan Specific Folder

Scan only a specific folder (replace `FOLDER_ID` with your folder ID from the URL):

```bash
uv run gdrive-catalog scan --folder-id "1a2b3c4d5e6f7g8h9i0j"
```

### Example 3: Custom Output Location

Save the catalog to a specific location:

```bash
uv run gdrive-catalog scan --output reports/drive-catalog-2024.csv
```

### Example 4: Update Existing Catalog

Update an existing catalog with new or modified files:

```bash
# First scan
uv run gdrive-catalog scan --output my-catalog.csv

# Later, update it
uv run gdrive-catalog scan --output my-catalog.csv --update
```

### Example 5: Scan with Custom Credentials

Use credentials from a different location:

```bash
uv run gdrive-catalog scan --credentials config/my-credentials.json
```

### Example 6: Complete Example

Scan a specific folder, update existing catalog, with custom paths:

```bash
uv run gdrive-catalog scan \
  --folder-id "1a2b3c4d5e6f7g8h9i0j" \
  --output reports/media-library.csv \
  --update \
  --credentials ~/Documents/drive-credentials.json
```

## Expected CSV Output

The generated CSV will look like this:

```csv
id,name,size_bytes,duration_seconds,path,link,created_at,mime_type
abc123,video.mp4,52428800,120.5,/Videos/video.mp4,https://drive.google.com/...,2024-01-15T10:30:00.000Z,video/mp4
def456,audio.mp3,5242880,180.2,/Music/audio.mp3,https://drive.google.com/...,2024-01-16T14:20:00.000Z,audio/mpeg
ghi789,document.pdf,1048576,,/Documents/document.pdf,https://drive.google.com/...,2024-01-17T09:15:00.000Z,application/pdf
```

## Tips

1. **For large Drive accounts**: The first scan may take several minutes. Be patient!

2. **Finding folder IDs**: Open a folder in Google Drive and copy the ID from the URL:
   ```
   https://drive.google.com/drive/folders/FOLDER_ID_HERE
   ```

3. **Regular updates**: Use `--update` flag to keep your catalog current without rescanning everything.

4. **Analysis**: Import the CSV into Excel, Google Sheets, or use Python/pandas for analysis:
   ```python
   import pandas as pd
   df = pd.read_csv('catalog.csv')
   
   # Total storage used
   total_gb = df['size_bytes'].sum() / (1024**3)
   print(f"Total storage: {total_gb:.2f} GB")
   
   # Video files only
   videos = df[df['mime_type'].str.startswith('video/')]
   print(f"Total videos: {len(videos)}")
   ```

## Troubleshooting

### First-time authentication

On first run, a browser window will open asking you to:
1. Sign in to your Google account
2. Grant read-only access to Google Drive
3. The token will be saved locally for future use

### Permission errors

If you get permission errors, verify:
- Google Drive API is enabled in your Cloud Console
- OAuth consent screen is configured
- credentials.json is from a Desktop app type credential
