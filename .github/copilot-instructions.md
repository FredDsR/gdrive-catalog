# Copilot Instructions for gdrive-catalog

This repository contains a CLI tool to scan Google Drive storage and create CSV catalogs with file metadata.

## Project Overview

- **Language**: Python 3.12+
- **Package Manager**: uv
- **CLI Framework**: Typer
- **Testing**: pytest
- **Linting/Formatting**: Ruff

## Quick Commands

```bash
# Install dependencies (including dev dependencies)
uv sync --dev

# Run the CLI
uv run gdrive-catalog [command]

# Run tests
uv run pytest tests/ -v

# Lint code
uv run ruff check .

# Format code
uv run ruff format .
```

## Code Style Guidelines

- Follow PEP 8 style guidelines
- Use Ruff for linting (`uv run ruff check .`) and formatting (`uv run ruff format .`)
- Add docstrings to all public functions, classes, and modules
- Use type hints for function parameters and return values
- Keep functions focused on a single responsibility
- Handle errors with specific exceptions defined in `gdrive_catalog/exceptions.py`

## Project Structure

```
gdrive_catalog/          # Main package
├── cli.py              # Command-line interface with Typer
├── drive_service.py    # Google Drive API integration
├── scanner.py          # Drive scanning logic
└── exceptions.py       # Custom exceptions
tests/                  # Test suite using pytest
main.py                 # Entry point
pyproject.toml         # Dependencies and tool configuration
```

## When Writing Code

1. **New features** should be added to the appropriate module in `gdrive_catalog/`
2. **CLI commands** should be added to `cli.py` using Typer decorators
3. **Google Drive API interactions** should go through `drive_service.py`
4. **Tests** should be added to `tests/` directory using pytest

## Security Considerations

- Never commit `credentials.json` or `token.pickle` files
- These files contain OAuth credentials and are listed in `.gitignore`
- Use environment variables for any sensitive configuration

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions/changes
- `refactor:` for code refactoring
- `chore:` for maintenance tasks

## Additional Context

- See `AGENTS.md` for detailed development workflow and conventions
- See `docs/QUICKSTART.md` for getting started guide
- See `docs/EXAMPLES.md` for usage examples
