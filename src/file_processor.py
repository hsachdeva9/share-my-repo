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
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".svg",
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".exe",
            ".dll",
            ".so",
            ".dylib",
            ".zip",
            ".tar",
            ".gz",
            ".rar",
            ".7z",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
            ".pyc",
            ".pyo",
            ".class",
            ".egg",
        }
        self.skip_directories = {
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            ".env",
            "env",
            "build",
            "dist",
            ".pytest_cache",
            ".egg-info",
        }

    # ---------------------------
    # Path normalization & patterns
    # ---------------------------
    def _normalize_path(self, path: Path) -> str:
        """Return consistent lowercase forward-slash string for a path."""
        if path is None:
            raise AttributeError("path cannot be None")
        return str(path).replace("\\", "/").lower()

    def load_gitignore_patterns(self, root_path: Path) -> dict:
        """
        Load all .gitignore files recursively from root.
        Returns a dict: {Path to .gitignore folder: set(patterns)}
        """
        gitignore_dict = {}
        for gitignore_file in root_path.rglob(".gitignore"):
            patterns = set()
            try:
                with open(gitignore_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            patterns.add(line)
            except Exception as e:
                print(
                    f"Warning: Could not read {gitignore_file}: {e}", file=sys.stderr)
            gitignore_dict[gitignore_file.parent] = patterns
        return gitignore_dict

    def matches_gitignore(
        self, file_path: Path, gitignore_dict: dict, root_path: Path
    ) -> bool:
        """
        Check if file matches any gitignore pattern in its directory hierarchy.
        """
        for parent, patterns in gitignore_dict.items():
            try:
                rel_to_gitignore = file_path.relative_to(parent)
            except ValueError:
                continue
            filename = file_path.name.lower()
            norm_path = self._normalize_path(rel_to_gitignore)
            for pattern in patterns:
                pattern = pattern.lower()
                if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(
                    norm_path, pattern
                ):
                    return True
                try:
                    if rel_to_gitignore.match(pattern):
                        return True
                except ValueError:
                    continue
        return False

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
        if dir_name in self.skip_directories or dir_name.endswith(".egg-info"):
            return True
        try:
            relative_path = dir_path.relative_to(root_path)
            if any(
                part.endswith(".egg-info") or part in self.skip_directories
                for part in relative_path.parts
            ):
                return True
        except ValueError:
            pass
        return False

    def is_text_file(self, file_path: Path) -> bool:
        """Determine if a file is likely a text file."""
        suffix = file_path.suffix.lower()
        if suffix in self.binary_extensions or suffix == ".egg":
            return False
        if ".egg-info" in str(file_path):
            return False
        try:
            if file_path.stat().st_size > self.max_file_size * 10:
                return False
        except OSError:
            return False
        try:
            with open(file_path, "rb") as f:
                if b"\x00" in f.read(1024):
                    return False
        except (OSError, UnicodeDecodeError):
            return False
        return True

    def should_include_file(
        self,
        file_path: Path,
        root_path: Path,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        gitignore_patterns: Optional[Set[str]] = None,
    ) -> bool:
        """Determine if file should be included based on patterns."""
        if gitignore_patterns and self.matches_gitignore(
            file_path, gitignore_patterns, root_path
        ):
            return False
        if exclude_patterns and self.matches_pattern(
            file_path, exclude_patterns, root_path
        ):
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
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read(self.max_file_size), True
            else:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read(), False
        except Exception as e:
            print(f"Warning: Error reading {file_path}: {e}", file=sys.stderr)
            return f"Error reading file: {e}", False

    # ---------------------------
    # File discovery
    # ---------------------------
    def discover_files(
        self,
        root_path: Path,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        use_gitignore: bool = True,
    ) -> List[Path]:
        """Find all files in directory tree that match our criteria."""
        files = []
        gitignore_patterns = (
            self.load_gitignore_patterns(root_path) if use_gitignore else None
        )

        try:
            for root, dirs, filenames in os.walk(root_path):
                root_path_obj = Path(root)
                dirs[:] = [
                    d
                    for d in dirs
                    if not self.should_skip_directory(root_path_obj / d, root_path)
                ]
                for filename in filenames:
                    file_path = root_path_obj / filename
                    if not self.is_text_file(file_path):
                        continue
                    if not self.should_include_file(
                        file_path,
                        root_path,
                        include_patterns,
                        exclude_patterns,
                        gitignore_patterns,
                    ):
                        continue
                    files.append(file_path)
        except PermissionError as e:
            print(
                f"Permission denied accessing {root_path}: {e}", file=sys.stderr)
        except Exception as e:
            print(
                f"Error discovering files in {root_path}: {e}", file=sys.stderr)

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
