import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from envwitness.core import SCHEMA_VERSION, capture, compare, load


class CaptureTests(unittest.TestCase):
    def test_capture_uses_allowlisted_project_files_and_hashes_contents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
            (root / ".env").write_text("TOKEN=do-not-capture\n", encoding="utf-8")

            with patch("envwitness.core._tool_version", return_value=None):
                receipt = capture(root)

            self.assertEqual(receipt["schema_version"], SCHEMA_VERSION)
            self.assertIn("pyproject.toml", receipt["project"]["markers"])
            self.assertNotIn(".env", receipt["project"]["markers"])
            serialized = json.dumps(receipt)
            self.assertNotIn("do-not-capture", serialized)

    def test_capture_is_stable_for_same_project_when_tools_are_fixed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package.json").write_text("{}", encoding="utf-8")
            with patch("envwitness.core._tool_version", return_value="tool 1"):
                first = capture(root)
                second = capture(root)
            self.assertEqual(first, second)


class CompareTests(unittest.TestCase):
    def test_compare_reports_runtime_tool_and_marker_drift(self):
        left = {
            "schema_version": 1,
            "runtime": {"python_version": "3.12"},
            "tools": {"git": "2.40"},
            "project": {"markers": {"pyproject.toml": {"sha256": "a", "size": "1"}}},
        }
        right = {
            "schema_version": 1,
            "runtime": {"python_version": "3.13"},
            "tools": {"git": "2.41"},
            "project": {"markers": {"pyproject.toml": {"sha256": "b", "size": "1"}}},
        }
        findings = compare(left, right)
        self.assertEqual([item["category"] for item in findings], ["runtime", "tools", "project"])

    def test_identical_receipts_have_no_drift(self):
        receipt = {"schema_version": 1, "runtime": {}, "tools": {}, "project": {"markers": {}}}
        self.assertEqual(compare(receipt, receipt), [])

    def test_load_rejects_unknown_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"schema_version": 999}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load(path)


if __name__ == "__main__":
    unittest.main()
