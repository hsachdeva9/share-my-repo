import click
import sys
from pathlib import Path
from main import process_repositories


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
@click.option('-o', '--output', help='Output file path')
@click.option('-v', '--version', is_flag=True, help='Show version')
@click.option('--include', help='Include files matching pattern (e.g., "*.js,*.py")')
@click.option('--exclude', help='Exclude files matching pattern (e.g., "*.log,node_modules")')
@click.option('--max-file-size', type=int, default=16384, help='Maximum file size in bytes (default: 16384)')
@click.option('--format', 'output_format', type=click.Choice(['markdown', 'json', 'yaml']),
              default='markdown', help='Output format')
@click.option('--tokens', is_flag=True, help='Show estimated token count')
@click.option(
    "-r", "--recent",
    is_flag=True,
    help="Include only files modified in the last 7 days"
)
@click.option('--line-numbers', '-l', is_flag=True, help='Show line numbers in file output')


def main(paths, output, version, include, exclude, max_file_size, output_format, tokens, recent, line_numbers):
    """Repository Context Packager - Convert repos to LLM-friendly format"""

    if version:
        click.echo("share-my-repo v0.1.0")
        return

    # If no paths provided, use current directory
    if not paths:
        paths = ['.']

    try:
        process_repositories(
            paths=list(paths),
            output_file=output,
            include=include,
            exclude=exclude,
            max_file_size=max_file_size,
            output_format=output_format,
            show_tokens=tokens,
            recent=recent,
            line_numbers=line_numbers
        )
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
