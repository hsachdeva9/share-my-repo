import os
import fnmatch
from pathlib import Path
from typing import List, Optional, Tuple, Set
import sys

class FileProcessor:
    """Handles file discovery, filtering, and content reading."""
    
    def __init__(self, max_file_size: int = 16 * 1024):
        self.max_file_size = max_file_size
        # Common binary file extensions to skip
        self.binary_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',  # Images
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',         # Documents
            '.exe', '.dll', '.so', '.dylib',                  # Executables
            '.zip', '.tar', '.gz', '.rar', '.7z',            # Archives
            '.mp3', '.mp4', '.avi', '.mov',                   # Media
            '.pyc', '.pyo', '.class', '.egg'                  # Compiled code (fixed: removed 'egg')
        }
        
        # Directories to always skip - UPDATED to include .egg-info patterns
        self.skip_directories = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv',
            '.env', 'env', 'build', 'dist', '.pytest_cache', '.egg-info'  
        }
    
    def load_gitignore_patterns(self, root_path: Path) -> Set[str]:
        """Load patterns from .gitignore file if it exists."""
        gitignore_path = root_path / '.gitignore'
        patterns = set()
        
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith('#'):
                            patterns.add(line)
            except Exception as e:
                print(f"Warning: Could not read .gitignore: {e}", file=sys.stderr)
        
        return patterns
    
    def matches_pattern(self, path: Path, patterns: List[str], root_path: Path) -> bool:
        """Check if path matches any of the given patterns."""
        if not patterns:
            return False
        
        try:
            relative_path = path.relative_to(root_path)
            path_str = str(relative_path)
            filename = path.name
            
            for pattern in patterns:
                # Check filename match
                if fnmatch.fnmatch(filename, pattern):
                    return True
                # Check full path match
                if fnmatch.fnmatch(path_str, pattern):
                    return True
                # Check directory match
                if pattern.endswith('/') and pattern[:-1] in relative_path.parts:
                    return True
        except ValueError:
            # Path is not relative to root_path
            pass
        
        return False
    
    def should_skip_directory(self, dir_path: Path, root_path: Path) -> bool:
        """Check if a directory should be skipped entirely."""
        dir_name = dir_path.name
        
        # Skip directories in our skip list
        if dir_name in self.skip_directories:
            return True
            
        # Skip directories ending with .egg-info (like share_my_repo.egg-info)
        if dir_name.endswith('.egg-info'):
            return True
            
        # Skip any directory containing .egg-info in the path
        try:
            relative_path = dir_path.relative_to(root_path)
            for part in relative_path.parts:
                if part.endswith('.egg-info') or part in self.skip_directories:
                    return True
        except ValueError:
            pass
            
        return False
    
    def is_text_file(self, file_path: Path) -> bool:
        """Determine if a file is likely a text file we can read."""
        # Skip files with binary extensions
        if file_path.suffix.lower() in self.binary_extensions:
            return False
        
        # Skip .egg files specifically
        if file_path.suffix.lower() == '.egg' or file_path.name.endswith('.egg'):
            return False
            
        # Skip files inside .egg-info directories
        if '.egg-info' in str(file_path):
            return False
        
        # Skip very large files
        try:
            if file_path.stat().st_size > self.max_file_size * 10:
                return False
        except OSError:
            return False
        
        # Try to read a small chunk and look for binary indicators
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)  # Read first 1KB
                # If we find null bytes, it's probably binary
                if b'\x00' in chunk:
                    return False
        except (OSError, UnicodeDecodeError):
            return False
        
        return True
    
    def should_include_file(self, file_path: Path, root_path: Path,
                          include_patterns: Optional[List[str]] = None,
                          exclude_patterns: Optional[List[str]] = None,
                          gitignore_patterns: Optional[Set[str]] = None) -> bool:
        """Determine if file should be included based on patterns."""
        
        # Check gitignore patterns first
        if gitignore_patterns and self.matches_pattern(file_path, list(gitignore_patterns), root_path):
            return False
        
        # Check exclude patterns
        if exclude_patterns and self.matches_pattern(file_path, exclude_patterns, root_path):
            return False
        
        # Check include patterns
        if include_patterns:
            return self.matches_pattern(file_path, include_patterns, root_path)
        
        return True
    
    def read_file_content(self, file_path: Path) -> Tuple[str, bool]:
        """Read file content, handling large files and encoding issues."""
        try:
            file_size = file_path.stat().st_size
            
            # If file is larger than our limit, truncate it
            if file_size > self.max_file_size:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(self.max_file_size)
                return content, True
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return content, False
                
        except Exception as e:
            error_msg = f"Error reading file: {str(e)}"
            print(f"Warning: {error_msg} for {file_path}", file=sys.stderr)
            return error_msg, False
    
    def discover_files(self, root_path: Path, 
                   include_patterns: Optional[List[str]] = None,
                   exclude_patterns: Optional[List[str]] = None,
                   use_gitignore: bool = True) -> List[Path]:
        """Find all files in directory tree that match our criteria."""
        files = []

        # Load gitignore patterns if requested
        gitignore_patterns = self.load_gitignore_patterns(root_path) if use_gitignore else None

        try:
            for root, dirs, filenames in os.walk(root_path):
                root_path_obj = Path(root)

                
                dirs[:] = [d for d in dirs if not self.should_skip_directory(root_path_obj / d, root_path)]

                dirs[:] = [d for d in dirs if not self.should_skip_directory(root_path_obj / d, root_path)]

                
                if root_path_obj != root_path and self.should_skip_directory(root_path_obj, root_path):
                    continue
                for filename in filenames:
                    file_path = root_path_obj / filename

                    # Check if it's a text file we can process
                    if not self.is_text_file(file_path):
                        continue

                    # Check include/exclude patterns
                    if not self.should_include_file(file_path, root_path, 
                                                    include_patterns, exclude_patterns, 
                                                    gitignore_patterns):
                        continue

                    files.append(file_path)

        except PermissionError as e:
            print(f"Permission denied accessing {root_path}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error discovering files in {root_path}: {e}", file=sys.stderr)

        return sorted(files)