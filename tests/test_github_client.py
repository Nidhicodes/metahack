import pytest
import respx
from httpx import Response
from app.github_client import GitHubClient, GITHUB_API_BASE_URL

REPO_URL = "https://github.com/atlanhq/atlan-sample-apps"
OWNER = "atlanhq"
REPO = "atlan-sample-apps"

@pytest.fixture
def github_client():
    return GitHubClient()

@respx.mock
async def test_get_repo_details_success(github_client: GitHubClient):
    mock_response = {
        "name": "atlan-sample-apps",
        "description": "Sample apps for Atlan",
        "owner": {"login": "atlanhq"},
        "topics": ["atlan", "sample-apps"],
        "html_url": REPO_URL,
    }
    respx.get(f"{GITHUB_API_BASE_URL}/repos/{OWNER}/{REPO}").mock(return_value=Response(200, json=mock_response))

    details = await github_client.get_repo_details(REPO_URL)

    assert details is not None
    assert details["name"] == "atlan-sample-apps"
    assert details["owner"] == "atlanhq"

@respx.mock
async def test_get_readme_content_success(github_client: GitHubClient):
    mock_response = "# Atlan Sample Apps"
    respx.get(f"{GITHUB_API_BASE_URL}/repos/{OWNER}/{REPO}/readme").mock(return_value=Response(200, text=mock_response))

    content = await github_client.get_readme_content(REPO_URL)

    assert content == mock_response

@respx.mock
async def test_get_file_tree_success(github_client: GitHubClient):
    mock_repo_response = {"default_branch": "main"}
    mock_tree_response = {
        "tree": [
            {"path": "README.md", "type": "blob"},
            {"path": "app", "type": "tree"},
        ]
    }
    respx.get(f"{GITHUB_API_BASE_URL}/repos/{OWNER}/{REPO}").mock(return_value=Response(200, json=mock_repo_response))
    respx.get(f"{GITHUB_API_BASE_URL}/repos/{OWNER}/{REPO}/git/trees/main?recursive=1").mock(return_value=Response(200, json=mock_tree_response))

    tree = await github_client.get_file_tree(REPO_URL)

    assert tree is not None
    assert len(tree) == 2
    assert tree[0]["path"] == "README.md"
