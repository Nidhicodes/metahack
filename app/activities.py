from application_sdk.activities import ActivitiesInterface
from temporalio import activity
from app.github_client import GitHubClient
import os
from dotenv import load_dotenv
from application_sdk.services.statestore import StateStore, StateType
from typing import Dict, Any

load_dotenv()

class SourceSenseActivities(ActivitiesInterface):
    """
    defines the activities to get executed by the workflow
    """

    @activity.defn
    async def extract_github_metadata(self, repo_url: str) -> dict:
        """
        it connects to the GitHub API and extracts metadata for a given repository's URL
        """
        github_token = os.getenv("GITHUB_TOKEN")
        github_client = GitHubClient(token=github_token)
        try:
            repo_details = await github_client.get_repo_details(repo_url)
            readme_content = await github_client.get_readme_content(repo_url)
            file_tree = await github_client.get_file_tree(repo_url)

            return {
                "repo_details": repo_details,
                "readme_content": readme_content,
                "file_tree": file_tree,
            }
        finally:
            await github_client.close()

    @activity.defn
    async def get_workflow_arguments(self, workflow_id: str) -> Dict[str, Any]:
        """
        Fetches the workflow arguments from the StateStore.
        """
        return await StateStore.get_state(id=workflow_id, type=StateType.WORKFLOWS)