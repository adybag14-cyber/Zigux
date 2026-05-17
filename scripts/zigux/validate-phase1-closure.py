#!/usr/bin/env python3
"""Validate the current-master-safe Phase 1 closure anchor."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_HELPERS = [
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
]

REQUIRED_NOTE_MARKERS = [
    "`PHASE1_STATUS=parked`",
    "`PHASE1_CLOSURE_RESTORE_STATE=partial`",
    "`PHASE1_HELPER_COUNT=13`",
    "manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`",
    "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,zigux/tests/fixtures/phase1_helper_manifest.json`",
    "`PHASE1_SHARED_REMINDER_SYNC_STATE=pending`",
    "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,scripts/zigux/check-phase1-bench.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c,zigux/Makefile`",
    "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
]

REQUIRED_BUILD_MARKERS = [
    'const phase1_step = b.step(',
    '"Run the shared Phase 1 host-tools smoke anchor from zigux/tests"',
    '"phase1_host_tools_smoke.zig"',
]

REQUIRED_SMOKE_MARKERS = [
    '@hasDecl(argv_split, "argvSplit")',
    '@hasDecl(cmdline, "memparse")',
    '@hasDecl(find_bit, "findFirstBit")',
    '@hasDecl(bitmap, "setRange")',
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_once(text: str, marker: str, label: str, failures: list[str]) -> None:
    count = text.count(marker)
    if count != 1:
        failures.append(f"{label}:expected=1:actual={count}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else DEFAULT_ROOT.resolve()
    note_path = root / "Documentation/zigux/phase1-closure.md"
    manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
    build_path = root / "zigux/tests/build.zig"
    smoke_path = root / "zigux/tests/phase1_host_tools_smoke.zig"

    failures: list[str] = []
    for path in (note_path, manifest_path, build_path, smoke_path):
        if not path.exists():
            failures.append(f"missing_file:{path.relative_to(root).as_posix()}")
    if failures:
        for item in failures:
            print(item)
        return 1

    note_text = read_text(note_path)
    build_text = read_text(build_path)
    smoke_text = read_text(smoke_path)
    manifest = json.loads(read_text(manifest_path))

    for marker in REQUIRED_NOTE_MARKERS:
        require_once(note_text, marker, "phase1_closure_note", failures)
    for marker in REQUIRED_BUILD_MARKERS:
        require_once(build_text, marker, "build_zig", failures)
    for marker in REQUIRED_SMOKE_MARKERS:
        require_once(smoke_text, marker, "phase1_host_tools_smoke", failures)

    if manifest.get("phase") != "Phase 1":
        failures.append("manifest:phase")
    if manifest.get("status") != "closed":
        failures.append("manifest:status")
    if manifest.get("helper_count") != 13:
        failures.append("manifest:helper_count")
    if manifest.get("helpers") != EXPECTED_HELPERS:
        failures.append("manifest:helpers")

    if failures:
        for item in failures:
            print(item)
        return 1

    print("PHASE1_CLOSURE_VALIDATION=pass")
    print("PHASE1_CLOSURE_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
