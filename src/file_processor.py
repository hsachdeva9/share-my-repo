import os
import fnmatch
from pathlib import Path
from typing import List, Optional, Tuple
import sys

class FileProcessor:
    def __init__(self, max_file_size: int = 16*1024):  # 16KB default
        self.max_file_size = max_file_size
        # Common binary file extensions to skip
        self.binary_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',  # Images
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',         # Documents
            '.exe', '.dll', '.so', '.dylib',                  # Executables
            '.zip', '.tar', '.gz', '.rar', '.7z',            # Archives
            '.mp3', '.mp4', '.avi', '.mov',                   # Media
            '.pyc', '.pyo', '.class'                          # Compiled code
        }
        
        # Directories to always skip
        self.skip_directories = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv',
            '.env', 'env', 'build', 'dist', '.pytest_cache'
        }
    
    def is_text_file(self, file_path: Path) -> bool:
        """
        Determine if a file is likely a text file we can read.
        """
        # Skip files with binary extensions
        if file_path.suffix.lower() in self.binary_extensions:
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
    
    def should_include_file(self, file_path: Path, 
                          include_patterns: Optional[List[str]] = None) -> bool:
        """
        Determine if file should be included based on include patterns.
        """
        filename = file_path.name
        
        # If include patterns are specified, file must match at least one
        if include_patterns:
            for pattern in include_patterns:
                if fnmatch.fnmatch(filename, pattern):
                    return True
            return False  # No include pattern matched
        
        return True  # No patterns specified, include everything
    
    def read_file_content(self, file_path: Path) -> Tuple[str, bool]:
        """
        Read file content, handling large files and encoding issues.
        
        Returns:
            Tuple of (content, was_truncated)
        """
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
                      include_patterns: Optional[List[str]] = None) -> List[Path]:
        """
        Find all files in directory tree that match our criteria.
        """
        files = []
        
        try:
            for root, dirs, filenames in os.walk(root_path):
                # Skip directories we don't want to traverse
                dirs[:] = [d for d in dirs if d not in self.skip_directories]
                
                root_path_obj = Path(root)
                
                for filename in filenames:
                    file_path = root_path_obj / filename
                    
                    # Check if it's a text file we can process
                    if not self.is_text_file(file_path):
                        continue
                    
                    # Check include patterns
                    if not self.should_include_file(file_path, include_patterns):
                        continue
                    
                    files.append(file_path)
                    
        except PermissionError as e:
            print(f"Permission denied accessing {root_path}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error discovering files in {root_path}: {e}", file=sys.stderr)
        
        return sorted(files)