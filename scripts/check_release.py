#!/usr/bin/env python3
"""Read-only release readiness checks for UniApp projects."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


TARGETS = {
    "h5": ("build:h5", Path("dist/build/h5")),
    "weixin": ("build:mp-weixin", Path("dist/build/mp-weixin")),
    "alipay": ("build:mp-alipay", Path("dist/build/mp-alipay")),
}
TARGET_ALIASES = {
    "h5": "h5",
    "weixin": "weixin",
    "mp-weixin": "weixin",
    "alipay": "alipay",
    "mp-alipay": "alipay",
}
IGNORED_BUILD_FILES = {".DS_Store", "Thumbs.db"}


def finding(level: str, code: str, message: str, path: str = "") -> dict[str, str]:
    return {"level": level, "code": code, "message": message, "path": path}


def first_existing(root: Path, candidates: tuple[str, ...]) -> Path | None:
    for candidate in candidates:
        path = root / candidate
        if path.is_file():
            return path
    return None


def require_nonempty(path: Path, code: str, label: str) -> list[dict[str, str]]:
    try:
        if path.stat().st_size > 0:
            return []
    except OSError as exc:
        return [finding("error", code, f"cannot inspect {label}: {exc}", str(path))]
    return [finding("error", code, f"{label} must not be empty", str(path))]


def has_build_artifacts(path: Path) -> bool:
    return any(candidate.is_file() and candidate.name not in IGNORED_BUILD_FILES for candidate in path.rglob("*"))


def load_package(root: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    path = root / "package.json"
    if not path.is_file():
        return {}, [finding("error", "missing_package", "package.json is required", str(path))]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [finding("error", "invalid_package", f"cannot parse package.json: {exc}", str(path))]
    if not isinstance(data, dict):
        return {}, [finding("error", "invalid_package", "package.json must contain an object", str(path))]
    return data, []


def audit(root: Path, targets: list[str], require_builds: bool) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    package, package_findings = load_package(root)
    findings.extend(package_findings)
    scripts = package.get("scripts", {}) if isinstance(package, dict) else {}
    if not isinstance(scripts, dict):
        findings.append(finding("error", "invalid_scripts", "package.json scripts must be an object", str(root / "package.json")))
        scripts = {}

    manifest = first_existing(root, ("src/manifest.json", "manifest.json"))
    if manifest is None:
        findings.append(finding("error", "missing_manifest", "manifest.json or src/manifest.json is required"))
    else:
        findings.extend(require_nonempty(manifest, "empty_manifest", "manifest.json"))
    pages = first_existing(root, ("src/pages.json", "pages.json"))
    if pages is None:
        findings.append(finding("warning", "missing_pages", "pages.json was not found"))
    else:
        findings.extend(require_nonempty(pages, "empty_pages", "pages.json"))

    for target in targets:
        script_name, output = TARGETS[target]
        if not isinstance(scripts.get(script_name), str) or not scripts[script_name].strip():
            findings.append(finding("error", "missing_build_script", f"missing npm script {script_name}", "package.json"))
        output_path = root / output
        if not output_path.is_dir():
            level = "error" if require_builds else "warning"
            findings.append(finding(level, "missing_build_output", f"build output for {target} was not found", str(output_path)))
        elif not has_build_artifacts(output_path):
            level = "error" if require_builds else "warning"
            findings.append(finding(level, "empty_build_output", f"build output for {target} is empty", str(output_path)))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("--targets", default="h5,weixin,alipay", help="comma-separated: h5,weixin,alipay (mp-weixin/mp-alipay aliases are accepted)")
    parser.add_argument("--require-builds", action="store_true")
    parser.add_argument("--strict", action="store_true", help="return failure when warnings are present")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"error: project root not found or is not a directory: {root}", file=sys.stderr)
        return 2
    requested_targets = [value.strip().lower() for value in args.targets.split(",") if value.strip()]
    unknown = sorted(set(requested_targets) - set(TARGET_ALIASES))
    if unknown:
        print(f"error: unknown target(s): {', '.join(unknown)}", file=sys.stderr)
        return 2
    if not requested_targets:
        print("error: at least one target is required", file=sys.stderr)
        return 2
    targets = list(dict.fromkeys(TARGET_ALIASES[target] for target in requested_targets))

    findings = audit(root, targets, args.require_builds)
    errors = sum(item["level"] == "error" for item in findings)
    warnings = sum(item["level"] == "warning" for item in findings)
    result = {"root": str(root), "targets": targets, "errors": errors, "warnings": warnings, "findings": findings}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"targets={','.join(targets)} errors={errors} warnings={warnings}")
        for item in findings:
            suffix = f" ({item['path']})" if item["path"] else ""
            print(f"{item['level'].upper()} {item['code']}: {item['message']}{suffix}")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
