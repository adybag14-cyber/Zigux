#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase8-exec-cmd-slice.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/Makefile",
    "zigux/tests/phase8_build.zig",
    "zigux/tests/phase8_exec_cmd.zig",
    "zigux/tests/phase8_exec_cmd_only_build.zig",
]

REQUIRED_MARKERS = {
    "Documentation/zigux/phase8-exec-cmd-slice.md": [
        "PHASE8_SLICE=exec-cmd-deferred-exec-packet",
        "shared Phase 8 validator-first route",
        "`kernel/workqueue.c` in the later Phase 14 boundary-study tranche",
        "stops before any ownership of `execv_cmd()` or `execvp()`",
        "make -C zigux phase8-validate",
    ],
    "Documentation/zigux/review-checklist.md": [
        "if the change touches the parked Phase 8 `exec-cmd` packet",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8-validate`",
        "helper-first, output-stable deferred-exec planning packet",
        "without widening into direct process-launch parity",
        "`kernel/workqueue.c`",
    ],
    "zigux/Makefile": [
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py --self-test",
        "scripts/zigux/validate-phase8.py",
        "scripts/zigux/check-phase8-exec-cmd-packet.py --self-test",
        "scripts/zigux/check-phase8-exec-cmd-packet.py",
        "phase8-exec-cmd-test:",
        "$(ZIG) build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all",
    ],
    "zigux/tests/phase8_build.zig": [
        "../../tools/lib/subcmd/exec-cmd.zig",
        "\"phase8_exec_cmd.zig\"",
        "phase8-exec-cmd-tests",
    ],
    "zigux/tests/phase8_exec_cmd.zig": [
        "PHASE8_SLICE=exec-cmd-deferred-exec-packet",
        "shared Phase 8 validator-first route",
        "`kernel/workqueue.c` in the later Phase 14 boundary-study tranche",
        "phase 8 exec-cmd checklist hook keeps the parked deferred-exec packet explicit",
        "make -C zigux phase8-validate",
    ],
    "zigux/tests/phase8_exec_cmd_only_build.zig": [
        "../../tools/lib/subcmd/exec-cmd.zig",
        "\"phase8_exec_cmd.zig\"",
        "phase8-exec-cmd-tests",
    ],
}


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def collect_missing_markers(root: Path) -> list[str]:
    missing: list[str] = []
    for rel, markers in REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel}: {marker}")
    return missing


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    return [], collect_missing_markers(root)


def write_fixture_root(tmp_root: Path) -> None:
    for rel, markers in REQUIRED_MARKERS.items():
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(markers) + "\n", encoding="utf-8")


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_missing_marker(case: str, tmp_root: Path, marker: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [marker], case


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    missing_file_cases = [
        ("missing_slice", "Documentation/zigux/phase8-exec-cmd-slice.md"),
        ("missing_checklist", "Documentation/zigux/review-checklist.md"),
        ("missing_makefile", "zigux/Makefile"),
        ("missing_phase8_build", "zigux/tests/phase8_build.zig"),
        ("missing_exec_cmd_test", "zigux/tests/phase8_exec_cmd.zig"),
        ("missing_exec_cmd_only_build", "zigux/tests/phase8_exec_cmd_only_build.zig"),
    ]

    marker_cases = [
        (
            "slice_marker",
            "Documentation/zigux/phase8-exec-cmd-slice.md",
            "PHASE8_SLICE=exec-cmd-deferred-exec-packet",
            "PHASE8_SLICE=exec-cmd-drift",
            "Documentation/zigux/phase8-exec-cmd-slice.md: PHASE8_SLICE=exec-cmd-deferred-exec-packet",
        ),
        (
            "makefile_route",
            "zigux/Makefile",
            "scripts/zigux/check-phase8-exec-cmd-packet.py --self-test",
            "scripts/zigux/check-phase8-exec-cmd-gate.py --self-test",
            "zigux/Makefile: scripts/zigux/check-phase8-exec-cmd-packet.py --self-test",
        ),
        (
            "makefile_target",
            "zigux/Makefile",
            "phase8-exec-cmd-test:",
            "phase8-exec-test:",
            "zigux/Makefile: phase8-exec-cmd-test:",
        ),
        (
            "makefile_command",
            "zigux/Makefile",
            "$(ZIG) build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all",
            "$(ZIG) build test --build-file zigux/tests/phase8_exec_cmd_build.zig --summary all",
            "zigux/Makefile: $(ZIG) build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all",
        ),
        (
            "checklist_boundary",
            "Documentation/zigux/review-checklist.md",
            "`kernel/workqueue.c`",
            "`kernel/sched/core.c`",
            "Documentation/zigux/review-checklist.md: `kernel/workqueue.c`",
        ),
        (
            "shared_build_source",
            "zigux/tests/phase8_build.zig",
            "\"phase8_exec_cmd.zig\"",
            "\"phase8_exec_cmd_drift.zig\"",
            "zigux/tests/phase8_build.zig: \"phase8_exec_cmd.zig\"",
        ),
        (
            "shared_build_test_name",
            "zigux/tests/phase8_build.zig",
            "phase8-exec-cmd-tests",
            "phase8-exec-tests",
            "zigux/tests/phase8_build.zig: phase8-exec-cmd-tests",
        ),
        (
            "focused_test_guard",
            "zigux/tests/phase8_exec_cmd.zig",
            "shared Phase 8 validator-first route",
            "shared Phase 8 tooling route",
            "zigux/tests/phase8_exec_cmd.zig: shared Phase 8 validator-first route",
        ),
        (
            "focused_build_root",
            "zigux/tests/phase8_exec_cmd_only_build.zig",
            "\"phase8_exec_cmd.zig\"",
            "\"phase8_exec_cmd_drift.zig\"",
            "zigux/tests/phase8_exec_cmd_only_build.zig: \"phase8_exec_cmd.zig\"",
        ),
        (
            "focused_build_name",
            "zigux/tests/phase8_exec_cmd_only_build.zig",
            "phase8-exec-cmd-tests",
            "phase8-exec-tests",
            "zigux/tests/phase8_exec_cmd_only_build.zig: phase8-exec-cmd-tests",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase8_exec_cmd_packet_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_root(tmp_root)
        assert validate(tmp_root) == ([], [])

        for case, rel in missing_file_cases:
            (tmp_root / rel).unlink()
            expect_missing_file(case, tmp_root, rel)
            write_fixture_root(tmp_root)

        for case, rel, old, new, expected in marker_cases:
            mutate_file(tmp_root, rel, old, new, case)
            expect_missing_marker(case, tmp_root, expected)
            write_fixture_root(tmp_root)

    print("PHASE8_EXEC_CMD_PACKET_SELF_TEST=pass")
    print(
        "PHASE8_EXEC_CMD_PACKET_SELF_TEST_CASE_COUNT="
        f"{len(missing_file_cases) + len(marker_cases)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the parked Phase 8 exec-cmd deferred-exec packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-test cases without reading repo files.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE8_EXEC_CMD_PACKET=fail")
        print("MISSING_PHASE8_EXEC_CMD_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE8_EXEC_CMD_PACKET_FILES_END")
        return 1

    if missing_markers:
        print("PHASE8_EXEC_CMD_PACKET=fail")
        print("MISSING_PHASE8_EXEC_CMD_PACKET_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE8_EXEC_CMD_PACKET_MARKERS_END")
        return 1

    print("PHASE8_EXEC_CMD_PACKET=pass")
    print(f"PHASE8_EXEC_CMD_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_EXEC_CMD_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
