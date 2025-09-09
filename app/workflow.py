from datetime import timedelta
from typing import Any, Callable, Dict, Sequence

from temporalio import workflow
from app.activities import SourceSenseActivities
from application_sdk.workflows import WorkflowInterface
from application_sdk.activities import ActivitiesInterface


@workflow.defn
class SourceSenseWorkflow(WorkflowInterface):
    """
    The main workflow for the SourceSense application.
    """

    @workflow.run
    async def run(self, workflow_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Entry point for the workflow's execution.
        """
        workflow_id = workflow_input.get("workflow_id")
        if not workflow_id:
            raise ValueError("Could not find 'workflow_id' in workflow arguments.")

        workflow_args = await workflow.execute_activity(
            SourceSenseActivities.get_workflow_arguments,
            workflow_id,
            start_to_close_timeout=timedelta(seconds=30),
        )
        
        repo_url = workflow_args.get("repo_url")
        if not repo_url:
            raise ValueError("'repo_url' is a required workflow argument in the StateStore.")

        return await workflow.execute_activity(
            SourceSenseActivities.extract_github_metadata,
            repo_url,
            start_to_close_timeout=timedelta(minutes=5),
        )

    @staticmethod
    def get_activities(activities: ActivitiesInterface) -> Sequence[Callable[..., Any]]:
        """
        Registers the particular activity to be used.
        """
        return [
            SourceSenseActivities.extract_github_metadata,
            SourceSenseActivities.get_workflow_arguments,
        ]