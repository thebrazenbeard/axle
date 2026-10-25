"""Fail-closed static checks for AXLE editor startup configuration."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _has_key(value, key):
    if isinstance(value, dict):
        return key in value or any(_has_key(v, key) for v in value.values())
    if isinstance(value, list):
        return any(_has_key(v, key) for v in value)
    return False


def _has_value(value, wanted):
    if isinstance(value, str):
        return value == wanted
    if isinstance(value, dict):
        return any(_has_value(v, wanted) for v in value.values())
    if isinstance(value, list):
        return any(_has_value(v, wanted) for v in value)
    return False


def _check_tasks(raw):
    doc = json.loads(raw)
    if not isinstance(doc, dict) or doc.get("tasks") != []:
        raise AssertionError("AXLE must not register editor tasks")
    if _has_key(doc, "runOn") or _has_value(doc, "folderOpen"):
        raise AssertionError("folder-open execution must not be configured")


def _check_settings(raw):
    doc = json.loads(raw)
    if not isinstance(doc, dict):
        raise AssertionError("settings must be an object")
    for disallowed in ("task.allowAutomaticTasks", "tasks", "runOn"):
        if _has_key(doc, disallowed):
            raise AssertionError(f"disallowed editor setting: {disallowed}")
    if _has_value(doc, "folderOpen"):
        raise AssertionError("folder-open setting must not be configured")


class EditorStartupSafety(unittest.TestCase):
    def test_no_auto_registered_tasks(self):
        _check_tasks((ROOT / ".vscode" / "tasks.json").read_text(encoding="utf-8"))

    def test_no_workspace_auto_task_policy(self):
        _check_settings((ROOT / ".vscode" / "settings.json").read_text(encoding="utf-8"))

    def test_disguised_loader_absent(self):
        self.assertFalse((ROOT / "public" / "fonts" / "fa-solid.lkf").exists())

    def test_nested_and_escaped_folder_open_rejected(self):
        for candidate in (
            '{"tasks": [], "windows": {"runOptions": {"runOn": "folderOpen"}}}',
            '{"tasks": [], "tasksAlias": [{"runOptions": {"run\\u004fn": "folderOpen"}}]}',
            '{"tasks": [], "linux": {"runOptions": {"runOn": "folder\\u004fpen"}}}',
        ):
            with self.subTest(candidate=candidate), self.assertRaises(AssertionError):
                _check_tasks(candidate)

    def test_nested_settings_rejected(self):
        for candidate in (
            '{"task.allowAutomaticTasks": false}',
            '{"windows": {"task.allowAutomaticTasks": "off"}}',
            '{"nested": {"tasks": {"runOn": "folderOpen"}}}',
            '{"nested": {"run\\u004fn": "folderOpen"}}',
        ):
            with self.subTest(candidate=candidate), self.assertRaises(AssertionError):
                _check_settings(candidate)

    def test_invalid_json_fails_closed(self):
        for candidate in ('{"tasks": [', '[]'):
            with self.subTest(candidate=candidate), self.assertRaises((AssertionError, ValueError)):
                _check_tasks(candidate)


if __name__ == "__main__":
    unittest.main()
