import pytest
from pathlib import Path
from src.formatter import OutputFormatter


class TestOutputFormatter:
    @pytest.fixture
    def formatter(self):
        return OutputFormatter()

    # --------------------------
    # generate_tree_structure tests
    # --------------------------
    def test_generate_tree_structure_simple(self, formatter, tmp_path):
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "dir1" / "file2.txt"
        file2.parent.mkdir()
        file1.write_text("hello")
        file2.write_text("world")
        files = [file1, file2]
        tree_str = formatter.generate_tree_structure(files, tmp_path)
        assert "file1.txt" in tree_str
        assert "dir1" in tree_str
        assert "file2.txt" in tree_str

    def test_generate_tree_structure_nested_dirs(self, formatter, tmp_path):
        (tmp_path / "a/b/c").mkdir(parents=True)
        file = tmp_path / "a/b/c/file.txt"
        file.write_text("content")
        tree_str = formatter.generate_tree_structure([file], tmp_path)
        assert "a" in tree_str
        assert "b" in tree_str
        assert "c" in tree_str
        assert "file.txt" in tree_str

    def test_generate_tree_structure_empty(self, formatter, tmp_path):
        tree_str = formatter.generate_tree_structure([], tmp_path)
        assert tree_str == ""

    def test_generate_tree_structure_multiple_files_same_dir(self, formatter, tmp_path):
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("a")
        file2.write_text("b")
        tree_str = formatter.generate_tree_structure([file1, file2], tmp_path)
        assert "file1.txt" in tree_str
        assert "file2.txt" in tree_str

    def test_generate_tree_structure_file_outside_root(self, formatter, tmp_path):
        outside_file = Path("/tmp/outside.txt")
        outside_file.write_text("outside")
        tree_str = formatter.generate_tree_structure([outside_file], tmp_path)
        assert tree_str == ""  # file outside root should not appear

    # --------------------------
    # format_markdown tests
    # --------------------------
    def test_format_markdown_basic_file(self, formatter, tmp_path):
        file = tmp_path / "file.txt"
        file.write_text("hello world")
        repo_info = {
            "absolute_path": tmp_path,
            "files": [
                {
                    "absolute_path": str(file),
                    "relative_path": "file.txt",
                    "content": "hello world",
                }
            ],
            "structure": "├── file.txt",
            "git_info": {},
        }
        md = formatter.format_markdown(repo_info)
        assert "## File Contents" in md
        assert "file.txt" in md
        assert "hello world" in md

    def test_format_markdown_recent_file(self, formatter, tmp_path):
        file = tmp_path / "file.txt"
        file.write_text("recent content")
        repo_info = {
            "absolute_path": tmp_path,
            "files": [
                {
                    "absolute_path": str(file),
                    "relative_path": "file.txt",
                    "content": "recent content",
                }
            ],
            "structure": "├── file.txt",
            "git_info": {},
        }
        md = formatter.format_markdown(repo_info, recent=True)
        assert "## Recent Changes" in md
        assert "(modified" in md

    def test_format_markdown_truncated_file(self, formatter, tmp_path):
        file = tmp_path / "file.txt"
        file.write_text("x" * 500)
        repo_info = {
            "absolute_path": tmp_path,
            "files": [
                {
                    "absolute_path": str(file),
                    "relative_path": "file.txt",
                    "content": "x" * 500,
                    "truncated_type": "size",
                }
            ],
            "structure": "├── file.txt",
            "git_info": {},
        }
        md = formatter.format_markdown(repo_info)
        assert "[... File truncated due to size limit ...]" in md

    def test_format_markdown_no_files(self, formatter, tmp_path):
        repo_info = {
            "absolute_path": tmp_path,
            "files": [],
            "structure": "",
            "git_info": {},
        }
        md = formatter.format_markdown(repo_info)
        assert "## File Contents" not in md
        assert "## Structure" in md

    def test_format_markdown_with_git_info(self, formatter, tmp_path):
        file = tmp_path / "file.txt"
        file.write_text("content")
        repo_info = {
            "absolute_path": tmp_path,
            "files": [
                {
                    "absolute_path": str(file),
                    "relative_path": "file.txt",
                    "content": "content",
                }
            ],
            "structure": "├── file.txt",
            "git_info": {
                "commit": "abc123",
                "branch": "main",
                "author": "Me",
                "date": "2025-11-13",
            },
        }
        md = formatter.format_markdown(repo_info)
        assert "- Commit: abc123" in md
        assert "- Branch: main" in md
        assert "- Author: Me" in md
