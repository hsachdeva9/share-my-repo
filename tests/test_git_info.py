from pathlib import Path
from src.git_info import GitInfo


class TestGetGitInfo:

    def setup_method(self):
        self.git_info = GitInfo(Path("."))

    def test_get_git_info_returns_dict(self):
        result = self.git_info.get_git_info()
        assert isinstance(result, dict)

    def test_get_git_info_has_required_keys(self):
        result = self.git_info.get_git_info()
        if "error" not in result:
            assert "commit" in result
            assert "branch" in result
            assert "author" in result
            assert "date" in result

    def test_get_git_info_empty_path(self):
        git_info = GitInfo(Path(""))
        # Empty path resolves to current directory, should pass without error
        result = git_info.get_git_info()
        assert isinstance(result, dict)

    def test_get_git_info_nonexistent_path(self):
        git_info = GitInfo(Path("/nonexistent/path/that/does/not/exist"))
        result = git_info.get_git_info()
        assert isinstance(result, dict)
        assert "error" in result
