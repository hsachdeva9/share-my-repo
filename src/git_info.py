import subprocess
from pathlib import Path
from typing import Dict

class GitInfo:
    """Handles git repository operations."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def get_git_info(self) -> Dict[str, str]:
        """Get git information for the repository."""
        if not self.is_git_repository():
            return {'error': 'Not a git repository'}

        try:
            # Get commit hash
            commit = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True, text=True, check=True
            ).stdout.strip()

            # Get branch name
            branch = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.repo_path,
                capture_output=True, text=True, check=True
            ).stdout.strip()

            # Get last commit author and date
            commit_info = subprocess.run(
                ['git', 'log', '-1', '--format=%an <%ae>%n%cd'],
                cwd=self.repo_path,
                capture_output=True, text=True, check=True
            ).stdout.strip().split('\n')

            author = commit_info[0] if len(commit_info) > 0 else 'Unknown'
            date = commit_info[1] if len(commit_info) > 1 else 'Unknown'

            return {
                'commit': commit,
                'branch': branch,
                'author': author,
                'date': date
            }

        except (subprocess.CalledProcessError, FileNotFoundError, IndexError) as e:
            return {'error': f'Git command failed: {str(e)}'}

    def is_git_repository(self) -> bool:
        """Check if the given path is a git repository."""
        try:
            subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.repo_path,
                capture_output=True, check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            return False
