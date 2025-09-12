import click
import sys
from pathlib import Path

@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
@click.option('-o', '--output', help='Output file path')
@click.option('-v', '--version', is_flag=True, help='Show version')
@click.option('--include', help='Include files matching pattern (e.g., "*.js,*.py")')
def main(paths, output, version, include):
    """Repository Context Packager - Convert repos to LLM-friendly format"""
    
    if version:
        click.echo("repo-context-packager v0.1.0")
        return
    
    # If no paths provided, use current directory
    if not paths:
        paths = ['.']
    
    # Import here to avoid circular imports
    from .main import process_repositories
    
    try:
        process_repositories(
            paths=list(paths),
            output_file=output,
            include=include
        )
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()