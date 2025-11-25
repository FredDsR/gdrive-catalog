"""CLI interface for Google Drive Catalog."""

import csv
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from gdrive_catalog.drive_service import DriveService
from gdrive_catalog.scanner import DriveScanner

app = typer.Typer(
    name="gdrive-catalog",
    help="Scan Google Drive storage and create CSV catalogs with file metadata.",
)
console = Console()


@app.command()
def scan(
    output: Path = typer.Option(
        "catalog.csv",
        "--output",
        "-o",
        help="Output CSV file path",
    ),
    folder_id: str | None = typer.Option(
        None,
        "--folder-id",
        "-f",
        help="Google Drive folder ID to scan (scans root if not specified)",
    ),
    update: bool = typer.Option(
        False,
        "--update",
        "-u",
        help="Update existing catalog file instead of creating new one",
    ),
    credentials: Path = typer.Option(
        "credentials.json",
        "--credentials",
        "-c",
        help="Path to Google OAuth credentials JSON file",
    ),
):
    """
    Scan Google Drive and generate a CSV catalog with file metadata.

    The catalog includes: name, size (bytes), duration (for video),
    path, link, and created_at timestamp.
    """
    try:
        # Check if credentials file exists
        if not credentials.exists():
            console.print(f"[red]Error: Credentials file not found at {credentials}[/red]")
            console.print(
                "\n[yellow]To use this tool, you need to:[/yellow]\n"
                "1. Create a project in Google Cloud Console\n"
                "2. Enable the Google Drive API\n"
                "3. Create OAuth 2.0 credentials (Desktop app)\n"
                "4. Download the credentials JSON file\n"
                "5. Save it as 'credentials.json' or specify path with --credentials\n"
            )
            raise typer.Exit(1)

        # Initialize services
        console.print("[cyan]Initializing Google Drive connection...[/cyan]")
        drive_service = DriveService(credentials_path=str(credentials))
        scanner = DriveScanner(drive_service)

        # Load existing data if updating
        existing_data = {}
        if update and output.exists():
            console.print(f"[cyan]Loading existing catalog from {output}...[/cyan]")
            with open(output, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_data[row["id"]] = row
            console.print(f"[green]Loaded {len(existing_data)} existing entries[/green]")

        # Scan Drive
        console.print("[cyan]Scanning Google Drive...[/cyan]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Scanning files...", total=None)
            files = scanner.scan_drive(folder_id=folder_id)
            progress.update(task, completed=True)

        console.print(f"[green]Found {len(files)} files[/green]")

        # Merge with existing data if updating
        if update:
            # Update existing entries and add new ones
            for file in files:
                file_id = file["id"]
                existing_data[file_id] = file
            files = list(existing_data.values())
            console.print(f"[green]Merged catalog contains {len(files)} total entries[/green]")

        # Write to CSV
        console.print(f"[cyan]Writing catalog to {output}...[/cyan]")
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "id",
                "name",
                "size_bytes",
                "duration_milliseconds",
                "path",
                "link",
                "created_at",
                "mime_type",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(files)

        console.print(f"[green]✓ Catalog saved to {output}[/green]")
        console.print(f"[green]Total files cataloged: {len(files)}[/green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Scan interrupted by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    from gdrive_catalog import __version__

    console.print(f"gdrive-catalog version {__version__}")


def main():
    """Main entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
