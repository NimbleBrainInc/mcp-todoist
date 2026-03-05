"""Tests for Todoist API models."""

from mcp_todoist.api_models import Due, Project, Task


def test_task_model() -> None:
    """Test Task model parsing from API response."""
    data = {
        "id": "task_123",
        "content": "Buy milk",
        "description": "From the store",
        "project_id": "proj_456",
        "priority": 2,
        "due": {
            "date": "2026-03-10",
            "string": "Mar 10",
            "is_recurring": False,
            "datetime": None,
            "timezone": None,
        },
        "is_completed": False,
        "labels": ["errands"],
        "created_at": "2026-03-05T00:00:00Z",
        "url": "https://todoist.com/showTask?id=task_123",
    }
    task = Task(**data)
    assert task.id == "task_123"
    assert task.content == "Buy milk"
    assert task.project_id == "proj_456"
    assert task.priority == 2
    assert task.due is not None
    assert task.due.date == "2026-03-10"
    assert task.labels == ["errands"]


def test_task_model_minimal() -> None:
    """Test Task model with only required fields."""
    task = Task(id="task_456", content="Simple task")
    assert task.id == "task_456"
    assert task.content == "Simple task"
    assert task.description == ""
    assert task.due is None
    assert task.labels == []
    assert task.is_completed is False


def test_due_model() -> None:
    """Test Due model."""
    due = Due(date="2026-03-10", string="Mar 10", is_recurring=False)
    assert due.date == "2026-03-10"
    assert due.string == "Mar 10"
    assert due.is_recurring is False
    assert due.datetime is None


def test_project_model() -> None:
    """Test Project model parsing."""
    data = {
        "id": "proj_123",
        "name": "Work",
        "color": "blue",
        "order": 1,
        "is_favorite": True,
        "is_inbox_project": False,
        "url": "https://todoist.com/showProject?id=proj_123",
    }
    project = Project(**data)
    assert project.id == "proj_123"
    assert project.name == "Work"
    assert project.is_favorite is True
    assert project.is_inbox_project is False


def test_project_model_minimal() -> None:
    """Test Project model with only required fields."""
    project = Project(id="proj_456", name="Inbox")
    assert project.id == "proj_456"
    assert project.name == "Inbox"
    assert project.color is None
    assert project.is_favorite is False
