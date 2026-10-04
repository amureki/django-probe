"""Collect Django setting names without inspecting setting values."""

from __future__ import annotations

import ast
import json
from collections import Counter
from importlib.resources import files
from pathlib import Path

from django_probe.config import django_settings_enabled


def _version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


_VOCABULARY_DIRECTORY = files("django_probe._vendor.django_settings")
DJANGO_SETTING_NAMES_BY_VERSION = {
    resource.name.removesuffix(".json"): frozenset(
        json.loads(resource.read_text(encoding="utf-8"))["names"]
    )
    for resource in sorted(
        (
            resource
            for resource in _VOCABULARY_DIRECTORY.iterdir()
            if resource.name.endswith(".json")
        ),
        key=lambda resource: _version_key(resource.name.removesuffix(".json")),
    )
}
DJANGO_SETTINGS_VERSIONS = tuple(DJANGO_SETTING_NAMES_BY_VERSION)
DJANGO_SETTING_NAMES = frozenset().union(*DJANGO_SETTING_NAMES_BY_VERSION.values())


def _assignment_names(target: ast.AST) -> list[str]:
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        names: list[str] = []
        for element in target.elts:
            names.extend(_assignment_names(element))
        return names
    return []


def configured_django_settings(
    root: Path,
    settings_files: list[ast.Module],
    vocabulary: frozenset[str] = DJANGO_SETTING_NAMES,
) -> tuple[Counter[str], bool]:
    """Count recognized module-level assignments in settings-like files."""
    if not django_settings_enabled(root):
        return Counter(), False

    counts: Counter[str] = Counter()
    for tree in settings_files:
        for node in tree.body:
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, ast.AnnAssign):
                targets = [node.target]
            else:
                continue
            for target in targets:
                counts.update(
                    name for name in _assignment_names(target) if name in vocabulary
                )
    return counts, True
