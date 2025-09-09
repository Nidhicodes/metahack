import asyncio
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from application_sdk.application import BaseApplication
from application_sdk.observability.logger_adaptor import get_logger
from app.workflow import SourceSenseWorkflow
from app.activities import SourceSenseActivities
import uvicorn
import json
import time

logger = get_logger(__name__)

APPLICATION_NAME = "sourcesense"

templates = Jinja2Templates(directory="frontend/templates")
class SourceSenseApp(BaseApplication):
    def __init__(self, name: str):
        super().__init__(name=name)

    async def homepage(self, request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    async def extract(self, request: Request, repo_url: str = Form(...)):
        try:
            client = self.workflow_client
            
            logger.info(f"Starting workflow with repo_url: {repo_url}")
            
            workflow_args = {"repo_url": repo_url}
            
            response = await client.start_workflow(
                workflow_args=workflow_args,
                workflow_class=SourceSenseWorkflow
            )

            handle = response.get("handle")
            if not handle:
                raise Exception("Could not get workflow handle from start_workflow response.")

            result = await handle.result()
            
            logger.info("Workflow completed successfully")
            return templates.TemplateResponse("index.html", {"request": request, "result": result})
                
        except Exception as e:
            logger.error(f"Error in workflow execution: {e}", exc_info=True)
            return templates.TemplateResponse("index.html", {"request": request, "error": str(e)})


def create_fastapi_app(source_sense_app):
    """Create a FastAPI application with our routes"""
    fastapi_app = FastAPI(title="SourceSense", description="Source Code Analysis Tool")
    
    fastapi_app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
   
    @fastapi_app.get("/", response_class=HTMLResponse)
    async def homepage(request: Request):
        return await source_sense_app.homepage(request)
        
    @fastapi_app.post("/extract", response_class=HTMLResponse) 
    async def extract(request: Request, repo_url: str = Form(...)):
        return await source_sense_app.extract(request, repo_url)
    
    return fastapi_app


async def setup_background_services():
    """Setup the workflow services in the background"""
    logger.info("Setting up background services...")
    app = SourceSenseApp(name=APPLICATION_NAME)

    await app.setup_workflow(
        workflow_and_activities_classes=[(SourceSenseWorkflow, SourceSenseActivities)],
    )

    await app.start_worker()
    
    logger.info("Background services setup completed")
    return app


async def main():
    logger.info("Starting SourceSense application")
    
    source_sense_app = await setup_background_services()
    
    fastapi_app = create_fastapi_app(source_sense_app)
    
    logger.info("Starting web server on http://0.0.0.0:8001")
    config = uvicorn.Config(
        fastapi_app, 
        host="0.0.0.0", 
        port=8001, 
        log_level="info",
        access_log=True
    )
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())