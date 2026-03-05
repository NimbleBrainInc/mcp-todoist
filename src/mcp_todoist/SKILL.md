# Todoist MCP Server — Skill Guide

## Tools

| Tool | Use when... |
|------|-------------|
| `get_tasks` | You need to list or browse tasks — optionally by project or a filter like "today" or "overdue" |
| `create_task` | You need to add a new task, optionally with a due date, project, or priority |
| `complete_task` | You have a task ID and want to mark it as done |
| `update_task` | You need to change an existing task's content, due date, or priority |
| `get_projects` | You need to list all projects (e.g. to find a project ID before filtering tasks) |

## Context Reuse

- Use `id` from `get_tasks` results when calling `complete_task` or `update_task`
- Use `id` from `get_projects` results as `project_id` when calling `get_tasks` or `create_task`
- Use `id` from `create_task` response for follow-up `update_task` or `complete_task` calls

## Workflows

### 1. Daily Review
1. `get_tasks` with `filter="today"` to see what's due today
2. Summarize tasks by priority
3. For completed items: `complete_task` with each task's `id`

### 2. Quick Capture
1. `get_projects` to find the right project ID (if not Inbox)
2. `create_task` for each item — pass `content`, optional `due_string`, optional `project_id`
3. Confirm back the created task IDs

### 3. Reschedule Overdue Tasks
1. `get_tasks` with `filter="overdue"` to find all overdue tasks
2. For each task: `update_task` with a new `due_string` (e.g. "today", "tomorrow")
