# Quick Start Guide

Get started with gdrive-catalog in just a few steps!

## 1. Install

```bash
# Clone the repository
git clone https://github.com/FredDsR/gdrive-catalog.git
cd gdrive-catalog

# Install dependencies with uv
uv sync

# Install the CLI tool
uv pip install -e .
```

## 2. Set Up Google Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Drive API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Drive API" and enable it
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the credentials file
5. Save it as `credentials.json` in your project directory

## 3. Run Your First Scan

```bash
# Scan your entire Google Drive
gdrive-catalog scan

# Or scan a specific folder
gdrive-catalog scan --folder-id "your-folder-id"
```

On first run, your browser will open to authenticate. Grant read-only access to your Drive.

## 4. View Results

Open `catalog.csv` to see your Drive contents with metadata!

## Common Commands

```bash
# Create a new catalog
gdrive-catalog scan --output my-catalog.csv

# Update an existing catalog
gdrive-catalog scan --output my-catalog.csv --update

# Scan specific folder
gdrive-catalog scan --folder-id "abc123"

# Check version
gdrive-catalog version

# Get help
gdrive-catalog --help
gdrive-catalog scan --help
```

## What's in the CSV?

- **id**: Unique file identifier
- **name**: File name
- **size_bytes**: File size in bytes
- **duration_milliseconds**: Duration for video (if available)
- **path**: Full path within Drive
- **link**: Direct link to open the file
- **created_at**: When the file was created
- **mime_type**: File type

## Tips

- Use `--update` to refresh existing catalogs without full rescans
- Get folder IDs from Drive URLs: `https://drive.google.com/drive/folders/FOLDER_ID`
- Your credentials are cached in `token.pickle` after first authentication
- CSV files can be opened in Excel, Google Sheets, or analyzed with Python

## Need Help?

- Read [README.md](README.md) for full documentation
- See [EXAMPLES.md](EXAMPLES.md) for more usage examples
- Check [LICENSE](LICENSE) for license information (GPL v3)

## Security

- Never commit `credentials.json` or `token.pickle`
- These files are automatically ignored by git
- The tool only requests read-only access to your Drive
