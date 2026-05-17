#!/usr/bin/env python3
"""Fail-closed checker for the Phase 14 skbuff compile-evidence packet."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


EXPECTED_NOTE_MARKERS = (
    "PHASE14_LANE_KEY=P14-L11",
    "PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker",
    "current `master` still ships the bounded skbuff anchor packet files `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_build.zig`, and `net/core/skbuff_bridge.zig`",
    "`full_bundle_only`",
    "`phase14-skbuff-bridge-tests`",
    "`zig build test --build-file zigux/tests/phase14_build.zig --summary all`",
    "`make -C zigux phase14-test`",
    "keeps the skbuff shard out of `phase14-smoke`",
)

FORBIDDEN_NOTE_MARKERS = (
    "PHASE14_BLOCKED_GAP=phase14-skbuff-anchor-packet-missing",
    "no longer exposes the earlier `P14-L11` skbuff anchor packet files",
    "must not be treated as live compile evidence on current `master`",
    "anchor packet is absent",
)

EXPECTED_BUILD_MARKERS = (
    '.root_source_file = b.path("../../net/core/skbuff_bridge.zig")',
    'phase14_skbuff_bridge_module.addImport("skbuff_bridge", skbuff_bridge_module);',
    '.name = "phase14-skbuff-bridge-tests"',
    "test_step.dependOn(&run_phase14_skbuff_bridge_tests.step);",
)

FORBIDDEN_BUILD_MARKERS = (
    "smoke_step.dependOn(&run_phase14_skbuff_bridge_tests.step);",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_errors(root: Path) -> list[str]:
    note_path = root / "Documentation/zigux/phase14-skbuff-bridge-survey.md"
    build_path = root / "zigux/tests/phase14_build.zig"

    errors: list[str] = []
    note = _read(note_path)
    build = _read(build_path)

    for marker in EXPECTED_NOTE_MARKERS:
        if marker not in note:
            errors.append(f"missing note marker: {marker}")

    for marker in FORBIDDEN_NOTE_MARKERS:
        if marker in note:
            errors.append(f"forbidden note marker present: {marker}")

    for marker in EXPECTED_BUILD_MARKERS:
        if marker not in build:
            errors.append(f"missing build marker: {marker}")

    for marker in FORBIDDEN_BUILD_MARKERS:
        if marker in build:
            errors.append(f"forbidden build marker present: {marker}")

    return errors


def run_check(root: Path) -> int:
    errors = collect_errors(root)
    if errors:
        print("PHASE14_SKBUFF_COMPILE_EVIDENCE=fail")
        for error in errors:
            print(f"PHASE14_SKBUFF_COMPILE_EVIDENCE_ERROR={error}")
        return 1

    print("PHASE14_SKBUFF_COMPILE_EVIDENCE=pass")
    print(
        f"PHASE14_SKBUFF_COMPILE_EVIDENCE_NOTE_MARKER_COUNT={len(EXPECTED_NOTE_MARKERS)}"
    )
    print(
        f"PHASE14_SKBUFF_COMPILE_EVIDENCE_BUILD_MARKER_COUNT={len(EXPECTED_BUILD_MARKERS)}"
    )
    print(
        "PHASE14_SKBUFF_COMPILE_EVIDENCE_FORBIDDEN_MARKER_COUNT="
        f"{len(FORBIDDEN_NOTE_MARKERS) + len(FORBIDDEN_BUILD_MARKERS)}"
    )
    return 0


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    good_note = """# Phase 14 Skbuff Bridge Survey
## Status
- `PHASE14_LANE_KEY=P14-L11`
- `PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker`
- current `master` still ships the bounded skbuff anchor packet files `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_build.zig`, and `net/core/skbuff_bridge.zig`

## Compile Evidence
- the skbuff anchor remains `full_bundle_only` through `phase14-skbuff-bridge-tests`, `zig build test --build-file zigux/tests/phase14_build.zig --summary all`, and `make -C zigux phase14-test`
- current `zigux/tests/phase14_build.zig` wires `../../net/core/skbuff_bridge.zig` into `phase14_skbuff_bridge.zig`, keeps the skbuff shard out of `phase14-smoke`, and registers the bounded `phase14-skbuff-bridge-tests` route only inside the shared Phase 14 full bundle
"""
    bad_note = good_note.replace(
        "phase14-skbuff-live-ownership-blocker",
        "phase14-skbuff-anchor-packet-missing",
    ).replace("current `master` still ships", "current `master` no longer exposes")

    good_build = """const phase14_skbuff_bridge_module = b.createModule(.{
    .root_source_file = b.path("phase14_skbuff_bridge.zig"),
});
phase14_skbuff_bridge_module.addImport("skbuff_bridge", skbuff_bridge_module);
const skbuff_bridge_module = b.createModule(.{
    .root_source_file = b.path("../../net/core/skbuff_bridge.zig"),
});
const phase14_skbuff_bridge_tests = b.addTest(.{
    .name = "phase14-skbuff-bridge-tests",
    .root_module = phase14_skbuff_bridge_module,
});
const smoke_step = b.step("phase14-smoke", "Run the focused Phase 14 smoke shard");
const test_step = b.step("test", "Run the full bundle");
test_step.dependOn(&run_phase14_skbuff_bridge_tests.step);
"""
    bad_build = good_build + "smoke_step.dependOn(&run_phase14_skbuff_bridge_tests.step);\n"

    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        note_path = root / "Documentation/zigux/phase14-skbuff-bridge-survey.md"
        build_path = root / "zigux/tests/phase14_build.zig"

        _write(note_path, good_note)
        _write(build_path, good_build)
        if collect_errors(root):
            print("PHASE14_SKBUFF_COMPILE_EVIDENCE_SELF_TEST=fail")
            print("PHASE14_SKBUFF_COMPILE_EVIDENCE_SELF_TEST_CASE=good_fixture")
            return 1

        _write(note_path, bad_note)
        errors = collect_errors(root)
        if not any("forbidden note marker present" in error for error in errors):
            print("PHASE14_SKBUFF_COMPILE_EVIDENCE_SELF_TEST=fail")
            print("PHASE14_SKBUFF_COMPILE_EVIDENCE_SELF_TEST_CASE=forbidden_note")
            return 1

        _write(note_path, good_note)
        _write(build_path, bad_build)
        errors = collect_errors(root)
        if not any("forbidden build marker present" in error for error in errors):
            print("PHASE14_SKBUFF_COMPILE_EVIDENCE_SELF_TEST=fail")
            print("PHASE14_SKBUFF_COMPILE_EVIDENCE_SELF_TEST_CASE=forbidden_build")
            return 1

    print("PHASE14_SKBUFF_COMPILE_EVIDENCE_SELF_TEST=pass")
    print("PHASE14_SKBUFF_COMPILE_EVIDENCE_SELF_TEST_CASE_COUNT=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    return run_check(args.root)


if __name__ == "__main__":
    sys.exit(main())
