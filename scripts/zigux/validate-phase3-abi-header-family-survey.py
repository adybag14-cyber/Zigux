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
    "zigux/bindings/abi.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/uapi/version.zig",
    "zigux/tests/phase3_export_uapi.zig",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "make -C zigux phase3-validate",
    "make -C zigux phase3",
)
REQUIRED_SHARED_REMINDER_MARKERS = (
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "zigux/uapi/version.zig",
    "zigux/tests/README.md",
    "zigux/bindings/abi.zig",
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
    "zigux/tests/fixtures/phase3_abi/expected.json",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
)


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing survey note: {path}") from exc


def validate_text(text: str) -> list[str]:
    if "## Current packet" not in text:
        return ["missing current packet section"]
    if "## Review boundary" not in text:
        return ["missing review boundary section"]

    current_packet = text.split("## Current packet", 1)[1].split(
        "## Review boundary", 1
    )[0]
    missing = [
        marker for marker in REQUIRED_MARKERS if marker not in current_packet
    ]
    if "## Shared reminder" not in text:
        missing.append("missing shared reminder section")
        return missing

    shared_reminder = text.split("## Shared reminder", 1)[1]
    missing.extend(
        f"shared reminder missing marker: {marker}"
        for marker in REQUIRED_SHARED_REMINDER_MARKERS
        if marker not in shared_reminder
    )
    return missing


def run_self_test() -> int:
    sample = (
        "## Current packet\n"
        + "\n".join(REQUIRED_MARKERS)
        + "\n## Review boundary\n"
        + "boundary marker\n"
        + "\n## Shared reminder\n"
        + "\n".join(REQUIRED_SHARED_REMINDER_MARKERS)
    )
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

    broken = validate_text(sample.replace("zigux/bindings/abi.zig", "", 1))
    if "zigux/bindings/abi.zig" not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected bindings marker was not reported")
        return 1

    broken_sample = sample.rsplit("zigux/uapi/version.zig", 1)
    broken = validate_text("".join(broken_sample))
    if "shared reminder missing marker: zigux/uapi/version.zig" not in broken:
        print("PHASE3_ABI_HEADER_FAMILY_SURVEY_SELF_TEST=fail")
        print("expected shared reminder marker was not reported")
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
