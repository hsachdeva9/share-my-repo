import os
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
            original_cwd = os.getcwd()
            os.chdir(self.repo_path)
            
            # Get commit hash
            commit = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], 
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            # Get branch name
            branch = subprocess.check_output(
                ['git', 'branch', '--show-current'], 
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            # Get last commit author and date
            commit_info = subprocess.check_output(
                ['git', 'log', '-1', '--format=%an <%ae>%n%cd'], 
                stderr=subprocess.DEVNULL
            ).decode().strip().split('\n')
            
            author = commit_info[0] if len(commit_info) > 0 else 'Unknown'
            date = commit_info[1] if len(commit_info) > 1 else 'Unknown'
            
            os.chdir(original_cwd)
            
            return {
                'commit': commit,
                'branch': branch,
                'author': author,
                'date': date
            }
            
        except (subprocess.CalledProcessError, FileNotFoundError, IndexError) as e:
            if 'original_cwd' in locals():
                os.chdir(original_cwd)
            return {'error': f'Git command failed: {str(e)}'}
    
    def is_git_repository(self) -> bool:
        """Check if the given path is a git repository."""
        try:
            original_cwd = os.getcwd()
            os.chdir(self.repo_path)
            subprocess.check_output(
                ['git', 'rev-parse', '--git-dir'], 
                stderr=subprocess.DEVNULL
            )
            os.chdir(original_cwd)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            if 'original_cwd' in locals():
                os.chdir(original_cwd)
            return False