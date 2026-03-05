"""Async HTTP client for Todoist API."""

import os
from typing import Any

import aiohttp
from aiohttp import ClientError

from mcp_todoist.api_models import Project, Task


class TodoistAPIError(Exception):
    """Exception raised for Todoist API errors."""

    def __init__(self, status: int, message: str, details: dict[str, Any] | None = None) -> None:
        self.status = status
        self.message = message
        self.details = details
        super().__init__(f"Todoist API Error {status}: {message}")


class TodoistClient:
    """Async client for Todoist API."""

    BASE_URL = "https://api.todoist.com/api/v1"

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key or os.environ.get("TODOIST_API_KEY")
        if not self.api_key:
            raise ValueError("TODOIST_API_KEY is required")
        self.timeout = timeout
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "TodoistClient":
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def _ensure_session(self) -> None:
        if not self._session:
            headers = {
                "User-Agent": "mcp-server-todoist/0.1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            self._session = aiohttp.ClientSession(
                headers=headers, timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_data: Any | None = None,
    ) -> Any:
        """Make an HTTP request to the Todoist API."""
        await self._ensure_session()
        url = f"{self.BASE_URL}{path}"

        if params:
            params = {k: v for k, v in params.items() if v is not None}

        try:
            if not self._session:
                raise RuntimeError("Session not initialized")

            kwargs: dict[str, Any] = {}
            if json_data is not None:
                kwargs["json"] = json_data
            if params:
                kwargs["params"] = params

            async with self._session.request(method, url, **kwargs) as response:
                if response.status >= 400:
                    try:
                        result = await response.json()
                    except Exception:
                        result = {}
                    error_msg = "Unknown error"
                    if isinstance(result, dict):
                        error_msg = result.get("error", result.get("message", error_msg))
                    raise TodoistAPIError(response.status, str(error_msg), result)

                # 204 No Content — nothing to parse
                if response.status == 204 or response.content_length == 0:
                    return {}

                return await response.json()

        except ClientError as e:
            raise TodoistAPIError(500, f"Network error: {str(e)}") from e

    def _extract_list(self, data: Any) -> list[dict[str, Any]]:
        """Extract items from either an array or paginated response."""
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("results", data.get("items", []))
        return []

    # ========================================================================
    # Tasks
    # ========================================================================

    async def get_tasks(
        self,
        project_id: str | None = None,
        filter: str | None = None,
        limit: int = 50,
    ) -> list[Task]:
        """List tasks, optionally filtered by project or a Todoist filter string."""
        params: dict[str, Any] = {"limit": limit}
        if project_id:
            params["project_id"] = project_id
        if filter:
            params["filter"] = filter
        data = await self._request("GET", "/tasks", params=params)
        return [Task(**item) for item in self._extract_list(data)]

    async def create_task(
        self,
        content: str,
        description: str | None = None,
        project_id: str | None = None,
        due_string: str | None = None,
        priority: int | None = None,
    ) -> Task:
        """Create a new task."""
        body: dict[str, Any] = {"content": content}
        if description is not None:
            body["description"] = description
        if project_id is not None:
            body["project_id"] = project_id
        if due_string is not None:
            body["due_string"] = due_string
        if priority is not None:
            body["priority"] = priority
        data = await self._request("POST", "/tasks", json_data=body)
        return Task(**data)

    async def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed."""
        await self._request("POST", f"/tasks/{task_id}/close")
        return True

    async def update_task(
        self,
        task_id: str,
        content: str | None = None,
        description: str | None = None,
        due_string: str | None = None,
        priority: int | None = None,
    ) -> Task:
        """Update an existing task."""
        body: dict[str, Any] = {}
        if content is not None:
            body["content"] = content
        if description is not None:
            body["description"] = description
        if due_string is not None:
            body["due_string"] = due_string
        if priority is not None:
            body["priority"] = priority
        data = await self._request("POST", f"/tasks/{task_id}", json_data=body)
        return Task(**data)

    # ========================================================================
    # Projects
    # ========================================================================

    async def get_projects(self) -> list[Project]:
        """List all projects."""
        data = await self._request("GET", "/projects")
        return [Project(**item) for item in self._extract_list(data)]
