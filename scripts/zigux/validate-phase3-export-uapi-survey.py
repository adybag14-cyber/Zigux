#!/usr/bin/env python3
"""Validate the current bounded Phase 3 export/UAPI survey packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SURVEY_PATH = Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md")
LINUX_HEADER_PATH = Path("include/linux/zigux.h")
C_HEADER_SMOKE_PATH = Path("zigux/tests/phase3_export_uapi_c_header_smoke.c")

REQUIRED_MARKERS = {
    SURVEY_PATH: (
        "PHASE3_LINUX_ZIGUX_H_STATUS_OK_RELAY=zigux_uapi_export_status_ok",
        "include/linux/zigux.h` now includes the bounded `zigux_uapi_export_status_ok()` relay",
        "PHASE3_EXPORT_UAPI_GAP=broader curated UAPI families and wider export-shim coverage remain open after the landed starter packet",
    ),
    LINUX_HEADER_PATH: (
        "static inline int zigux_uapi_export_status_ok(struct zigux_export_status status)",
        "return zigux_export_status_ok(status);",
    ),
    C_HEADER_SMOKE_PATH: (
        "if (!zigux_uapi_export_status_ok(valid))",
        "if (zigux_uapi_export_status_ok(invalid))",
        "if (!zigux_uapi_export_status_ok(ok))",
        "if (zigux_uapi_export_status_ok(err))",
        "if (!zigux_uapi_export_status_ok(unknown))",
    ),
}

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")

def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")
    return issues

def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_survey_") as temp_dir:
        root = Path(temp_dir)
        for relative_path, markers in REQUIRED_MARKERS.items():
            _write(root / relative_path, "\n".join(markers) + "\n")
        issues = validate_repo(root)
        if issues:
            print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        text = _read(root / SURVEY_PATH).replace("PHASE3_LINUX_ZIGUX_H_STATUS_OK_RELAY=zigux_uapi_export_status_ok", "", 1)
        _write(root / SURVEY_PATH, text)
        issues = validate_repo(root)
        expected = "missing Documentation/zigux/phase3-export-uapi-boundary-survey.md marker: PHASE3_LINUX_ZIGUX_H_STATUS_OK_RELAY=zigux_uapi_export_status_ok"
        if expected not in issues:
            print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=fail")
            print("expected survey status-ok marker removal to fail validation")
            return 1
        for relative_path, markers in REQUIRED_MARKERS.items():
            _write(root / relative_path, "\n".join(markers) + "\n")
        text = _read(root / LINUX_HEADER_PATH).replace("static inline int zigux_uapi_export_status_ok(struct zigux_export_status status)", "", 1)
        _write(root / LINUX_HEADER_PATH, text)
        issues = validate_repo(root)
        expected = "missing include/linux/zigux.h marker: static inline int zigux_uapi_export_status_ok(struct zigux_export_status status)"
        if expected not in issues:
            print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=fail")
            print("expected linux header status-ok relay removal to fail validation")
            return 1
    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST=pass")
    print("PHASE3_EXPORT_UAPI_SURVEY_SELF_TEST_CASES=3")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path('.'))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_EXPORT_UAPI_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1
    print(f"validated {args.repo_root / SURVEY_PATH}")
    print("PHASE3_EXPORT_UAPI_SURVEY=pass")
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
