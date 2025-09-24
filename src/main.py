import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from file_processor import FileProcessor
from git_info import GitInfo
from formatter import OutputFormatter

VALID_FORMATS = ['markdown', 'json', 'yaml']

def process_repositories(paths: List[str], 
                        output_file: Optional[str] = None,
                        include: Optional[str] = None,
                        exclude: Optional[str] = None,
                        max_file_size: int = 16384,
                        output_format: str = 'markdown',
                        show_tokens: bool = False,
                        recent: bool = False,
                        line_numbers: bool = False):  
    """Main processing function with enhanced features."""
    
    if output_format not in VALID_FORMATS:
        raise ValueError(
            f"Invalid output format '{output_format}'. Must be one of: {', '.join(VALID_FORMATS)}"
        )

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
        
        try:
            if path.is_file():
                repo_info = process_single_file(path, file_processor, line_numbers=line_numbers) 
            elif path.is_dir():
                repo_info = process_directory(path, file_processor, formatter, 
                                            include_patterns, exclude_patterns, recent,
                                            line_numbers=line_numbers)  
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
    
    # Handle output
    try:
        if len(all_results) == 1:
            final_output = formatter.format_output(all_results[0], output_format, show_tokens, recent)
        else:
            combined_info = combine_repositories(all_results)
            final_output = formatter.format_output(combined_info, output_format, show_tokens, recent)
        
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
            # Handle large console output properly
            try:
                if len(final_output) > 50000: 
                    chunk_size = 8192  
                    for i in range(0, len(final_output), chunk_size):
                        chunk = final_output[i:i + chunk_size]
                        sys.stdout.write(chunk)
                        sys.stdout.flush()
                else:
                    sys.stdout.write(final_output)
                    sys.stdout.flush()
                
                if not final_output.endswith('\n'):
                    sys.stdout.write('\n')
                    sys.stdout.flush()
                    
            except BrokenPipeError:
                pass
            except Exception as e:
                print(f"Error writing to console: {e}", file=sys.stderr)
                print(final_output)
                
    except Exception as e:
        print(f"Error formatting output: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

# -------------------- UPDATED process_directory --------------------
def process_directory(path: Path, 
                     file_processor: FileProcessor, 
                     formatter: OutputFormatter,
                     include_patterns: Optional[List[str]] = None,
                     exclude_patterns: Optional[List[str]] = None,
                     recent: bool = False,
                     line_numbers: bool = False):  # <-- added line_numbers parameter
    """Process a directory with enhanced filtering."""
    
    git_info = GitInfo(path)
    
    try:
        files = file_processor.discover_files(path, include_patterns, exclude_patterns)
        if recent:
            files = file_processor.filter_recent_files(files)
    except Exception as e:
        print(f"Error discovering files: {e}", file=sys.stderr)
        files = []
    
    file_contents = []
    total_lines = 0
    
    for i, file_path in enumerate(files, 1):
        try:
            content, truncated = file_processor.read_file_content(file_path)
            relative_path = file_path.relative_to(path)
            
            # <-- add line numbers if requested
            if line_numbers and content:
                content = "\n".join(f"{idx+1}: {line}" for idx, line in enumerate(content.splitlines()))
            
            line_count = len(content.split('\n')) if content else 0
            
            file_info = {
                'relative_path': str(relative_path),
                'absolute_path': str(file_path),
                'content': content,  # <-- may include line numbers now
                'truncated': truncated,
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


def process_single_file(file_path: Path, file_processor: FileProcessor, line_numbers: bool = False): 
    """Process a single file."""
    
    git_info = GitInfo(file_path.parent)
    
    try:
        content, truncated = file_processor.read_file_content(file_path)
        
        if line_numbers and content:
            content = "\n".join(f"{idx+1}: {line}" for idx, line in enumerate(content.splitlines()))
        
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
        print(f"Error processing {file_path}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
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
