#!/usr/bin/env python3
"""Fail-closed checker for the parked Phase 8 exec-cmd review packet."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


REQUIRED_FILES = (
    "Documentation/zigux/phase8-exec-cmd-slice.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase8_exec_cmd.zig",
    "zigux/tests/phase8_exec_cmd_only_build.zig",
    "zigux/tests/phase8_build.zig",
    "tools/lib/subcmd/exec-cmd.zig",
    "tools/lib/subcmd/exec-cmd.c",
)

SLICE_MARKERS = (
    "PHASE8_SLICE=exec-cmd-tooling-parked",
    "legacy validator alias: `PHASE8_SLICE=exec-cmd-tooling-starter`",
    "`zigux/tests/phase8_exec_cmd_only_build.zig`",
    "`buildDeferredExecvCall()`",
    "`planDeferredExecvCallWithPwd()`",
    "`buildDeferredExeclCall()`",
    "`planDeferredExeclCallWithPwd()`",
    "`make -C zigux phase8-exec-cmd-test`",
    "`kernel/workqueue.c`",
)

CHECKLIST_MARKERS = (
    "if the change touches the parked Phase 8 `exec-cmd` packet",
    "`zigux/tests/phase8_exec_cmd_only_build.zig`",
    "`make -C zigux phase8-exec-cmd-test`",
    "`make -C zigux phase8-validate`",
    "helper-first, output-stable deferred-exec planning packet",
    "without widening into direct process-launch parity",
    "separate `kernel/workqueue.c` Phase 14 boundary-study target",
)

SCRIPTS_README_MARKERS = (
    "`check-phase8-exec-cmd-packet.py`",
    "`Documentation/zigux/phase8-exec-cmd-slice.md`",
    "`zigux/tests/phase8_exec_cmd.zig`",
    "`zigux/tests/phase8_exec_cmd_only_build.zig`",
    "`scripts/zigux/check-phase8-exec-cmd-packet.py`",
    "`make -C zigux phase8-validate`",
    "`make -C zigux phase8-exec-cmd-test`",
)

TESTS_README_MARKERS = (
    "Phase 8 flow",
    "`zigux/tests/phase8_exec_cmd.zig`",
    "`zigux/tests/phase8_exec_cmd_only_build.zig`",
    "`make -C zigux phase8-exec-cmd-test`",
    "`make -C zigux phase8-validate`",
)

MAKEFILE_MARKERS = (
    "scripts/zigux/check-phase8-exec-cmd-packet.py --self-test",
    "scripts/zigux/check-phase8-exec-cmd-packet.py",
    "phase8-exec-cmd-test:",
    "zigux/tests/phase8_exec_cmd_only_build.zig --summary all",
)

TEST_MARKERS = (
    'test "phase 8 exec-cmd slice note keeps the helper-vs-phase ownership boundary explicit" {',
    'test "phase 8 exec-cmd deferred boundary note still matches the live C helper anchors" {',
    'test "phase 8 exec-cmd checklist hook keeps the parked deferred-exec packet explicit" {',
    'test "phase 8 exec-cmd workflow keeps the focused replay ahead of sibling help shards" {',
    'test "phase 8 exec-cmd docs root summary keeps the focused replay route explicit" {',
    'test "phase 8 exec-cmd scripts root summary keeps the focused replay route explicit" {',
    'test "phase 8 exec-cmd tests root summary keeps the focused replay route explicit" {',
)

HELPER_MARKERS = (
    "pub const max_execl_slots: usize = 32;",
    "pub fn buildDeferredExecvCall(",
    "pub fn planDeferredExecvCall(",
    "pub fn planDeferredExecvCallWithPwd(",
    "pub fn buildDeferredExeclCall(",
    "pub fn planDeferredExeclCall(",
    "pub fn planDeferredExeclCallWithPwd(",
    'test "planDeferredExecvCallWithPwd reuses caller-proved logical PWD aliases" {',
    'test "planDeferredExeclCallWithPwd reuses caller-proved logical PWD aliases" {',
)

SELF_TEST_CASE_COUNT = 6


def read_text(root: Path, rel_path: str) -> str:
    path = root / rel_path
    if not path.is_file():
        raise SystemExit(f"missing required file: {rel_path}")
    return path.read_text(encoding="utf-8")


def require_markers(root: Path, rel_path: str, markers: tuple[str, ...]) -> None:
    text = read_text(root, rel_path)
    missing = [marker for marker in markers if marker not in text]
    if missing:
        joined = "\n".join(f"  - {marker}" for marker in missing)
        raise SystemExit(f"{rel_path} is missing expected Phase 8 exec-cmd markers:\n{joined}")


def validate(root: Path) -> None:
    missing = [rel for rel in REQUIRED_FILES if not (root / rel).is_file()]
    if missing:
        joined = "\n".join(f"  - {rel}" for rel in missing)
        raise SystemExit(f"missing required Phase 8 exec-cmd packet files:\n{joined}")

    require_markers(root, "Documentation/zigux/phase8-exec-cmd-slice.md", SLICE_MARKERS)
    require_markers(root, "Documentation/zigux/review-checklist.md", CHECKLIST_MARKERS)
    require_markers(root, "scripts/zigux/README.md", SCRIPTS_README_MARKERS)
    require_markers(root, "zigux/tests/README.md", TESTS_README_MARKERS)
    require_markers(root, "zigux/Makefile", MAKEFILE_MARKERS)
    require_markers(root, "zigux/tests/phase8_exec_cmd.zig", TEST_MARKERS)
    require_markers(root, "tools/lib/subcmd/exec-cmd.zig", HELPER_MARKERS)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_fixture(root: Path) -> None:
    for rel in REQUIRED_FILES:
        write(root / rel, "placeholder\n")

    write(root / "Documentation/zigux/phase8-exec-cmd-slice.md", "\n".join(SLICE_MARKERS) + "\n")
    write(root / "Documentation/zigux/review-checklist.md", "\n".join(CHECKLIST_MARKERS) + "\n")
    write(root / "scripts/zigux/README.md", "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write(root / "zigux/tests/README.md", "\n".join(TESTS_README_MARKERS) + "\n")
    write(root / "zigux/Makefile", "\n".join(MAKEFILE_MARKERS) + "\n")
    write(root / "zigux/tests/phase8_exec_cmd.zig", "\n".join(TEST_MARKERS) + "\n")
    write(root / "tools/lib/subcmd/exec-cmd.zig", "\n".join(HELPER_MARKERS) + "\n")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        validate(root)
    except SystemExit as exc:
        text = str(exc)
        if expected_fragment not in text:
            raise AssertionError(
                f"expected self-test failure containing {expected_fragment!r}, got {text!r}"
            ) from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase8_exec_cmd_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture(root)
        validate(root)

        slice_path = root / "Documentation/zigux/phase8-exec-cmd-slice.md"
        slice_path.write_text(
            slice_path.read_text(encoding="utf-8").replace(
                "`planDeferredExeclCallWithPwd()`\n", "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(root, "`planDeferredExeclCallWithPwd()`")
        build_fixture(root)

        checklist_path = root / "Documentation/zigux/review-checklist.md"
        checklist_path.write_text(
            checklist_path.read_text(encoding="utf-8").replace(
                "helper-first, output-stable deferred-exec planning packet\n", "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(root, "helper-first, output-stable deferred-exec planning packet")
        build_fixture(root)

        scripts_readme_path = root / "scripts/zigux/README.md"
        scripts_readme_path.write_text(
            scripts_readme_path.read_text(encoding="utf-8").replace(
                "`scripts/zigux/check-phase8-exec-cmd-packet.py`\n", "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(root, "`scripts/zigux/check-phase8-exec-cmd-packet.py`")
        build_fixture(root)

        makefile_path = root / "zigux/Makefile"
        makefile_path.write_text(
            makefile_path.read_text(encoding="utf-8").replace(
                "scripts/zigux/check-phase8-exec-cmd-packet.py --self-test\n", "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(root, "scripts/zigux/check-phase8-exec-cmd-packet.py --self-test")
        build_fixture(root)

        helper_path = root / "tools/lib/subcmd/exec-cmd.zig"
        helper_path.write_text(
            helper_path.read_text(encoding="utf-8").replace(
                'test "planDeferredExecvCallWithPwd reuses caller-proved logical PWD aliases" {\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            'test "planDeferredExecvCallWithPwd reuses caller-proved logical PWD aliases" {',
        )
        build_fixture(root)

        (root / "zigux" / "tests" / "phase8_exec_cmd.zig").unlink()
        expect_failure(root, "zigux/tests/phase8_exec_cmd.zig")

    print("PHASE8_EXEC_CMD_PACKET_SELF_TEST=pass")
    print(f"PHASE8_EXEC_CMD_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="repository root to validate",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in checker self-test",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    validate(args.root.resolve())
    print("phase8 exec-cmd packet ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
