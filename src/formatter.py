import json
import yaml
import os
import time
from pathlib import Path
from typing import List, Dict, Any

class OutputFormatter:
    def __init__(self):
        # Approximate token estimation: ~4 characters per token
        self.chars_per_token = 4
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for given text."""
        return len(text) // self.chars_per_token
    
    def generate_tree_structure(self, files: List[Path], root_path: Path) -> str:
        """Generate a tree structure representation of the files."""
        tree_dict = {}
        
        for file_path in files:
            try:
                relative_path = file_path.relative_to(root_path)
                parts = relative_path.parts
                
                current_dict = tree_dict
                for part in parts[:-1]:  # directories
                    if part not in current_dict:
                        current_dict[part] = {}
                    current_dict = current_dict[part]
                
                current_dict[parts[-1]] = None
                
            except ValueError:
                continue
        
        return self._dict_to_tree_string(tree_dict)
    
    def _dict_to_tree_string(self, tree_dict: Dict[str, Any], prefix: str = "") -> str:
        """Convert nested dictionary to tree string."""
        if not tree_dict:
            return ""
        
        result = []
        items = list(tree_dict.items())
        
        for i, (name, subtree) in enumerate(items):
            is_last_item = i == len(items) - 1
            line_prefix = "└── " if is_last_item else "├── "
            
            result.append(f"{prefix}{line_prefix}{name}")
            
            if subtree is not None:  # It's a directory
                extension = "    " if is_last_item else "│   "
                subtree_str = self._dict_to_tree_string(subtree, prefix + extension)
                if subtree_str:
                    result.append(subtree_str)
        
        return "\n".join(result)
    
    def format_output(self, repo_info: Dict[str, Any], format_type: str = 'markdown', 
                     show_tokens: bool = False, recent: bool = False) -> str:
        """Format output in specified format."""
        if format_type == 'json':
            return self.format_json(repo_info, show_tokens)
        elif format_type == 'yaml':
            return self.format_yaml(repo_info, show_tokens)
        else:  # markdown
            return self.format_markdown(repo_info, show_tokens, recent)
    
    def format_json(self, repo_info: Dict[str, Any], show_tokens: bool = False) -> str:
        """Format as JSON."""
        output_data = repo_info.copy()
        
        if show_tokens:
            # Calculate token estimates
            total_content = ""
            for file_info in repo_info.get('files', []):
                total_content += file_info.get('content', '')
            
            output_data['token_estimate'] = self.estimate_tokens(total_content)
        
        return json.dumps(output_data, indent=2)
    
    def format_yaml(self, repo_info: Dict[str, Any], show_tokens: bool = False) -> str:
        """Format as YAML."""
        output_data = repo_info.copy()
        
        if show_tokens:
            # Calculate token estimates
            total_content = ""
            for file_info in repo_info.get('files', []):
                total_content += file_info.get('content', '')
            
            output_data['token_estimate'] = self.estimate_tokens(total_content)
        
        return yaml.dump(output_data, default_flow_style=False, allow_unicode=True)
    
    def format_markdown(self, repo_info: Dict[str, Any], show_tokens: bool = False, recent: bool = False) -> str:
        """Format as Markdown."""
        output = []
        
        output.append("# Repository Context")
        output.append("")
        
        # File system location
        output.append("## File System Location")
        output.append("")
        output.append(str(repo_info['absolute_path']))
        output.append("")
        
        # Git information
        output.append("## Git Info")
        output.append("")
        if repo_info.get('git_info') and 'error' not in repo_info['git_info']:
            git_info = repo_info['git_info']
            output.append(f"- Commit: {git_info.get('commit', 'N/A')}")
            output.append(f"- Branch: {git_info.get('branch', 'N/A')}")
            output.append(f"- Author: {git_info.get('author', 'N/A')}")
            output.append(f"- Date: {git_info.get('date', 'N/A')}")
        else:
            output.append("- Not a git repository")
        output.append("")
        
        # Directory structure
        output.append("## Structure")
        output.append("```")
        output.append(repo_info.get('structure', 'No files found'))
        output.append("```")
        output.append("")
        
        # File contents
        if repo_info.get('files'):
            if recent:
                output.append("## Recent Changes (Last 7 Days)")
            else:
                output.append("## File Contents")
            output.append("")
            
            for file_info in repo_info['files']:
                relative_path = file_info['relative_path']
                
                # Add modification date for recent files
                if recent:
                    try:
                        file_path = Path(file_info['absolute_path'])
                        last_modified = file_path.stat().st_mtime
                        days_ago = int((time.time() - last_modified) / 86400)
                        output.append(f"### File: {relative_path} (modified {days_ago} days ago)")
                    except (OSError, FileNotFoundError):
                        output.append(f"### File: {relative_path}")
                else:
                    output.append(f"### File: {relative_path}")
                
                # Determine syntax highlighting language
                file_ext = Path(relative_path).suffix.lower()
                lang_map = {
                    '.py': 'python',
                    '.js': 'javascript', '.jsx': 'jsx',
                    '.ts': 'typescript', '.tsx': 'tsx',
                    '.java': 'java',
                    '.cpp': 'cpp', '.c': 'c', '.h': 'c',
                    '.css': 'css', '.html': 'html',
                    '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml',
                    '.md': 'markdown', '.sh': 'bash', '.sql': 'sql',
                }
                lang = lang_map.get(file_ext, '')
                
                output.append(f"```{lang}")
                output.append(file_info['content'])
                if file_info.get('truncated', False):
                    output.append("")
                    output.append("[... File truncated due to size limit ...]")
                output.append("```")
                output.append("")
        
        # Summary statistics
        output.append("## Summary")
        summary = repo_info.get('summary', {})
        output.append(f"- Total files: {summary.get('total_files', 0)}")
        output.append(f"- Total lines: {summary.get('total_lines', 0)}")
        
        # Token estimation if requested
        if show_tokens:
            total_content = "\n".join(output)
            estimated_tokens = self.estimate_tokens(total_content)
            output.append(f"- Estimated tokens: {estimated_tokens}")
        
        return "\n".join(output)