import json
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from types import SimpleNamespace

# Add the parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class FakeRepository:
    def __init__(self):
        self.branches = {}
        self.files = {}
        self.pulls = []
    
    def get_branch(self, branch_name):
        if branch_name in self.branches:
            return SimpleNamespace(commit=SimpleNamespace(sha="abc123"))
        raise Exception("Branch not found")
    
    def create_git_ref(self, ref, sha):
        branch_name = ref.replace("refs/heads/", "")
        self.branches[branch_name] = {"sha": sha}
    
    def create_file(self, path, message, content, branch):
        self.files[path] = {
            "content": content,
            "message": message,
            "branch": branch
        }
    
    def create_pull(self, title, body, head, base):
        pr = SimpleNamespace(
            html_url=f"https://github.com/test/repo/pull/{len(self.pulls) + 1}",
            title=title,
            body=body,
            head=head,
            base=base
        )
        self.pulls.append(pr)
        return pr


class FakeGithub:
    def __init__(self):
        self.repositories = {}
    
    def get_repo(self, repo_name):
        if repo_name not in self.repositories:
            self.repositories[repo_name] = FakeRepository()
        return self.repositories[repo_name]


def test_slugify():
    """Test URL slug generation"""
    from executor.pr_executor import slugify
    
    assert slugify("Hello World!") == "hello-world"
    assert slugify("Test@#$%^&*()") == "test"
    assert slugify("Multiple   Spaces") == "multiple-spaces"
    assert slugify("") == ""


def test_load_decision_pack():
    """Test loading decision pack from file"""
    from executor.pr_executor import load_decision_pack
    
    test_pack = {
        "title": "Test Pack",
        "hypothesis": "Test hypothesis",
        "expected_lift": {"level": "medium", "metric": "conversion"}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_pack, f)
        temp_file = f.name
    
    try:
        loaded_pack = load_decision_pack(temp_file)
        assert loaded_pack["title"] == "Test Pack"
        assert loaded_pack["hypothesis"] == "Test hypothesis"
    finally:
        os.unlink(temp_file)


def test_generate_pr_content():
    """Test PR content generation"""
    from executor.pr_executor import generate_pr_content
    
    test_pack = {
        "title": "Test Growth Experiment",
        "hypothesis": "This is a test hypothesis for the growth experiment",
        "expected_lift": {"level": "high", "metric": "conversion rate"}
    }
    
    content = generate_pr_content(test_pack, "example.com")
    
    assert "branch_name" in content
    assert content["branch_name"].startswith("play/")
    assert "title" in content
    assert content["title"] == "Test Growth Experiment"
    assert "files" in content
    assert "decision_pack" in content["files"]
    assert "landing_page" in content["files"]
    assert "commit_message" in content
    assert "example.com" in content["commit_message"]


def test_load_pr_template():
    """Test PR template loading"""
    from executor.pr_executor import load_pr_template
    
    # Test fallback template when file doesn't exist
    template = load_pr_template()
    assert "Growth Experiment" in template
    assert "{hypothesis}" in template
    assert "{lift_level}" in template


def test_write_preview():
    """Test preview file writing"""
    from executor.pr_executor import write_preview
    
    content = {
        "branch_name": "play/test-branch",
        "title": "Test PR",
        "commit_message": "Test commit",
        "files": {
            "decision_pack": "test/pack.json",
            "landing_page": "test/page.html"
        },
        "domain": "example.com",
        "slug": "test-pr"
    }
    
    test_pack = {"title": "Test Pack"}
    lp_html = "<html><body>Test</body></html>"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        preview_path = write_preview(content, test_pack, lp_html, temp_dir)
        
        assert os.path.exists(preview_path)
        assert preview_path.endswith('_pr_preview.json')
        
        # Verify content
        with open(preview_path, 'r') as f:
            preview = json.load(f)
        
        assert preview["branch_name"] == "play/test-branch"
        assert preview["title"] == "Test PR"
        assert "diffs" in preview
        assert "decision_pack" in preview["diffs"]
        assert "landing_page" in preview["diffs"]


@patch('executor.pr_executor.Github')
def test_create_github_pr_success(mock_github):
    """Test successful GitHub PR creation"""
    from executor.pr_executor import create_github_pr
    
    # Setup mocks
    fake_github = FakeGithub()
    mock_github.return_value = fake_github
    
    content = {
        "branch_name": "play/test-branch",
        "title": "Test PR",
        "files": {
            "decision_pack": "test/pack.json",
            "landing_page": "test/page.html"
        }
    }
    
    test_pack = {"title": "Test Pack"}
    lp_html = "<html><body>Test</body></html>"
    
    # Test successful PR creation
    pr_url = create_github_pr(content, test_pack, lp_html, "fake_token", "test/repo")
    
    assert pr_url.startswith("https://github.com/test/repo/pull/")
    
    # Verify repository was accessed
    repo = fake_github.get_repo("test/repo")
    assert "test/pack.json" in repo.files
    assert "test/page.html" in repo.files
    assert len(repo.pulls) == 1


@patch('executor.pr_executor.Github')
def test_create_github_pr_branch_exists(mock_github):
    """Test GitHub PR creation with existing branch"""
    from executor.pr_executor import create_github_pr
    
    # Setup mocks
    fake_github = FakeGithub()
    mock_github.return_value = fake_github
    
    # Create existing branch
    repo = fake_github.get_repo("test/repo")
    repo.branches["play/test-branch"] = {"sha": "abc123"}
    
    content = {
        "branch_name": "play/test-branch",
        "title": "Test PR",
        "files": {
            "decision_pack": "test/pack.json",
            "landing_page": "test/page.html"
        }
    }
    
    test_pack = {"title": "Test Pack"}
    lp_html = "<html><body>Test</body></html>"
    
    # Should handle existing branch by appending timestamp
    pr_url = create_github_pr(content, test_pack, lp_html, "fake_token", "test/repo")
    
    assert pr_url.startswith("https://github.com/test/repo/pull/")
    # Branch name should be modified
    assert content["branch_name"] != "play/test-branch"


@patch('executor.pr_executor.Github')
def test_create_github_pr_invalid_repo(mock_github):
    """Test GitHub PR creation with invalid repo format"""
    from executor.pr_executor import create_github_pr
    
    content = {
        "branch_name": "play/test-branch",
        "title": "Test PR",
        "files": {
            "decision_pack": "test/pack.json",
            "landing_page": "test/page.html"
        }
    }
    
    test_pack = {"title": "Test Pack"}
    lp_html = "<html><body>Test</body></html>"
    
    # Test invalid repo format
    try:
        create_github_pr(content, test_pack, lp_html, "fake_token", "invalid-repo-format")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "format" in str(e)


def test_preview_or_create_pr_preview_mode():
    """Test PR preview mode (no GitHub token)"""
    from executor.pr_executor import preview_or_create_pr
    
    test_pack = {
        "title": "Test Pack",
        "hypothesis": "Test hypothesis",
        "expected_lift": {"level": "medium", "metric": "conversion"}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_pack, f)
        pack_path = f.name
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create output directory structure
            output_dir = os.path.join(temp_dir, "output", "decision_packs")
            os.makedirs(output_dir, exist_ok=True)
            
            # Move pack to output directory
            new_pack_path = os.path.join(output_dir, "test_pack.json")
            os.rename(pack_path, new_pack_path)
            
            result = preview_or_create_pr(
                pack_path=new_pack_path,
                lp_html="<html><body>Test</body></html>",
                domain="example.com"
            )
            
            assert result["success"] is True
            assert result["mode"] == "preview"
            assert "preview" in result["message"]
            assert result["url"].endswith('_pr_preview.json')
            assert os.path.exists(result["url"])
            
    except Exception as e:
        if os.path.exists(pack_path):
            os.unlink(pack_path)
        raise e


@patch('executor.pr_executor.Github')
def test_preview_or_create_pr_github_mode(mock_github):
    """Test PR creation mode with GitHub token"""
    from executor.pr_executor import preview_or_create_pr
    
    # Setup mocks
    fake_github = FakeGithub()
    mock_github.return_value = fake_github
    
    test_pack = {
        "title": "Test Pack",
        "hypothesis": "Test hypothesis",
        "expected_lift": {"level": "medium", "metric": "conversion"}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_pack, f)
        pack_path = f.name
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create output directory structure
            output_dir = os.path.join(temp_dir, "output", "decision_packs")
            os.makedirs(output_dir, exist_ok=True)
            
            # Move pack to output directory
            new_pack_path = os.path.join(output_dir, "test_pack.json")
            os.rename(pack_path, new_pack_path)
            
            result = preview_or_create_pr(
                pack_path=new_pack_path,
                lp_html="<html><body>Test</body></html>",
                domain="example.com",
                github_token="fake_token",
                github_repo="test/repo"
            )
            
            assert result["success"] is True
            assert result["mode"] == "pr_created"
            assert "successfully" in result["message"]
            assert result["url"].startswith("https://github.com/test/repo/pull/")
            
    except Exception as e:
        if os.path.exists(pack_path):
            os.unlink(pack_path)
        raise e


def test_preview_or_create_pr_error():
    """Test PR creation with error handling"""
    from executor.pr_executor import preview_or_create_pr
    
    # Test with non-existent pack file
    result = preview_or_create_pr(
        pack_path="non_existent_file.json",
        lp_html="<html><body>Test</body></html>",
        domain="example.com"
    )
    
    assert result["success"] is False
    assert result["mode"] == "error"
    assert "Failed to process PR" in result["message"]


if __name__ == "__main__":
    # Run tests
    import pytest
    pytest.main([__file__, "-v"])
