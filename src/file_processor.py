import os
import time
import fnmatch
from pathlib import Path
from typing import List, Optional, Tuple, Set
import sys

class FileProcessor:
    """Handles file discovery, filtering, and content reading."""
    
    def __init__(self, max_file_size: int = 16 * 1024):
        self.max_file_size = max_file_size
        self.binary_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',
            '.exe', '.dll', '.so', '.dylib',
            '.zip', '.tar', '.gz', '.rar', '.7z',
            '.mp3', '.mp4', '.avi', '.mov',
            '.pyc', '.pyo', '.class', '.egg'
        }
        self.skip_directories = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv',
            '.env', 'env', 'build', 'dist', '.pytest_cache', '.egg-info'  
        }

    # ---------------------------
    # Path normalization & patterns
    # ---------------------------
    def _normalize_path(self, path: Path) -> str:
        """Return consistent lowercase forward-slash string for a path."""
        return path.as_posix().lower()

    def load_gitignore_patterns(self, root_path: Path) -> Set[str]:
        """Load patterns from .gitignore file if it exists."""
        gitignore_path = root_path / '.gitignore'
        patterns = set()
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.add(line)
            except Exception as e:
                print(f"Warning: Could not read .gitignore: {e}", file=sys.stderr)
        return patterns

    def matches_pattern(self, path: Path, patterns: List[str], root_path: Path) -> bool:
        """Check if a path matches any of the given patterns."""
        if not patterns:
            return False
        relative_path = path.relative_to(root_path)
        norm_path = self._normalize_path(relative_path)
        filename = path.name.lower()

        for pattern in patterns:
            pattern = pattern.strip().lower()
            if not pattern:
                continue
            # Match filename directly
            if fnmatch.fnmatch(filename, pattern):
                return True
            # Match relative path
            if fnmatch.fnmatch(norm_path, pattern):
                return True
            # Match using Path.match (supports **)
            try:
                if relative_path.match(pattern):
                    return True
            except ValueError:
                continue
        return False

    # ---------------------------
    # Directory/file checks
    # ---------------------------
    def should_skip_directory(self, dir_path: Path, root_path: Path) -> bool:
        """Check if a directory should be skipped entirely."""
        dir_name = dir_path.name
        if dir_name in self.skip_directories or dir_name.endswith('.egg-info'):
            return True
        try:
            relative_path = dir_path.relative_to(root_path)
            if any(part.endswith('.egg-info') or part in self.skip_directories for part in relative_path.parts):
                return True
        except ValueError:
            pass
        return False

    def is_text_file(self, file_path: Path) -> bool:
        """Determine if a file is likely a text file."""
        suffix = file_path.suffix.lower()
        if suffix in self.binary_extensions or suffix == '.egg':
            return False
        if '.egg-info' in str(file_path):
            return False
        try:
            if file_path.stat().st_size > self.max_file_size * 10:
                return False
        except OSError:
            return False
        try:
            with open(file_path, 'rb') as f:
                if b'\x00' in f.read(1024):
                    return False
        except (OSError, UnicodeDecodeError):
            return False
        return True

    def should_include_file(self, file_path: Path, root_path: Path,
                            include_patterns: Optional[List[str]] = None,
                            exclude_patterns: Optional[List[str]] = None,
                            gitignore_patterns: Optional[Set[str]] = None) -> bool:
        """Determine if file should be included based on patterns."""
        if gitignore_patterns and self.matches_pattern(file_path, list(gitignore_patterns), root_path):
            return False
        if exclude_patterns and self.matches_pattern(file_path, exclude_patterns, root_path):
            return False
        if include_patterns:
            return self.matches_pattern(file_path, include_patterns, root_path)
        return True

    # ---------------------------
    # File reading
    # ---------------------------
    def read_file_content(self, file_path: Path) -> Tuple[str, bool]:
        """Read file content, handling large files and encoding issues."""
        try:
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read(self.max_file_size), True
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read(), False
        except Exception as e:
            print(f"Warning: Error reading {file_path}: {e}", file=sys.stderr)
            return f"Error reading file: {e}", False

    # ---------------------------
    # File discovery
    # ---------------------------
    def discover_files(self, root_path: Path, 
                       include_patterns: Optional[List[str]] = None,
                       exclude_patterns: Optional[List[str]] = None,
                       use_gitignore: bool = True) -> List[Path]:
        """Find all files in directory tree that match our criteria."""
        files = []
        gitignore_patterns = self.load_gitignore_patterns(root_path) if use_gitignore else None

        try:
            for root, dirs, filenames in os.walk(root_path):
                root_path_obj = Path(root)
                dirs[:] = [d for d in dirs if not self.should_skip_directory(root_path_obj / d, root_path)]
                for filename in filenames:
                    file_path = root_path_obj / filename
                    if not self.is_text_file(file_path):
                        continue
                    if not self.should_include_file(file_path, root_path, include_patterns, exclude_patterns, gitignore_patterns):
                        continue
                    files.append(file_path)
        except PermissionError as e:
            print(f"Permission denied accessing {root_path}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error discovering files in {root_path}: {e}", file=sys.stderr)

        return sorted(files)

    # ---------------------------
    # Recent file filtering
    # ---------------------------
    def is_recent_file(self, file_path: Path, days: int = 7) -> bool:
        try:
            return (time.time() - file_path.stat().st_mtime) <= (days * 86400)
        except (OSError, FileNotFoundError):
            return False

    def filter_recent_files(self, files: List[Path], days: int = 7) -> List[Path]:
        return [f for f in files if self.is_recent_file(f, days)]
