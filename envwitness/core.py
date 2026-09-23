from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
PROJECT_MARKERS = (
    "pyproject.toml",
    "requirements.txt",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "Cargo.toml",
    "Cargo.lock",
    "go.mod",
    "go.sum",
    "Dockerfile",
    "compose.yaml",
    "docker-compose.yml",
    ".devcontainer/devcontainer.json",
)
TOOLS = ("git", "node", "npm", "java")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tool_version(name: str) -> str | None:
    executable = shutil.which(name)
    if not executable:
        return None
    try:
        result = subprocess.run(
            [executable, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    value = (result.stdout or result.stderr).strip().splitlines()
    return value[0][:200] if value else None


def capture(root: Path) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"project directory does not exist: {root}")

    markers: dict[str, dict[str, str]] = {}
    for relative in PROJECT_MARKERS:
        path = root / relative
        if path.is_file():
            markers[relative] = {"sha256": _sha256(path), "size": str(path.stat().st_size)}

    tools = {name: _tool_version(name) for name in TOOLS}
    return {
        "schema_version": SCHEMA_VERSION,
        "runtime": {
            "os": platform.system(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
        },
        "tools": tools,
        "project": {"root_name": root.name, "markers": markers},
    }


def canonicalize(receipt: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(receipt, sort_keys=True, separators=(",", ":")))


def compare(left: dict[str, Any], right: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for category in ("runtime", "tools"):
        left_values = left.get(category, {})
        right_values = right.get(category, {})
        for key in sorted(set(left_values) | set(right_values)):
            if left_values.get(key) != right_values.get(key):
                findings.append({
                    "category": category,
                    "key": key,
                    "left": left_values.get(key),
                    "right": right_values.get(key),
                })

    left_markers = left.get("project", {}).get("markers", {})
    right_markers = right.get("project", {}).get("markers", {})
    for key in sorted(set(left_markers) | set(right_markers)):
        if left_markers.get(key) != right_markers.get(key):
            findings.append({
                "category": "project",
                "key": key,
                "left": left_markers.get(key),
                "right": right_markers.get(key),
            })
    return findings


def load(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read receipt {path}: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"unsupported receipt schema in {path}")
    return data
