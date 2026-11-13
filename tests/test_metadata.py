"""Every file that states the release version states the same one."""

import json
import tomllib
from pathlib import Path

import mcp_todoist

ROOT = Path(__file__).resolve().parent.parent


def test_versions_agree():
    """pyproject, manifest, server.json (top level and each package) and __version__ match."""
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    manifest = json.loads((ROOT / "manifest.json").read_text())["version"]
    server = json.loads((ROOT / "server.json").read_text())
    stated = {
        "pyproject.toml": pyproject,
        "manifest.json": manifest,
        "server.json": server["version"],
        "mcp_todoist.__version__": mcp_todoist.__version__,
    }
    for i, package in enumerate(server.get("packages", [])):
        stated[f"server.json packages[{i}]"] = package["version"]
    assert len(set(stated.values())) == 1, stated
