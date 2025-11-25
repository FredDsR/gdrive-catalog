# AGENTS.md

Google Drive catalog scanner - creates CSV reports of Drive contents using Python and the Google Drive API.

## Setup commands

- Install dependencies: `uv sync`
- Run the scanner: `uv run python main.py` or `uv run python -m gdrive_catalog`
- Run tests: `uv run pytest` or `uv run pytest tests/`
- Run specific test: `uv run pytest tests/test_basic.py -v`
- Run linter: `uv run ruff check .`
- Auto-fix issues: `uv run ruff check --fix .`
- Format code: `uv run ruff format .`

## Project structure

```
gdrive_catalog/          # Main package
├── cli.py              # Command-line interface
├── drive_service.py    # Google Drive API integration
└── scanner.py          # Drive scanning logic
tests/                  # Test suite
main.py                 # Entry point
pyproject.toml         # Dependencies and config
```

## Testing instructions

- Run `pytest` before committing changes
- Add unit tests for new functionality in `tests/` directory
- Use pytest as the testing framework
- Aim for good test coverage of core functionality

## Code style

- Follow PEP 8 style guidelines
- Use Ruff for linting and formatting (`uv run ruff check .` and `uv run ruff format .`)
- Add docstrings to all functions, classes, and modules
- Use clear, self-documenting variable names
- Keep functions focused on a single responsibility
- Handle errors with specific exceptions and clear messages

## Google Drive API guidelines

- Credentials in `credentials.json` (never commit)
- OAuth generates `token.json` (keep local)
- Handle API rate limits gracefully
- Use `drive_service.py` for all Drive API interactions
- Implement retry logic for transient failures

## Development workflow

1. Create a feature branch using conventional branch naming
2. Read relevant code files before making changes
3. Write or update tests for new functionality
4. Run `uv run ruff check .` and `uv run ruff format .` to lint and format code
5. Run `uv run pytest` to verify all tests pass
6. Update documentation (README.md, EXAMPLES.md) as needed
7. Test changes thoroughly before committing
8. Commit using conventional commit messages

## Conventional commits

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for all commit messages:

**Format**: `<type>[optional scope]: <description>`

**Common types**:
- `feat:` - New feature for the user
- `fix:` - Bug fix
- `docs:` - Documentation only changes
- `style:` - Code style changes (formatting, missing semicolons, etc.)
- `refactor:` - Code change that neither fixes a bug nor adds a feature
- `test:` - Adding or updating tests
- `chore:` - Changes to build process, dependencies, or auxiliary tools
- `perf:` - Performance improvements
- `ci:` - Changes to CI/CD configuration

**Examples**:
- `feat(scanner): add support for shared drives`
- `fix(cli): handle empty Drive folders correctly`
- `docs: update QUICKSTART.md with installation steps`
- `test(drive_service): add unit tests for rate limiting`
- `refactor(scanner): simplify file filtering logic`
- `chore(deps): update google-api-python-client to 2.100.0`

**Breaking changes**: Add `!` after type or add `BREAKING CHANGE:` in footer
- `feat(api)!: change scanner output format to JSON`

## Conventional branches

Use descriptive branch names with conventional prefixes:

**Format**: `<type>/<short-description>`

**Branch types**:
- `feature/` or `feat/` - New features
- `fix/` or `bugfix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or updates
- `chore/` - Maintenance tasks
- `hotfix/` - Urgent production fixes

**Examples**:
- `feature/shared-drive-support`
- `fix/empty-folder-handling`
- `docs/update-quickstart`
- `refactor/simplify-scanner`
- `test/drive-service-coverage`
- `chore/update-dependencies`

**Branch naming guidelines**:
- Use lowercase with hyphens (kebab-case)
- Keep names concise but descriptive
- Avoid special characters except hyphens
- Delete branches after merging

## Security notes

- Never commit credentials (`credentials.json`) or tokens (`token.json`)
- Validate and sanitize user input
- Use environment variables for sensitive configuration
- Follow principle of least privilege for API scopes

## Common tasks

### Adding a feature
1. Create a feature branch: `git checkout -b feature/descriptive-name`
2. Identify where it fits in the architecture
3. Write tests first (TDD recommended)
4. Implement the feature
5. Update CLI if user-facing (`cli.py`)
6. Document in `EXAMPLES.md` if relevant
7. Commit with conventional commit: `feat(scope): add description`

### Fixing a bug
1. Create a bugfix branch: `git checkout -b fix/issue-description`
2. Write a test that reproduces the bug
3. Fix the bug
4. Verify the test passes
5. Check for similar issues elsewhere
6. Commit with conventional commit: `fix(scope): resolve issue description`

### Dependencies
- Add to `pyproject.toml`
- Keep minimal and well-justified
- Document why each is needed
