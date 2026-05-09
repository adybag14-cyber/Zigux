#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase8-exec-cmd-slice.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/phase8_build.zig",
    "zigux/tests/phase8_exec_cmd.zig",
    "zigux/tests/phase8_exec_cmd_only_build.zig",
    "tools/lib/subcmd/exec-cmd.zig",
    "tools/lib/subcmd/exec-cmd.c",
]

EXACT_ONCE_SECTION_MARKERS = {
    "zigux/tests/README.md": [
        {
            "start": "  * `zigux/tests/phase8_build.zig`\n",
            "end": "  * `zigux/tests/phase9_build.zig`\n",
            "needle": "  * `zigux/tests/phase8_exec_cmd_only_build.zig`\n",
        },
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        {
            "start": "      - name: Validate Phase 8 tooling packet\n",
            "end": "      - name: Run focused Phase 8 help tests\n",
            "needle": "      - name: Run focused Phase 8 exec-cmd tests\n",
        },
    ],
}

REQUIRED_MARKERS = {
    "Documentation/zigux/phase8-exec-cmd-slice.md": [
        "PHASE8_SLICE=exec-cmd-deferred-exec-packet",
        "prove Zigux inside serious repo-hosted tooling, not just tiny helpers",
        "output-stable tooling behavior",
        "shared Phase 8 validator-first route",
        "`kernel/workqueue.c` in the later Phase 14 boundary-study tranche",
        "stops before any ownership of `execv_cmd()` or `execvp()`",
        "stops before any ownership of `execl_cmd()`",
        "direct varargs launch path",
        "integrated `planDeferredExecvCall()` plus `planDeferredExeclCall()` planner packet",
        "zig test tools/lib/subcmd/exec-cmd.zig",
        "make -C zigux phase8-validate",
        "zig build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all",
        "make -C zigux phase8-exec-cmd-test",
        "zig build test --build-file zigux/tests/phase8_build.zig --summary all",
    ],
    "Documentation/zigux/README.md": [
        "Documentation/zigux/phase8-exec-cmd-slice.md",
        "zigux/tests/phase8_exec_cmd.zig",
        "zigux/tests/phase8_exec_cmd_only_build.zig",
        "make -C zigux phase8-exec-cmd-test",
        "make -C zigux phase8-validate",
    ],
    "Documentation/zigux/review-checklist.md": [
        "if the change touches the parked Phase 8 `exec-cmd` packet",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8-validate`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "helper-first, output-stable deferred-exec planning packet",
        "without widening into direct process-launch parity",
        "separate `kernel/workqueue.c` Phase 14 boundary-study target",
    ],
    "scripts/zigux/README.md": [
        "Phase 8 flow",
        "scripts/zigux/check-phase8-exec-cmd-packet.py",
        "Documentation/zigux/phase8-exec-cmd-slice.md",
        "zigux/tests/phase8_exec_cmd.zig",
        "zigux/tests/phase8_exec_cmd_only_build.zig",
        "make -C zigux phase8-validate",
        "make -C zigux phase8-exec-cmd-test",
    ],
    "zigux/tests/README.md": [
        "Phase 8 flow",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8`",
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
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 8 tooling packet",
        "make -C zigux phase8-validate",
        "Run focused Phase 8 exec-cmd tests",
        "make -C zigux phase8-exec-cmd-test",
        "Run focused Phase 8 help tests",
        "Run Phase 8 tooling tests",
    ],
    "zigux/tests/phase8_build.zig": [
        "../../tools/lib/subcmd/exec-cmd.zig",
        "\"phase8_exec_cmd.zig\"",
        "phase8-exec-cmd-tests",
    ],
    "zigux/tests/phase8_exec_cmd.zig": [
        "PHASE8_SLICE=exec-cmd-deferred-exec-packet",
        "prove Zigux inside serious repo-hosted tooling, not just tiny helpers",
        "shared Phase 8 validator-first route",
        "`kernel/workqueue.c` in the later Phase 14 boundary-study tranche",
        "focused Phase 8 replay keeps the integrated deferred-exec packet reviewable",
        "phase 8 exec-cmd checklist hook keeps the parked deferred-exec packet explicit",
        "make -C zigux phase8-validate",
        "phase 8 exec-cmd deferred boundary note still matches the live C helper anchors",
        "`execl_cmd()`",
    ],
    "zigux/tests/phase8_exec_cmd_only_build.zig": [
        "../../tools/lib/subcmd/exec-cmd.zig",
        "\"phase8_exec_cmd.zig\"",
        "phase8-exec-cmd-tests",
    ],
    "tools/lib/subcmd/exec-cmd.zig": [
        "pub fn buildDeferredExecvCall",
        "pub fn buildDeferredExeclCall",
        "pub fn planDeferredExecvCall",
        "pub fn planDeferredExecvCallWithPwd",
        "pub fn planDeferredExeclCall",
        "pub fn planDeferredExeclCallWithPwd",
        "pub fn collectExeclArgs",
        "pub fn choosePwdCwdFromFilesystem",
        "pub const max_execl_slots",
    ],
    "tools/lib/subcmd/exec-cmd.c": [
        "static const char *get_pwd_cwd",
        "void setup_path(void)",
        "int execv_cmd",
        "int execl_cmd",
        "execvp(",
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


def collect_exact_section_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for rel, section_specs in EXACT_ONCE_SECTION_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for spec in section_specs:
            start = text.find(spec["start"])
            if start == -1:
                errors.append(f"{rel}: missing_section_start:{spec['start'].strip()}")
                continue
            section_start = start + len(spec["start"])
            end = text.find(spec["end"], section_start)
            if end == -1:
                errors.append(f"{rel}: missing_section_end:{spec['end'].strip()}")
                continue
            section = text[section_start:end]
            if section.count(spec["needle"]) != 1:
                errors.append(
                    f"{rel}: exact_once_section_marker:{spec['needle'].rstrip()}"
                )
    return errors


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    missing_markers = collect_missing_markers(root)
    missing_markers.extend(collect_exact_section_errors(root))
    return [], missing_markers


def build_tests_readme_fixture() -> str:
    return "\n".join(
        [
            "Phase 8 flow",
            "  * `zigux/tests/phase8_build.zig`",
            "  * `zigux/tests/phase8_exec_cmd.zig`",
            "  * `zigux/tests/phase8_exec_cmd_only_build.zig`",
            "  * `make -C zigux phase8-exec-cmd-test`",
            "  * `make -C zigux phase8`",
            "  * `zigux/tests/phase9_build.zig`",
        ]
    ) + "\n"


def build_workflow_fixture() -> str:
    return "\n".join(
        [
            "Validate Phase 8 tooling packet",
            "      - name: Validate Phase 8 tooling packet",
            "        run: make -C zigux phase8-validate",
            "Run focused Phase 8 exec-cmd tests",
            "      - name: Run focused Phase 8 exec-cmd tests",
            "        run: make -C zigux phase8-exec-cmd-test",
            "Run focused Phase 8 help tests",
            "      - name: Run focused Phase 8 help tests",
            "        run: make -C zigux phase8-help-test",
            "Run focused Phase 8 kallsyms tests",
            "      - name: Run focused Phase 8 kallsyms tests",
            "        run: make -C zigux phase8-kallsyms-test",
            "Run focused Phase 8 cpu-mask tests",
            "      - name: Run focused Phase 8 cpu-mask tests",
            "        run: make -C zigux phase8-cpu-mask-test",
            "Run focused Phase 8 help and kallsyms tests",
            "      - name: Run focused Phase 8 help and kallsyms tests",
            "Run Phase 8 tooling tests",
        ]
    ) + "\n"


FIXTURE_OVERRIDES = {
    "zigux/tests/README.md": build_tests_readme_fixture(),
    ".github/workflows/zigux-bootstrap.yml": build_workflow_fixture(),
}


def write_fixture_root(tmp_root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = tmp_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        override = FIXTURE_OVERRIDES.get(rel)
        if override is not None:
            path.write_text(override, encoding="utf-8")
            continue
        path.write_text("\n".join(REQUIRED_MARKERS[rel]) + "\n", encoding="utf-8")


def assert_valid(case: str, tmp_root: Path) -> None:
    assert validate(tmp_root) == ([], []), case


def expect_missing_file(case: str, tmp_root: Path, rel: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_markers == [], case
    assert missing_files == [rel], case


def expect_marker_error(case: str, tmp_root: Path, expected: str) -> None:
    missing_files, missing_markers = validate(tmp_root)
    assert missing_files == [], case
    assert missing_markers == [expected], case


def mutate_file(tmp_root: Path, rel: str, old: str, new: str, case: str) -> None:
    path = tmp_root / rel
    original = path.read_text(encoding="utf-8")
    updated = original.replace(old, new, 1)
    assert updated != original, case
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_exec_cmd_packet_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_root(tmp_root)
        assert_valid("baseline", tmp_root)

        (tmp_root / "zigux/tests/phase8_exec_cmd_only_build.zig").unlink()
        expect_missing_file(
            "missing_exec_cmd_only_build",
            tmp_root,
            "zigux/tests/phase8_exec_cmd_only_build.zig",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            "Documentation/zigux/README.md",
            "make -C zigux phase8-exec-cmd-test",
            "make -C zigux phase8-exec-test",
            "docs_root_make_route",
        )
        expect_marker_error(
            "docs_root_make_route",
            tmp_root,
            "Documentation/zigux/README.md: make -C zigux phase8-exec-cmd-test",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml",
            "      - name: Run focused Phase 8 exec-cmd tests\n        run: make -C zigux phase8-exec-cmd-test\nRun focused Phase 8 help tests\n      - name: Run focused Phase 8 help tests\n",
            "Run focused Phase 8 help tests\n      - name: Run focused Phase 8 help tests\n      - name: Run focused Phase 8 exec-cmd tests\n        run: make -C zigux phase8-exec-cmd-test\n",
            "workflow_exec_cmd_moved_after_help",
        )
        expect_marker_error(
            "workflow_exec_cmd_moved_after_help",
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml: exact_once_section_marker:      - name: Run focused Phase 8 exec-cmd tests",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml",
            "      - name: Run focused Phase 8 exec-cmd tests\n",
            "      - name: Run focused Phase 8 exec-cmd tests\n      - name: Run focused Phase 8 exec-cmd tests\n",
            "workflow_exec_cmd_duplicate",
        )
        expect_marker_error(
            "workflow_exec_cmd_duplicate",
            tmp_root,
            ".github/workflows/zigux-bootstrap.yml: exact_once_section_marker:      - name: Run focused Phase 8 exec-cmd tests",
        )
        write_fixture_root(tmp_root)

        mutate_file(
            tmp_root,
            "tools/lib/subcmd/exec-cmd.zig",
            "pub fn planDeferredExeclCallWithPwd",
            "pub fn planDeferredExecLineCallWithPwd",
            "helper_export",
        )
        expect_marker_error(
            "helper_export",
            tmp_root,
            "tools/lib/subcmd/exec-cmd.zig: pub fn planDeferredExeclCallWithPwd",
        )

    print("PHASE8_EXEC_CMD_PACKET_SELF_TEST=pass")
    print("PHASE8_EXEC_CMD_PACKET_SELF_TEST_CASE_COUNT=6")


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
