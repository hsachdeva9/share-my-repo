import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

from file_processor import FileProcessor
from git_info import GitInfo
from formatter import OutputFormatter

# TOML loader: tomllib (Python 3.11+) or tomli fallback
try:
    import tomllib as _toml_lib
except Exception:
    try:
        import tomli as _toml_lib
    except Exception:
        _toml_lib = None

VALID_FORMATS = ['markdown', 'json', 'yaml']

def _load_toml_config_from_cwd() -> Dict[str, Any]:
    """Search the current working directory for a TOML dotfile config."""
    cwd = Path.cwd()
    candidates = list(cwd.glob('.share-my-repo*.toml')) + list(cwd.glob('.*config.toml'))
    if not candidates:
        return {}
    config_path = candidates[0]

    if _toml_lib is None:
        print("TOML parser not available: please install tomli or use Python 3.11+.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(config_path, 'rb') as f:
            config = _toml_lib.load(f)
    except Exception as e:
        print(f"Error: Failed to parse TOML config {config_path}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded config from {config_path}", file=sys.stderr)
    return config or {}

def _coerce_list_or_string_to_csv(val) -> Optional[str]:
    """Accept either a string or a list of strings, return a CSV string or None."""
    if val is None:
        return None
    if isinstance(val, str):
        return val
    if isinstance(val, (list, tuple)):
        return ",".join(str(x) for x in val if x is not None)
    return str(val)

def process_repositories(paths: List[str],
                        output_file: Optional[str] = None,
                        include: Optional[str] = None,
                        exclude: Optional[str] = None,
                        max_file_size: int = 16384,
                        output_format: str = 'markdown',
                        show_tokens: bool = False,
                        recent: bool = False,
                        line_numbers: bool = False,
                        preview: Optional[int] = None):
    """Main processing function with TOML and .gitignore support."""

    # Default use_gitignore
    use_gitignore = False

    # Load config from TOML
    config = _load_toml_config_from_cwd()

    if config:
        if output_file is None and 'output' in config:
            output_file = config.get('output')

        if include is None and 'include' in config:
            include = _coerce_list_or_string_to_csv(config.get('include'))

        if exclude is None and 'exclude' in config:
            exclude = _coerce_list_or_string_to_csv(config.get('exclude'))

        if 'use_gitignore' in config:
            use_gitignore = bool(config.get('use_gitignore'))

        if max_file_size == 16384 and 'max_file_size' in config:
            try:
                max_file_size = int(config.get('max_file_size'))
            except Exception:
                print("Warning: 'max_file_size' in TOML config is not an integer; ignoring.", file=sys.stderr)

        if output_format == 'markdown':
            fmt_val = config.get('format', config.get('output_format'))
            if fmt_val:
                fmt_val = str(fmt_val)
                if fmt_val not in VALID_FORMATS:
                    print(f"Warning: unknown format '{fmt_val}' in TOML config; using default.", file=sys.stderr)
                else:
                    output_format = fmt_val

        if not show_tokens and 'tokens' in config:
            show_tokens = bool(config.get('tokens'))

        if not recent and 'recent' in config:
            recent = bool(config.get('recent'))

        if not line_numbers and 'line_numbers' in config:
            line_numbers = bool(config.get('line_numbers'))

        if preview is None and 'preview' in config:
            try:
                preview = int(config.get('preview'))
            except Exception:
                print("Warning: 'preview' in TOML config is not an integer; ignoring.", file=sys.stderr)

    if output_format not in VALID_FORMATS:
        raise ValueError(f"Invalid output format '{output_format}'. Must be one of: {', '.join(VALID_FORMATS)}")

    include_patterns = [p.strip() for p in include.split(',')] if include else None
    exclude_patterns = [p.strip() for p in exclude.split(',')] if exclude else None

    file_processor = FileProcessor(max_file_size)
    formatter = OutputFormatter()

    all_results = []

    for path_str in paths:
        path = Path(path_str).resolve()
        try:
            if path.is_file():
                repo_info = process_single_file(path, file_processor, line_numbers, preview)
            elif path.is_dir():
                repo_info = process_directory(
                    path, file_processor, formatter,
                    include_patterns, exclude_patterns,
                    recent, line_numbers, preview,
                    use_gitignore=use_gitignore
                )
            else:
                print(f"Error: {path} is neither a file nor a directory", file=sys.stderr)
                continue

            all_results.append(repo_info)

        except Exception as e:
            print(f"Error processing {path}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            continue

    if not all_results:
        print("No results to output", file=sys.stderr)
        return

    try:
        if len(all_results) == 1:
            final_output = formatter.format_output(all_results[0], output_format, show_tokens, recent)
        else:
            combined_info = combine_repositories(all_results)
            final_output = formatter.format_output(combined_info, output_format, show_tokens, recent)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_output)
            print(f"Output written to {output_file}", file=sys.stderr)
        else:
            sys.stdout.write(final_output)
            if not final_output.endswith('\n'):
                sys.stdout.write('\n')
            sys.stdout.flush()

    except Exception as e:
        print(f"Error formatting output: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def process_directory(path: Path,
                      file_processor: FileProcessor,
                      formatter: OutputFormatter,
                      include_patterns: Optional[List[str]] = None,
                      exclude_patterns: Optional[List[str]] = None,
                      recent: bool = False,
                      line_numbers: bool = False,
                      preview: Optional[int] = None,
                      use_gitignore: bool = False) -> Dict[str, Any]:
    """Process a directory respecting .gitignore."""

    git_info = GitInfo(path)

    try:
        files = file_processor.discover_files(path, include_patterns, exclude_patterns, use_gitignore=use_gitignore)
        if recent:
            files = file_processor.filter_recent_files(files)
    except Exception as e:
        print(f"Error discovering files: {e}", file=sys.stderr)
        files = []

    file_contents = []
    total_lines = 0

    for file_path in files:
        try:
            content, truncated = file_processor.read_file_content(file_path)
            relative_path = file_path.relative_to(path)

            if line_numbers and content:
                content = "\n".join(f"{idx+1}: {line}" for idx, line in enumerate(content.splitlines()))

            line_count = len(content.split('\n')) if content else 0
            truncated_type = None

            if preview:
                lines = content.splitlines()
                content = "\n".join(lines[:preview])
                if len(lines) > preview:
                    content += f"\n[... Preview truncated after {preview} lines ...]"
                truncated_type = "preview"
            elif truncated:
                truncated_type = "size"

            file_info = {
                'relative_path': str(relative_path),
                'absolute_path': str(file_path),
                'content': content,
                'truncated_type': truncated_type,
                'lines': line_count
            }

            file_contents.append(file_info)
            total_lines += line_count

        except Exception as e:
            print(f"Warning: Error processing {file_path}: {e}", file=sys.stderr)

    try:
        tree_structure = formatter.generate_tree_structure(files, path)
    except Exception as e:
        print(f"Error generating tree structure: {e}", file=sys.stderr)
        tree_structure = "Error generating tree structure"

    summary = {'total_files': len(file_contents), 'total_lines': total_lines}

    return {
        'absolute_path': str(path),
        'git_info': git_info.get_git_info(),
        'structure': tree_structure,
        'files': file_contents,
        'summary': summary
    }


def process_single_file(file_path: Path, file_processor: FileProcessor, line_numbers: bool = False, preview: Optional[int] = None) -> Dict[str, Any]:
    git_info = GitInfo(file_path.parent)
    try:
        content, truncated = file_processor.read_file_content(file_path)

        if line_numbers and content:
            content = "\n".join(f"{idx+1}: {line}" for idx, line in enumerate(content.splitlines()))

        line_count = len(content.split('\n')) if content else 0
        truncated_type = None

        if preview:
            lines = content.splitlines()
            content = "\n".join(lines[:preview])
            if len(lines) > preview:
                content += f"\n[... Preview truncated after {preview} lines ...]"
            truncated_type = "preview"
        elif truncated:
            truncated_type = "size"

        file_info = {
            'relative_path': file_path.name,
            'absolute_path': str(file_path),
            'content': content,
            'truncated_type': truncated_type,
            'lines': line_count
        }

        summary = {'total_files': 1, 'total_lines': line_count}

        return {
            'absolute_path': str(file_path.parent),
            'git_info': git_info.get_git_info(),
            'structure': file_path.name,
            'files': [file_info],
            'summary': summary
        }

    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return {
            'absolute_path': str(file_path.parent),
            'git_info': None,
            'structure': file_path.name,
            'files': [],
            'summary': {'total_files': 0, 'total_lines': 0}
        }

def combine_repositories(repo_infos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Combine multiple repository information dictionaries."""
    if len(repo_infos) == 1:
        return repo_infos[0]

    combined = {
        'absolute_path': "Multiple paths processed",
        'git_info': None,
        'structure': "",
        'files': [],
        'summary': {'total_files': 0, 'total_lines': 0}
    }

    for repo_info in repo_infos:
        combined['files'].extend(repo_info.get('files', []))
        summary = repo_info.get('summary', {})
        combined['summary']['total_files'] += summary.get('total_files', 0)
        combined['summary']['total_lines'] += summary.get('total_lines', 0)

    return combined

if __name__ == '__main__':
    process_repositories(['.'])
