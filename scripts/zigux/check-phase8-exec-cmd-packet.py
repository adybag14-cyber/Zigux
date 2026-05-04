#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "Documentation/zigux/phase8-exec-cmd-slice.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/phase8_exec_cmd.zig",
]

REQUIRED_SLICE_MARKERS = [
    "PHASE8_STATUS=parked",
    "PHASE8_SLICE=exec-cmd-tooling-parked",
    "legacy validator alias: `PHASE8_SLICE=exec-cmd-tooling-starter`",
    "make -C zigux phase8-exec-cmd-test",
    "`kernel/workqueue.c` remains a Phase 14 boundary-study target",
    "`planDeferredExeclCallWithPwd()`",
]

REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    "parked Phase 8 `exec-cmd` helper packet",
    "Documentation/zigux/phase8-exec-cmd-slice.md",
    "zigux/tests/phase8_exec_cmd.zig",
    "zigux/tests/phase8_exec_cmd_only_build.zig",
    "deferred execution helper-only",
    "separate `kernel/workqueue.c` Phase 14 boundary-study target",
    "direct `execvp()` side effects",
    "queue ownership",
    "scheduler-facing transport claims",
]

REQUIRED_TEST_MARKERS = [
    'test "phase 8 exec-cmd docs keep the deferred execution boundary explicit"',
    'test "phase 8 exec-cmd docs keep the validator alias and Phase 14 wording reviewable"',
    'test "phase 8 exec-cmd review checklist keeps deferred handoff review wording aligned"',
    'test "phase 8 exec-cmd build wiring keeps focused and shared gates explicit"',
    'test "phase 8 exec-cmd evidence still matches the live C helper anchors"',
    'try expectContains(slice_note, "PHASE8_SLICE=exec-cmd-tooling-parked");',
    'try expectContains(slice_note, "legacy validator alias: `PHASE8_SLICE=exec-cmd-tooling-starter`");',
    'try expectContains(review_checklist, "separate `kernel/workqueue.c` Phase 14 boundary-study target");',
]

FIXTURE_SLICE = """# Phase 8 Exec-Cmd Slice

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=exec-cmd-tooling-parked`
- legacy validator alias: `PHASE8_SLICE=exec-cmd-tooling-starter`
- `kernel/workqueue.c` remains a Phase 14 boundary-study target
- `planDeferredExeclCallWithPwd()`
- `make -C zigux phase8-exec-cmd-test`
"""

FIXTURE_REVIEW_CHECKLIST = """# Zigux Review Checklist

- parked Phase 8 `exec-cmd` helper packet
- Documentation/zigux/phase8-exec-cmd-slice.md
- zigux/tests/phase8_exec_cmd.zig
- zigux/tests/phase8_exec_cmd_only_build.zig
- deferred execution helper-only
- separate `kernel/workqueue.c` Phase 14 boundary-study target
- direct `execvp()` side effects
- queue ownership
- scheduler-facing transport claims
"""

FIXTURE_TEST = """const std = @import("std");

test "phase 8 exec-cmd docs keep the deferred execution boundary explicit" {}
test "phase 8 exec-cmd docs keep the validator alias and Phase 14 wording reviewable" {}
test "phase 8 exec-cmd review checklist keeps deferred handoff review wording aligned" {}
test "phase 8 exec-cmd build wiring keeps focused and shared gates explicit" {}
test "phase 8 exec-cmd evidence still matches the live C helper anchors" {}

fn markers() void {
    _ = "try expectContains(slice_note, \"PHASE8_SLICE=exec-cmd-tooling-parked\");";
    _ = "try expectContains(slice_note, \"legacy validator alias: `PHASE8_SLICE=exec-cmd-tooling-starter`\");";
    _ = "try expectContains(review_checklist, \"separate `kernel/workqueue.c` Phase 14 boundary-study target\");";
}
"""


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]
    if missing_files:
        return missing_files, []

    slice_note = read_text(root, "Documentation/zigux/phase8-exec-cmd-slice.md")
    review_checklist = read_text(root, "Documentation/zigux/review-checklist.md")
    exec_cmd_test = read_text(root, "zigux/tests/phase8_exec_cmd.zig")

    missing_markers: list[str] = []
    for marker in REQUIRED_SLICE_MARKERS:
        if marker not in slice_note:
            missing_markers.append(f"slice:{marker}")
    for marker in REQUIRED_REVIEW_CHECKLIST_MARKERS:
        if marker not in review_checklist:
            missing_markers.append(f"review_checklist:{marker}")
    for marker in REQUIRED_TEST_MARKERS:
        if marker not in exec_cmd_test:
            missing_markers.append(f"exec_cmd_test:{marker}")

    return [], missing_markers


def write_fixture(root: Path) -> None:
    for rel_path, content in {
        "Documentation/zigux/phase8-exec-cmd-slice.md": FIXTURE_SLICE,
        "Documentation/zigux/review-checklist.md": FIXTURE_REVIEW_CHECKLIST,
        "zigux/tests/phase8_exec_cmd.zig": FIXTURE_TEST,
    }.items():
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"{label}:unexpected_missing_files:{','.join(missing_files)}")
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(f"{label}:expected_missing_marker:{expected_marker}:actual:{actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase8_exec_cmd_packet_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture(tmp_root)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        slice_path = tmp_root / "Documentation/zigux/phase8-exec-cmd-slice.md"
        original_slice = slice_path.read_text(encoding="utf-8")
        slice_path.write_text(
            original_slice.replace(
                "PHASE8_SLICE=exec-cmd-tooling-parked",
                "PHASE8_SLICE=exec-cmd-tooling-active",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "parked_slice_marker",
            tmp_root,
            "slice:PHASE8_SLICE=exec-cmd-tooling-parked",
        )
        slice_path.write_text(original_slice, encoding="utf-8")

        slice_path.write_text(
            original_slice.replace(
                "legacy validator alias: `PHASE8_SLICE=exec-cmd-tooling-starter`",
                "legacy validator alias: `PHASE8_SLICE=exec-cmd-tooling-legacy`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "legacy_alias_marker",
            tmp_root,
            "slice:legacy validator alias: `PHASE8_SLICE=exec-cmd-tooling-starter`",
        )
        slice_path.write_text(original_slice, encoding="utf-8")

        review_path = tmp_root / "Documentation/zigux/review-checklist.md"
        original_review = review_path.read_text(encoding="utf-8")
        review_path.write_text(
            original_review.replace(
                "separate `kernel/workqueue.c` Phase 14 boundary-study target",
                "separate `kernel/workqueue.c` freeze boundary",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "review_phase14_marker",
            tmp_root,
            "review_checklist:separate `kernel/workqueue.c` Phase 14 boundary-study target",
        )
        review_path.write_text(original_review, encoding="utf-8")

        test_path = tmp_root / "zigux/tests/phase8_exec_cmd.zig"
        original_test = test_path.read_text(encoding="utf-8")
        test_path.write_text(
            original_test.replace(
                'test "phase 8 exec-cmd docs keep the validator alias and Phase 14 wording reviewable"',
                'test "phase 8 exec-cmd docs keep the validator alias reviewable"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "test_alias_guard",
            tmp_root,
            'exec_cmd_test:test "phase 8 exec-cmd docs keep the validator alias and Phase 14 wording reviewable"',
        )

    print("PHASE8_EXEC_CMD_PACKET_CHECK=pass")
    print("PHASE8_EXEC_CMD_PACKET_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the parked Phase 8 exec-cmd note, review checklist, and focused regression packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="Repository root to validate.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker self-tests against a temporary fixture tree.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(args.repo_root)
    if missing_files:
        print("PHASE8_EXEC_CMD_PACKET_CHECK=fail")
        print("MISSING_PHASE8_EXEC_CMD_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE8_EXEC_CMD_PACKET_FILES_END")
        return 1
    if missing_markers:
        print("PHASE8_EXEC_CMD_PACKET_CHECK=fail")
        print("MISSING_PHASE8_EXEC_CMD_PACKET_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE8_EXEC_CMD_PACKET_MARKERS_END")
        return 1

    print("PHASE8_EXEC_CMD_PACKET_CHECK=pass")
    print(f"PHASE8_EXEC_CMD_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_EXEC_CMD_PACKET_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_SLICE_MARKERS) + len(REQUIRED_REVIEW_CHECKLIST_MARKERS) + len(REQUIRED_TEST_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
