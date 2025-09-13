import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from file_processor import FileProcessor
from git_info import GitInfo
from formatter import OutputFormatter

def process_repositories(paths: List[str], 
                        output_file: Optional[str] = None,
                        include: Optional[str] = None,
                        exclude: Optional[str] = None,
                        max_file_size: int = 16384,
                        output_format: str = 'markdown',
                        show_tokens: bool = False):
    """Main processing function with enhanced features."""
    
    # Parse include/exclude patterns from comma-separated strings
    include_patterns = [p.strip() for p in include.split(',')] if include else None
    exclude_patterns = [p.strip() for p in exclude.split(',')] if exclude else None
    
    # Initialize processors
    file_processor = FileProcessor(max_file_size)
    formatter = OutputFormatter()
    
    # Process each path
    all_results = []
    
    for path_str in paths:
        path = Path(path_str).resolve()
        
        if path.is_file():
            repo_info = process_single_file(path, file_processor)
        elif path.is_dir():
            repo_info = process_directory(path, file_processor, formatter, 
                                        include_patterns, exclude_patterns)
        else:
            print(f"Error: {path} is neither a file nor a directory", file=sys.stderr)
            continue
        
        all_results.append(repo_info)
    
    # Handle output
    if len(all_results) == 1:
        final_output = formatter.format_output(all_results[0], output_format, show_tokens)
    else:
        combined_info = combine_repositories(all_results)
        final_output = formatter.format_output(combined_info, output_format, show_tokens)
    
    # Output results
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_output)
            print(f"Output written to {output_file}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing to {output_file}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(final_output)

def process_directory(path: Path, 
                     file_processor: FileProcessor, 
                     formatter: OutputFormatter,
                     include_patterns: Optional[List[str]] = None,
                     exclude_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
    """Process a directory with enhanced filtering."""
    
    print(f"Processing directory: {path}", file=sys.stderr)
    
    # Get git information
    git_info = GitInfo(path)
    
    # Discover files with enhanced filtering
    print("Discovering files...", file=sys.stderr)
    files = file_processor.discover_files(path, include_patterns, exclude_patterns)
    print(f"Found {len(files)} files to process", file=sys.stderr)
    
    # Process each file
    file_contents = []
    total_lines = 0
    
    for file_path in files:
        try:
            content, truncated = file_processor.read_file_content(file_path)
            relative_path = file_path.relative_to(path)
            
            line_count = len(content.split('\n')) if content else 0
            
            file_info = {
                'relative_path': str(relative_path),
                'absolute_path': str(file_path),
                'content': content,
                'truncated': truncated,
                'lines': line_count
            }
            
            file_contents.append(file_info)
            total_lines += line_count
            
        except Exception as e:
            print(f"Warning: Error processing {file_path}: {e}", file=sys.stderr)
    
    # Generate tree structure
    tree_structure = formatter.generate_tree_structure(files, path)
    
    # Summary statistics
    summary = {
        'total_files': len(file_contents),
        'total_lines': total_lines
    }
    
    return {
        'absolute_path': str(path),
        'git_info': git_info.get_git_info(),
        'structure': tree_structure,
        'files': file_contents,
        'summary': summary
    }

def process_single_file(file_path: Path, file_processor: FileProcessor) -> Dict[str, Any]:
    """Process a single file."""
    
    print(f"Processing file: {file_path}", file=sys.stderr)
    
    git_info = GitInfo(file_path.parent)
    
    try:
        content, truncated = file_processor.read_file_content(file_path)
        line_count = len(content.split('\n')) if content else 0
        
        file_info = {
            'relative_path': file_path.name,
            'absolute_path': str(file_path),
            'content': content,
            'truncated': truncated,
            'lines': line_count
        }
        
        summary = {
            'total_files': 1,
            'total_lines': line_count
        }
        
        return {
            'absolute_path': str(file_path.parent),
            'git_info': git_info.get_git_info(),
            'structure': file_path.name,
            'files': [file_info],
            'summary': summary
        }
        
    except Exception as e:
        print(f"Error: Error processing {file_path}: {e}", file=sys.stderr)
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