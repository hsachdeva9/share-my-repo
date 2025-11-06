import pytest
from pathlib import Path
from src.file_processor import FileProcessor

class TestNormalizePath:

    def setup_method(self):
        self.processor = FileProcessor()

    def test_normalize_path_basic(self):
        path = Path("C:\\Users\\Example\\File.TXT")
        result = self.processor._normalize_path(path)
        assert result == "c:/users/example/file.txt"
    
    def test_normalize_path_unix(self):
        path = Path("/home/user/File.txt")
        result = self.processor._normalize_path(path)
        assert result == "/home/user/file.txt"

    def test_normalize_path_mixed_case(self):
        path = Path("C:/SomeFolder/MixedCase.TXT")
        result = self.processor._normalize_path(path)
        assert result == "c:/somefolder/mixedcase.txt"

    def test_normalize_path_with_spaces(self):
        path = Path("/home/user/My Documents/File.txt")
        result = self.processor._normalize_path(path)
        assert result == "/home/user/my documents/file.txt"
    
    def test_already_normalized_path(self):
        path = Path("c:/users/example/file.txt")
        result = self.processor._normalize_path(path)
        assert result == "c:/users/example/file.txt"

    def test_empty_path(self):
        path = Path("")
        result = self.processor._normalize_path(path)
        assert result == "."

    def test_none_path(self):
        with pytest.raises(AttributeError):
            self.processor._normalize_path(None)

    def test_special_characters_path(self):
        path = Path("/home/user/Doc$#@!/File.txt")
        result = self.processor._normalize_path(path)
        assert result == "/home/user/doc$#@!/file.txt"

    def test_path_with_trailing_slash(self):
        path = Path("/home/user/folder/")
        result = self.processor._normalize_path(path)
        assert result == "/home/user/folder"

class TestMatchesPattern:
    def setup_method(self):
        self.processor = FileProcessor()
        self.root = Path("/project")

    def test_matches_filename_pattern(self):
        file_path = Path("/project/src/main.py")
        patterns = ["*.py"]
        assert self.processor.matches_pattern(file_path, patterns, self.root)

    def test_matches_relative_path_pattern(self):
        file_path = Path("/project/src/main.py")
        patterns = ["src/*.py"]
        assert self.processor.matches_pattern(file_path, patterns, self.root)

    def test_matches_multiple_patterns(self):
        file_path = Path("/project/src/main.py")
        patterns = ["*.txt", "src/*.py"]
        assert self.processor.matches_pattern(file_path, patterns, self.root)

    def test_no_match(self):
        file_path = Path("/project/src/main.py")
        patterns = ["*.txt"]
        assert not self.processor.matches_pattern(file_path, patterns, self.root)

    def test_empty_patterns_list(self):
        file_path = Path("/project/src/main.py")
        patterns = []
        assert not self.processor.matches_pattern(file_path, patterns, self.root)

    def test_none_patterns(self):
        file_path = Path("/project/src/main.py")
        patterns = None
        assert not self.processor.matches_pattern(file_path, patterns, self.root)

    def test_pattern_with_spaces(self):
        file_path = Path("/project/src/my file.py")
        patterns = ["*.py"]
        assert self.processor.matches_pattern(file_path, patterns, self.root)

    def test_pattern_with_subdirectories(self):
        file_path = Path("/project/src/subdir/file.py")
        patterns = ["src/**/*.py"]  # ** should match subdirs
        assert self.processor.matches_pattern(file_path, patterns, self.root)

    def test_filename_case_insensitive(self):
        file_path = Path("/project/src/Main.PY")
        patterns = ["main.py"]
        assert self.processor.matches_pattern(file_path, patterns, self.root)

    def test_none_file_path(self):
        with pytest.raises(AttributeError):
            self.processor.matches_pattern(None, ["*.py"], self.root)