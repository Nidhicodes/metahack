import httpx
from typing import Any, Dict, List, Optional

GITHUB_API_BASE_URL="https://api.github.com"

class GitHubClient:
    """
    Asynchronous client to interact with GitHub API
    """
    def __init__(self, token: Optional[str]=None):
        """
        Initializes the client with a GitHub Personal Access Token (PAT)
        """
        headers={
            "Accept":"application/vnd.github.v3+json",
            "X-GitHub-Api-Version":"2022-11-28"
        }
        if token:
            headers["Authorization"]=f"Bearer {token}"

        self.client=httpx.AsyncClient(base_url=GITHUB_API_BASE_URL, headers=headers)

    async def _get_repo_parts(self, repo_url:str)->Optional[tuple[str, str]]:
        """
        helper to parse a GitHub url and extract the owner and repo parts
        """
        try:
            parts=repo_url.strip("/").split("/")
            if len(parts)>=2 and parts[-2] and parts[-1]:
                return parts[-2], parts[-1]
            return None
        except Exception:
            return None
        
    async def get_repo_details(self, repo_url:str)->Optional[Dict[str,Any]]:
        """
        to fetch basic details of the repository like name, description, etc
        """
        repo_parts=await self._get_repo_parts(repo_url)
        if not repo_parts:
            return None
        owner, repo=repo_parts

        try:
            response= await self.client.get(f"/repos/{owner}/{repo}")
            response.raise_for_status()
            data=response.json()

            return {
                "name":data.get("name"),
                "description":data.get("description","No description provided."),
                "owner":data.get("owner",{}).get("login"),
                "topics":data.get("topics",[]),
                "url":data.get("html_url")
            }
        except httpx.HTTPStatusError:
            return None
        
    async def get_readme_content(self, repo_url:str)->Optional[str]:
        """
        fetches raw content of the repository's README file.
        """
        repo_parts=await self._get_repo_parts(repo_url)
        if not repo_parts:
            return None
        owner, repo=repo_parts

        try:
            response=await self.client.get(f"/repos/{owner}/{repo}/readme", headers={"Accept": "application/vnd.github.raw"})
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError:
            return "No README file found for this repository."
        
    async def get_file_tree(self, repo_url:str)->Optional[List[Dict[str,str]]]:
        """
        fetches the entire file and directory structure of the repository's dafault branch
        """
        repo_parts=await self._get_repo_parts(repo_url)
        if not repo_parts:
            return None
        owner, repo=repo_parts

        try:
            repo_details_response=await self.client.get(f"/repos/{owner}/{repo}")
            repo_details_response.raise_for_status()
            default_branch=repo_details_response.json().get("default_branch")
            if not default_branch:
                return None
            
            tree_response=await self.client.get(f"/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1")
            tree_response.raise_for_status()

            tree_data=tree_response.json().get("tree",[])

            return [{"path":item["path"], "type":item["type"]} for item in tree_data]
        
        except httpx.HTTPStatusError:
            return None
        
    async def close(self):
        """
        to close underlying HTTP client session.
        """
        await self.client.aclose()