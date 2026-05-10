#!/usr/bin/env python3
"""Validate the dedicated Phase 3 ABI header-family survey note."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SURVEY_PATH = Path("Documentation/zigux/phase3-abi-header-family-survey.md")
REQUIRED_MARKERS = (
    "include/linux/zigux.h",
    "include/zigux/abi.h",
    "zigux/kernel/export_shim.zig",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/tests/phase3_export_uapi.zig",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "make -C zigux phase3-validate",
    "make -C zigux phase3",
)


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing survey note: {path}") from exc


def validate_text(text: str) -> list[str]:
    return [marker for marker in REQUIRED_MARKERS if marker not in text]


def run_self_test() -> int:
    sample = "\n".join(REQUIRED_MARKERS)
    missing = validate_text(sample)
    if missing:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("\n".join(missing))
        return 1

    broken = validate_text(sample.replace("include/zigux/abi.h", "", 1))
    if "include/zigux/abi.h" not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected missing marker was not reported")
        return 1

    print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains Documentation/zigux/",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in validator coverage without reading repo files",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    survey_path = args.repo_root / SURVEY_PATH
    text = load_text(survey_path)
    missing = validate_text(text)
    if missing:
        for marker in missing:
            print(f"missing marker: {marker}", file=sys.stderr)
        return 1

    print(f"validated {survey_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
