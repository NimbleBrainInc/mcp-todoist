"""Todoist MCP Server - FastMCP Implementation."""

import logging
import os
import sys
from importlib.resources import files

from fastmcp import Context, FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp_todoist.api_client import TodoistAPIError, TodoistClient

# Logging setup - all logs to stderr (stdout is reserved for JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mcp_todoist")

logger.info("Todoist server module loading...")

SKILL_CONTENT = files("mcp_todoist").joinpath("SKILL.md").read_text()

# Create MCP server
mcp = FastMCP(
    "Todoist",
    instructions="Read the skill resource at skill://todoist/usage before using tools.",
)

# Global client instance (lazy initialization)
_client: TodoistClient | None = None


@mcp.resource("skill://todoist/usage")
def get_skill() -> str:
    """Tool selection guide and workflow patterns for this server."""
    return SKILL_CONTENT


def get_client(ctx: Context | None = None) -> TodoistClient:
    """Get or create the API client instance."""
    global _client
    if _client is None:
        api_key = os.environ.get("TODOIST_API_KEY")
        if not api_key:
            msg = "TODOIST_API_KEY environment variable is required"
            if ctx:
                ctx.error(msg)
            raise ValueError(msg)
        _client = TodoistClient(api_key=api_key)
    return _client


# Health endpoint for HTTP transport
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for monitoring."""
    return JSONResponse({"status": "healthy", "service": "mcp-todoist"})


# ============================================================================
# Tools
# ============================================================================


@mcp.tool()
async def get_tasks(
    project_id: str | None = None,
    filter: str | None = None,
    limit: int = 50,
    ctx: Context | None = None,
) -> list[dict]:
    """List tasks from Todoist.

    Args:
        project_id: Filter tasks by project ID (optional)
        filter: Todoist filter string, e.g. "today", "overdue", "p1" (optional)
        limit: Maximum number of tasks to return (default 50)
        ctx: MCP context for logging

    Returns:
        List of tasks
    """
    client = get_client(ctx)
    try:
        tasks = await client.get_tasks(project_id=project_id, filter=filter, limit=limit)
        return [t.model_dump() for t in tasks]
    except TodoistAPIError as e:
        if ctx:
            ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def create_task(
    content: str,
    description: str | None = None,
    project_id: str | None = None,
    due_string: str | None = None,
    priority: int | None = None,
    ctx: Context | None = None,
) -> dict:
    """Create a new task in Todoist.

    Args:
        content: Task title/content (required)
        description: Optional longer description
        project_id: Project to add the task to (defaults to Inbox)
        due_string: Natural language due date, e.g. "tomorrow", "next Monday", "Jan 15"
        priority: Priority level: 1=normal, 2=medium, 3=high, 4=urgent
        ctx: MCP context for logging

    Returns:
        The created task
    """
    client = get_client(ctx)
    try:
        task = await client.create_task(
            content=content,
            description=description,
            project_id=project_id,
            due_string=due_string,
            priority=priority,
        )
        return task.model_dump()
    except TodoistAPIError as e:
        if ctx:
            ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def complete_task(
    task_id: str,
    ctx: Context | None = None,
) -> dict:
    """Mark a task as completed.

    Args:
        task_id: The ID of the task to complete
        ctx: MCP context for logging

    Returns:
        Confirmation with the completed task ID
    """
    client = get_client(ctx)
    try:
        await client.complete_task(task_id)
        return {"success": True, "task_id": task_id}
    except TodoistAPIError as e:
        if ctx:
            ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def update_task(
    task_id: str,
    content: str | None = None,
    description: str | None = None,
    due_string: str | None = None,
    priority: int | None = None,
    ctx: Context | None = None,
) -> dict:
    """Update an existing task.

    Args:
        task_id: The ID of the task to update
        content: New task title/content (optional)
        description: New description (optional)
        due_string: New due date as natural language, e.g. "tomorrow", "next Friday" (optional)
        priority: New priority: 1=normal, 2=medium, 3=high, 4=urgent (optional)
        ctx: MCP context for logging

    Returns:
        The updated task
    """
    client = get_client(ctx)
    try:
        task = await client.update_task(
            task_id=task_id,
            content=content,
            description=description,
            due_string=due_string,
            priority=priority,
        )
        return task.model_dump()
    except TodoistAPIError as e:
        if ctx:
            ctx.error(f"API error: {e.message}")
        raise


@mcp.tool()
async def get_projects(
    ctx: Context | None = None,
) -> list[dict]:
    """List all Todoist projects.

    Args:
        ctx: MCP context for logging

    Returns:
        List of projects with their IDs and names
    """
    client = get_client(ctx)
    try:
        projects = await client.get_projects()
        return [p.model_dump() for p in projects]
    except TodoistAPIError as e:
        if ctx:
            ctx.error(f"API error: {e.message}")
        raise


# ============================================================================
# Entrypoints
# ============================================================================

# ASGI app for HTTP deployment (uvicorn mcp_todoist.server:app)
app = mcp.http_app()

# Stdio entrypoint for Claude Desktop / mpak
if __name__ == "__main__":
    logger.info("Running in stdio mode")
    mcp.run()
