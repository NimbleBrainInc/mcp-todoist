"""Tests for Todoist MCP Server tools."""

from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from mcp_todoist.api_client import TodoistAPIError
from mcp_todoist.api_models import Project, Task

MOCK_TASK = Task(
    id="task_1",
    content="Buy milk",
    project_id="proj_1",
    priority=1,
    created_at="2026-03-05T00:00:00Z",
)

MOCK_PROJECT = Project(id="proj_1", name="Inbox", is_inbox_project=True)


@pytest.fixture
def mock_client():
    """Create a mock API client."""
    client = AsyncMock()
    client.get_tasks = AsyncMock(return_value=[MOCK_TASK])
    client.create_task = AsyncMock(return_value=MOCK_TASK)
    client.complete_task = AsyncMock(return_value=True)
    client.update_task = AsyncMock(return_value=MOCK_TASK)
    client.get_projects = AsyncMock(return_value=[MOCK_PROJECT])
    return client


@pytest.mark.asyncio
async def test_get_tasks(mock_client):
    """Test get_tasks tool."""
    with patch("mcp_todoist.server.get_client", return_value=mock_client):
        from mcp_todoist.server import get_tasks

        result = await get_tasks(limit=10)
        assert len(result) == 1
        assert result[0]["id"] == "task_1"
        mock_client.get_tasks.assert_called_once_with(project_id=None, filter=None, limit=10)


@pytest.mark.asyncio
async def test_get_tasks_with_filter(mock_client):
    """Test get_tasks tool with filter."""
    with patch("mcp_todoist.server.get_client", return_value=mock_client):
        from mcp_todoist.server import get_tasks

        await get_tasks(filter="today")
        mock_client.get_tasks.assert_called_once_with(project_id=None, filter="today", limit=50)


@pytest.mark.asyncio
async def test_create_task(mock_client):
    """Test create_task tool."""
    with patch("mcp_todoist.server.get_client", return_value=mock_client):
        from mcp_todoist.server import create_task

        result = await create_task(content="Buy milk", due_string="tomorrow")
        assert result["id"] == "task_1"
        mock_client.create_task.assert_called_once_with(
            content="Buy milk",
            description=None,
            project_id=None,
            due_string="tomorrow",
            priority=None,
        )


@pytest.mark.asyncio
async def test_complete_task(mock_client):
    """Test complete_task tool."""
    with patch("mcp_todoist.server.get_client", return_value=mock_client):
        from mcp_todoist.server import complete_task

        result = await complete_task(task_id="task_1")
        assert result["success"] is True
        assert result["task_id"] == "task_1"
        mock_client.complete_task.assert_called_once_with("task_1")


@pytest.mark.asyncio
async def test_update_task(mock_client):
    """Test update_task tool."""
    with patch("mcp_todoist.server.get_client", return_value=mock_client):
        from mcp_todoist.server import update_task

        result = await update_task(task_id="task_1", due_string="next Monday")
        assert result["id"] == "task_1"
        mock_client.update_task.assert_called_once_with(
            task_id="task_1",
            content=None,
            description=None,
            due_string="next Monday",
            priority=None,
        )


@pytest.mark.asyncio
async def test_get_projects(mock_client):
    """Test get_projects tool."""
    with patch("mcp_todoist.server.get_client", return_value=mock_client):
        from mcp_todoist.server import get_projects

        result = await get_projects()
        assert len(result) == 1
        assert result[0]["name"] == "Inbox"
        mock_client.get_projects.assert_called_once()


@pytest.mark.asyncio
async def test_get_tasks_api_error(mock_client):
    """An API error reaches the caller as a ToolError carrying its message."""
    mock_client.get_tasks = AsyncMock(side_effect=TodoistAPIError(401, "Unauthorized"))
    with patch("mcp_todoist.server.get_client", return_value=mock_client):
        from mcp_todoist.server import get_tasks

        with pytest.raises(ToolError, match="Unauthorized"):
            await get_tasks()


@pytest.mark.asyncio
async def test_api_error_reaches_an_mcp_client_as_an_error_result(mock_client):
    """Through the protocol, the failure is an error result, with no client log message."""
    mock_client.get_tasks = AsyncMock(side_effect=TodoistAPIError(401, "Unauthorized"))
    with patch("mcp_todoist.server.get_client", return_value=mock_client):
        from mcp_todoist.server import mcp

        async with Client(mcp) as client:
            with pytest.raises(ToolError, match="Unauthorized"):
                await client.call_tool("get_tasks", {})


@pytest.mark.asyncio
async def test_missing_token_is_a_tool_error(monkeypatch):
    """Without TODOIST_API_KEY the tool fails with a message naming the variable."""
    from mcp_todoist import server

    monkeypatch.setattr(server, "_client", None)
    monkeypatch.delenv("TODOIST_API_KEY", raising=False)
    with pytest.raises(ToolError, match="TODOIST_API_KEY"):
        await server.get_client()
