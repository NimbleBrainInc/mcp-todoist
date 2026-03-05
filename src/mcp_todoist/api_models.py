"""Pydantic models for Todoist API responses."""

from pydantic import BaseModel, Field


class Due(BaseModel):
    """Task due date information."""

    date: str | None = Field(None, description="Due date in YYYY-MM-DD format")
    datetime: str | None = Field(None, description="Due datetime in ISO 8601 format")
    string: str | None = Field(None, description="Human-readable due date string")
    is_recurring: bool = Field(False, description="Whether the task recurs")
    timezone: str | None = Field(None, description="Timezone for the due datetime")


class Task(BaseModel):
    """A Todoist task."""

    id: str = Field(..., description="Task ID")
    content: str = Field(..., description="Task content/title")
    description: str = Field("", description="Task description")
    project_id: str | None = Field(None, description="Project ID")
    section_id: str | None = Field(None, description="Section ID")
    parent_id: str | None = Field(None, description="Parent task ID for subtasks")
    order: int = Field(0, description="Position within the project")
    priority: int = Field(1, description="Priority: 1=normal, 2=medium, 3=high, 4=urgent")
    due: Due | None = Field(None, description="Due date information")
    is_completed: bool = Field(False, description="Whether the task is completed")
    labels: list[str] = Field(default_factory=list, description="Labels attached to the task")
    creator_id: str | None = Field(None, description="Creator user ID")
    created_at: str | None = Field(None, description="Creation timestamp (ISO 8601)")
    url: str | None = Field(None, description="Task URL in Todoist")


class Project(BaseModel):
    """A Todoist project."""

    id: str = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    color: str | None = Field(None, description="Project color")
    parent_id: str | None = Field(None, description="Parent project ID")
    order: int = Field(0, description="Position in the project list")
    is_favorite: bool = Field(False, description="Whether the project is a favorite")
    is_inbox_project: bool = Field(False, description="Whether this is the Inbox project")
    url: str | None = Field(None, description="Project URL in Todoist")
