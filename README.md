# gdrive-catalog

[![Tests](https://github.com/FredDsR/gdrive-catalog/actions/workflows/run-pytest.yml/badge.svg)](https://github.com/FredDsR/gdrive-catalog/actions/workflows/run-pytest.yml)

A CLI tool to scan Google Drive storage and create CSV catalogs with comprehensive file metadata.

## Documentation

### Quick Links

- [Quick Start Guide](docs/QUICKSTART.md) - Get started in minutes
- [Usage Examples](docs/EXAMPLES.md) - Real-world usage scenarios

### README Sections

- [Features](#features)
- [Metadata Captured](#metadata-captured)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Setup Google Drive API](#setup-google-drive-api)
- [Usage](#usage)
- [First Run Authentication](#first-run-authentication)
- [CSV Output Format](#csv-output-format)
- [Development](#development)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)
- [License](#license)
- [Contributing](#contributing)

## Features

- 📁 Scan entire Google Drive or specific folders
- 📊 Export metadata to CSV format
- 🎵 Extract duration for video files
- 🔄 Update existing catalogs with new files
- 📝 Capture file metadata: name, size, duration, path, link, created_at
- 🚀 Built with Typer for an excellent CLI experience
- 📦 Uses `uv` as package manager for fast dependency management

## Metadata Captured

For each file, the tool captures:
- **id**: Google Drive file ID
- **name**: File name
- **size_bytes**: File size in bytes
- **duration_milliseconds**: Duration for audio/video files (when available)
- **path**: Full path within Google Drive
- **link**: Direct link for easy access
- **created_at**: File creation timestamp
- **mime_type**: File MIME type

## Prerequisites

1. **Python 3.12+**
2. **uv package manager** (install with `pip install uv`)
3. **Google Cloud Project with Drive API enabled**
   - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Google Drive API
   - Create OAuth 2.0 credentials (Desktop app type)
   - Download the credentials JSON file

## Installation

```bash
# Clone the repository
git clone https://github.com/FredDsR/gdrive-catalog.git
cd gdrive-catalog

# Install dependencies with uv
uv sync

# Install the package
uv pip install -e .
```

## Setup Google Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop app" as application type
   - Download the credentials JSON file
5. Save the downloaded file as `credentials.json` in your project directory

## Usage

> **Note:** After installing with `uv pip install -e .`, you can run commands directly as `gdrive-catalog`. Alternatively, use `uv run gdrive-catalog` if you haven't installed the package.

### Basic Usage

Scan your entire Google Drive and create a catalog:

```bash
gdrive-catalog scan
```

This creates a `catalog.csv` file with all file metadata.

### Scan Specific Folder

Scan a specific Google Drive folder by providing its ID:

```bash
gdrive-catalog scan --folder-id "your-folder-id-here"
```

To get a folder ID, open the folder in Google Drive and copy the ID from the URL:
`https://drive.google.com/drive/folders/FOLDER_ID_HERE`

### Custom Output File

Specify a custom output file path:

```bash
gdrive-catalog scan --output my-catalog.csv
```

### Update Existing Catalog

Update an existing catalog with new or modified files:

```bash
gdrive-catalog scan --update --output catalog.csv
```

This will:
- Load existing entries from the catalog
- Scan Google Drive for current files
- Merge the results (updating existing entries and adding new ones)
- Save back to the same file

### Custom Credentials Location

Use credentials from a different location:

```bash
gdrive-catalog scan --credentials /path/to/credentials.json
```

### All Options Combined

```bash
gdrive-catalog scan \
  --output reports/my-catalog.csv \
  --folder-id "abc123xyz" \
  --update \
  --credentials config/credentials.json
```

### Check Version

```bash
gdrive-catalog version
```

## First Run Authentication

On the first run, the tool will:
1. Open your web browser
2. Ask you to log in to your Google account
3. Request permission to read your Google Drive files
4. Save an authentication token (`token.pickle`) for future use

The token is saved locally and reused for subsequent runs.

## CSV Output Format

The generated CSV file contains the following columns:

| Column | Description |
|--------|-------------|
| id | Google Drive file ID |
| name | File name |
| size_bytes | File size in bytes |
| duration_milliseconds | Duration in milliseconds (for audio/video files) |
| path | Full path within Google Drive structure |
| link | Direct Google Drive link for easy access |
| created_at | ISO 8601 timestamp of file creation |
| mime_type | File MIME type |

## Development

### Install Development Dependencies

```bash
uv sync --dev
```

### Project Structure

```
gdrive-catalog/
├── gdrive_catalog/
│   ├── __init__.py       # Package initialization
│   ├── cli.py            # CLI interface with Typer
│   ├── drive_service.py  # Google Drive API wrapper
│   └── scanner.py        # File scanning and metadata extraction
├── main.py               # Entry point
├── pyproject.toml        # Project configuration
└── README.md            # Documentation
```

## Testing

### Running Tests

Run the test suite with coverage reporting:

```bash
uv run pytest
```

This will automatically run tests with coverage due to configuration in `pyproject.toml`.

### Test Options

```bash
# Run tests with verbose output
uv run pytest -v

# Run a specific test file
uv run pytest tests/test_scanner.py

# Run tests without coverage
uv run pytest tests/ --no-cov
```

### Coverage Requirements

The project requires a minimum of **80% code coverage**. Tests will fail if coverage drops below this threshold.

To generate an HTML coverage report:

```bash
uv run pytest --cov-report=html
# Open htmlcov/index.html in your browser
```

### Testing Patterns

The test suite follows these conventions:

- **Test Organization**: Tests are organized into classes by feature area (e.g., `TestScanDrive`, `TestExtractDuration`)
- **Naming**: Test methods use `test_<what_is_being_tested>_<expected_behavior>` naming
- **Mocking**: External services (Google Drive API) are mocked using `unittest.mock`
- **Fixtures**: pytest fixtures are used for common test setup
- **Assertions**: Tests use clear, single-purpose assertions

### Test Structure

```
tests/
├── test_basic.py          # Basic import and version tests
├── test_cli.py            # CLI command tests
├── test_drive_service.py  # Google Drive API wrapper tests
├── test_exceptions.py     # Custom exception tests
└── test_scanner.py        # File scanning logic tests
```

## Troubleshooting

### "Credentials file not found"
Make sure you have downloaded the OAuth credentials from Google Cloud Console and saved them as `credentials.json` in your project directory.

### "Access denied" or permission errors
Ensure your OAuth consent screen is properly configured and the Google Drive API is enabled for your project.

### Large Drive scans are slow
The tool scans recursively through all folders. For very large Drive accounts, this can take some time. The progress indicator will show scanning activity.

## Security Notes

- Never commit `credentials.json` or `token.pickle` to version control
- These files are automatically ignored by `.gitignore`
- The tool only requests read-only access to your Drive

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Issue or a Pull Request.

## Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for the CLI interface
- Uses [Google Drive API](https://developers.google.com/drive) for file access
- Managed with [uv](https://github.com/astral-sh/uv) package manager

## AI Notice

- We comprehensively made use of [Copilot](https://github.com/features/copilot) as coding agent for development, reviewing and documenting process.
