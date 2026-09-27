import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "check_release.py"


class ReleaseGuardTests(unittest.TestCase):
    def run_check(self, root, *args):
        return subprocess.run([sys.executable, str(SCRIPT), str(root), "--json", *args], text=True, capture_output=True)

    def test_valid_h5_source_without_build_is_warning(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package.json").write_text(json.dumps({"scripts": {"build:h5": "uni build -p h5"}}), encoding="utf-8")
            (root / "manifest.json").write_text("{}", encoding="utf-8")
            (root / "pages.json").write_text("{}", encoding="utf-8")
            result = self.run_check(root, "--targets", "h5")
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(report["errors"], 0)
            self.assertEqual(report["warnings"], 1)

    def test_missing_script_and_required_build_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package.json").write_text(json.dumps({"scripts": {}}), encoding="utf-8")
            (root / "manifest.json").write_text("{}", encoding="utf-8")
            result = self.run_check(root, "--targets", "alipay", "--require-builds")
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1)
            self.assertGreaterEqual(report["errors"], 2)

    def test_platform_aliases_are_normalized_and_deduplicated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = {"build:mp-weixin": "uni build -p mp-weixin"}
            (root / "package.json").write_text(json.dumps({"scripts": scripts}), encoding="utf-8")
            (root / "manifest.json").write_text("{}", encoding="utf-8")
            (root / "pages.json").write_text("{}", encoding="utf-8")
            result = self.run_check(root, "--targets", "mp-weixin,weixin")
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(report["targets"], ["weixin"])
            self.assertEqual(report["warnings"], 1)

    def test_strict_mode_fails_on_warnings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package.json").write_text(json.dumps({"scripts": {"build:h5": "uni build -p h5"}}), encoding="utf-8")
            (root / "manifest.json").write_text("{}", encoding="utf-8")
            (root / "pages.json").write_text("{}", encoding="utf-8")
            result = self.run_check(root, "--targets", "h5", "--strict")
            report = json.loads(result.stdout)
            self.assertEqual(report["errors"], 0)
            self.assertEqual(report["warnings"], 1)
            self.assertEqual(result.returncode, 1)

    def test_missing_project_root_is_reported_clearly(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing"
            result = self.run_check(missing, "--targets", "h5")
            self.assertEqual(result.returncode, 2)
            self.assertIn("project root not found", result.stderr)
            self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
