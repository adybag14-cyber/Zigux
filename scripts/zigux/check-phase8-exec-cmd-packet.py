#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase8-exec-cmd-packet.py"
DOCS_ROOT_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE_PATH = "zigux/Makefile"
BOUNDARY_SURVEY_PATH = "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"
SEQUENCING_PATH = "Documentation/zigux/phase8-tooling-lane-sequencing.md"
EXEC_CMD_SLICE_PATH = "Documentation/zigux/phase8-exec-cmd-slice.md"
EXEC_CMD_SOURCE_PATH = "tools/lib/subcmd/exec-cmd.zig"
EXEC_CMD_C_PATH = "tools/lib/subcmd/exec-cmd.c"
EXEC_CMD_TEST_PATH = "zigux/tests/phase8_exec_cmd.zig"
EXEC_CMD_ONLY_BUILD_PATH = "zigux/tests/phase8_exec_cmd_only_build.zig"
PHASE8_BUILD_PATH = "zigux/tests/phase8_build.zig"

REQUIRED_FILES = (
    SCRIPT_PATH,
    DOCS_ROOT_PATH,
    REVIEW_CHECKLIST_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    WORKFLOW_PATH,
    MAKEFILE_PATH,
    BOUNDARY_SURVEY_PATH,
    SEQUENCING_PATH,
    EXEC_CMD_SLICE_PATH,
    EXEC_CMD_SOURCE_PATH,
    EXEC_CMD_C_PATH,
    EXEC_CMD_TEST_PATH,
    EXEC_CMD_ONLY_BUILD_PATH,
    PHASE8_BUILD_PATH,
)

REQUIRED_MARKERS = {
    DOCS_ROOT_PATH: (
        "`Documentation/zigux/phase8-exec-cmd-slice.md`",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8-validate`",
    ),
    REVIEW_CHECKLIST_PATH: (
        "if the change touches the parked Phase 8 `exec-cmd` packet",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
        "helper-first, output-stable deferred-exec planning packet",
        "separate `kernel/workqueue.c` Phase 14 boundary-study target",
    ),
    SCRIPTS_README_PATH: (
        "Phase 8 flow - `validate-phase8.py` checks that the parked libbpf and tooling packet stays aligned across",
        "`scripts/zigux/check-phase8-exec-cmd-packet.py`",
        "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`",
        "`Documentation/zigux/phase8-exec-cmd-slice.md`",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`make -C zigux phase8-validate`",
        "`make -C zigux phase8-exec-cmd-test`",
    ),
    TESTS_README_PATH: (
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8-validate`",
        "`make -C zigux phase8`",
    ),
    WORKFLOW_PATH: (
        "Validate Phase 8 tooling packet",
        "Run focused Phase 8 exec-cmd tests",
        "make -C zigux phase8-exec-cmd-test",
    ),
    MAKEFILE_PATH: (
        "phase8-validate:",
        "phase8-exec-cmd-test:",
        "scripts/zigux/validate-phase8.py",
        "phase8: phase8-validate",
    ),
    BOUNDARY_SURVEY_PATH: (
        "PHASE8_USERSPACE_KERNEL_BRIDGE_LANE_KEY=P8-L01",
        "`Documentation/zigux/phase8-exec-cmd-slice.md`",
        "`tools/lib/subcmd/exec-cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`python3 scripts/zigux/validate-phase8.py`",
    ),
    SEQUENCING_PATH: (
        "### 1. Exec-cmd lane",
        "public default-branch tree readback still lists `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_exec_cmd.zig`, and `zigux/tests/phase8_exec_cmd_only_build.zig`",
        "authenticated contents readback for the direct exec-cmd shard remains intermittent from this environment",
        "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` remains the dedicated boundary note",
    ),
    EXEC_CMD_SLICE_PATH: (
        "PHASE8_SLICE=exec-cmd-deferred-exec-packet",
        "helper-first, output-stable deferred-exec planning",
        "identity-based `sameFileLocation()`, `samePathIdentity()`, `choosePwdCwdFromFileIdentity()`, and `choosePwdCwdFromIdentities()` helpers",
        "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` stays the dedicated roadmap-gap survey for this file family while the direct exec-cmd shard remains helper-first and deferred-exec only.",
        "Within that parked packet, helper-local unit tests in `tools/lib/subcmd/exec-cmd.zig` own the low-level trailing-colon `PATH` edge, while the focused Phase 8 replay stays on the integrated deferred-exec packet so the live C helper anchors, checklist hook, and validator route stay aligned around one reviewable packet.",
        "zig test tools/lib/subcmd/exec-cmd.zig",
        "python3 scripts/zigux/check-phase8-exec-cmd-packet.py",
        "make -C zigux phase8-validate",
        "zigux/tests/phase8_exec_cmd_only_build.zig",
    ),
    EXEC_CMD_TEST_PATH: (
        'test "phase 8 exec-cmd module imports cleanly" {',
        'test "phase 8 exec-cmd focused replay keeps the integrated deferred-exec packet reviewable" {',
        'test "phase 8 exec-cmd slice note keeps the helper-vs-phase ownership boundary explicit" {',
        'test "phase 8 exec-cmd deferred boundary note still matches the live C helper anchors" {',
        'test "phase 8 exec-cmd scripts root summary keeps the focused replay route explicit" {',
        'test "phase 8 exec-cmd workflow keeps the focused replay ahead of sibling help shards" {',
        'test "phase 8 exec-cmd docs root summary keeps the focused replay route explicit" {',
        'test "phase 8 exec-cmd tests root summary keeps the focused replay route explicit" {',
    ),
    EXEC_CMD_ONLY_BUILD_PATH: (
        '.root_source_file = b.path("../../tools/lib/subcmd/exec-cmd.zig")',
        '.root_source_file = b.path("phase8_exec_cmd.zig")',
        'exec_cmd_root_module.addImport("exec_cmd", exec_cmd_module);',
        '.name = "phase8-exec-cmd-tests"',
        'b.step("test", "Run focused Phase 8 exec-cmd tests")',
    ),
    PHASE8_BUILD_PATH: (
        '.name = "phase8-exec-cmd-tests"',
        '.root_source_file = b.path("phase8_exec_cmd.zig")',
        'exec_cmd_root_module.addImport("exec_cmd", exec_cmd_module);',
        'test_step.dependOn(&run_exec_cmd_tests.step);',
        'b.step("test", "Run Phase 8 tooling expansion tests")',
    ),
    EXEC_CMD_SOURCE_PATH: (
        "pub fn buildDeferredExecvCall(",
        "pub fn buildDeferredExeclCall(",
        "pub fn samePathIdentity(",
        "pub fn choosePwdCwdFromIdentities(",
        "pub fn planDeferredExecvCall(",
        "pub fn planDeferredExecvCallWithPwd(",
        "pub fn planDeferredExeclCall(",
        "pub fn planDeferredExeclCallWithPwd(",
    ),
    EXEC_CMD_C_PATH: (
        "int execv_cmd",
        "int execl_cmd",
    ),
}

ORDERED_MARKER_SEQUENCES = {
    EXEC_CMD_SLICE_PATH: (
        "zig test tools/lib/subcmd/exec-cmd.zig",
        "python3 scripts/zigux/check-phase8-exec-cmd-packet.py",
        "make -C zigux phase8-validate",
        "zig build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all",
        "make -C zigux phase8-exec-cmd-test",
        "zig build test --build-file zigux/tests/phase8_build.zig --summary all",
    ),
    WORKFLOW_PATH: (
        " - name: Validate Phase 8 tooling packet",
        " - name: Run focused Phase 8 exec-cmd tests",
        " - name: Run focused Phase 8 help tests",
        " - name: Run focused Phase 8 kallsyms tests",
        " - name: Run focused Phase 8 help and kallsyms tests",
    ),
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    problems: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            problems.append(f"missing-file:{rel_path}")
    if problems:
        return problems

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                problems.append(f"missing-marker:{rel_path}:{marker}")

    for rel_path, ordered_markers in ORDERED_MARKER_SEQUENCES.items():
        text = read_text(root, rel_path)
        marker_indexes: list[tuple[str, int]] = []
        for marker in ordered_markers:
            marker_index = text.find(marker)
            if marker_index == -1:
                continue
            marker_indexes.append((marker, marker_index))

        for (earlier_marker, earlier_index), (later_marker, later_index) in zip(
            marker_indexes,
            marker_indexes[1:],
        ):
            if earlier_index >= later_index:
                problems.append(
                    f"marker-order:{rel_path}:{earlier_marker}:{later_marker}"
                )

    return problems


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / SCRIPT_PATH)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_fixture_root(root: Path) -> None:
    script_text = Path(__file__).read_text(encoding="utf-8")
    write_text(root, SCRIPT_PATH, script_text)
    for rel_path in REQUIRED_FILES:
        if rel_path == SCRIPT_PATH:
            continue
        markers = list(REQUIRED_MARKERS.get(rel_path, ()))
        for ordered_marker in ORDERED_MARKER_SEQUENCES.get(rel_path, ()):
            if ordered_marker not in markers:
                markers.append(ordered_marker)
        content = "\n".join(markers) + "\n" if markers else "# fixture\n"
        write_text(root, rel_path, content)


def assert_missing_case(root: Path, rel_path: str, marker: str) -> None:
    text = read_text(root, rel_path)
    if marker not in text:
        raise SystemExit(f"self-test-fixture-missing:{rel_path}:{marker}")
    (root / rel_path).write_text(text.replace(marker, "", 1), encoding="utf-8")
    result = run_validator(root)
    expected = f"missing-marker:{rel_path}:{marker}"
    output = result.stdout.strip() or result.stderr.strip() or "no_output"
    if result.returncode == 0:
        raise SystemExit(f"self-test-unexpected-pass:{rel_path}:{marker}")
    if expected not in output:
        raise SystemExit(f"self-test-mismatch:{expected}:{output}")


def assert_order_case(root: Path, rel_path: str, earlier_marker: str, later_marker: str) -> None:
    text = read_text(root, rel_path)
    earlier_index = text.find(earlier_marker)
    later_index = text.find(later_marker)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(f"self-test-fixture-missing-order:{rel_path}")
    if earlier_index >= later_index:
        raise SystemExit(f"self-test-fixture-order-already-broken:{rel_path}")

    swapped = (
        text[:earlier_index]
        + later_marker
        + text[earlier_index + len(earlier_marker) : later_index]
        + earlier_marker
        + text[later_index + len(later_marker) :]
    )
    (root / rel_path).write_text(swapped, encoding="utf-8")

    result = run_validator(root)
    expected = f"marker-order:{rel_path}:{earlier_marker}:{later_marker}"
    output = result.stdout.strip() or result.stderr.strip() or "no_output"
    if result.returncode == 0:
        raise SystemExit(f"self-test-order-unexpected-pass:{rel_path}")
    if expected not in output:
        raise SystemExit(f"self-test-order-mismatch:{expected}:{output}")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_exec_cmd_packet_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = run_validator(baseline_root)
        if baseline.returncode != 0:
            details = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
            raise SystemExit(f"self-test-baseline-failed:{details}")

        mutations = (
            (SCRIPTS_README_PATH, "Phase 8 flow - `validate-phase8.py` checks that the parked libbpf and tooling packet stays aligned across"),
            (SCRIPTS_README_PATH, "`scripts/zigux/check-phase8-exec-cmd-packet.py`"),
            (SCRIPTS_README_PATH, "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`"),
            (DOCS_ROOT_PATH, "`make -C zigux phase8-exec-cmd-test`"),
            (MAKEFILE_PATH, "phase8-exec-cmd-test:"),
            (BOUNDARY_SURVEY_PATH, "PHASE8_USERSPACE_KERNEL_BRIDGE_LANE_KEY=P8-L01"),
            (BOUNDARY_SURVEY_PATH, "`Documentation/zigux/phase8-exec-cmd-slice.md`"),
            (SEQUENCING_PATH, "### 1. Exec-cmd lane"),
            (SEQUENCING_PATH, "public default-branch tree readback still lists `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_exec_cmd.zig`, and `zigux/tests/phase8_exec_cmd_only_build.zig`"),
            (SEQUENCING_PATH, "authenticated contents readback for the direct exec-cmd shard remains intermittent from this environment"),
            (EXEC_CMD_SLICE_PATH, "PHASE8_SLICE=exec-cmd-deferred-exec-packet"),
            (EXEC_CMD_SLICE_PATH, "identity-based `sameFileLocation()`, `samePathIdentity()`, `choosePwdCwdFromFileIdentity()`, and `choosePwdCwdFromIdentities()` helpers"),
            (EXEC_CMD_SLICE_PATH, "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` stays the dedicated roadmap-gap survey for this file family while the direct exec-cmd shard remains helper-first and deferred-exec only."),
            (EXEC_CMD_SLICE_PATH, "Within that parked packet, helper-local unit tests in `tools/lib/subcmd/exec-cmd.zig` own the low-level trailing-colon `PATH` edge, while the focused Phase 8 replay stays on the integrated deferred-exec packet so the live C helper anchors, checklist hook, and validator route stay aligned around one reviewable packet."),
            (EXEC_CMD_SLICE_PATH, "zig test tools/lib/subcmd/exec-cmd.zig"),
            (EXEC_CMD_SLICE_PATH, "python3 scripts/zigux/check-phase8-exec-cmd-packet.py"),
            (EXEC_CMD_TEST_PATH, 'test "phase 8 exec-cmd focused replay keeps the integrated deferred-exec packet reviewable" {'),
            (EXEC_CMD_TEST_PATH, 'test "phase 8 exec-cmd deferred boundary note still matches the live C helper anchors" {'),
            (EXEC_CMD_TEST_PATH, 'test "phase 8 exec-cmd scripts root summary keeps the focused replay route explicit" {'),
            (EXEC_CMD_TEST_PATH, 'test "phase 8 exec-cmd workflow keeps the focused replay ahead of sibling help shards" {'),
            (EXEC_CMD_TEST_PATH, 'test "phase 8 exec-cmd docs root summary keeps the focused replay route explicit" {'),
            (EXEC_CMD_TEST_PATH, 'test "phase 8 exec-cmd tests root summary keeps the focused replay route explicit" {'),
            (EXEC_CMD_ONLY_BUILD_PATH, '.root_source_file = b.path("../../tools/lib/subcmd/exec-cmd.zig")'),
            (EXEC_CMD_ONLY_BUILD_PATH, '.root_source_file = b.path("phase8_exec_cmd.zig")'),
            (EXEC_CMD_ONLY_BUILD_PATH, 'exec_cmd_root_module.addImport("exec_cmd", exec_cmd_module);'),
            (EXEC_CMD_ONLY_BUILD_PATH, '.name = "phase8-exec-cmd-tests"'),
            (EXEC_CMD_ONLY_BUILD_PATH, 'b.step("test", "Run focused Phase 8 exec-cmd tests")'),
            (PHASE8_BUILD_PATH, '.name = "phase8-exec-cmd-tests"'),
            (PHASE8_BUILD_PATH, '.root_source_file = b.path("phase8_exec_cmd.zig")'),
            (PHASE8_BUILD_PATH, 'exec_cmd_root_module.addImport("exec_cmd", exec_cmd_module);'),
            (PHASE8_BUILD_PATH, 'test_step.dependOn(&run_exec_cmd_tests.step);'),
            (EXEC_CMD_SOURCE_PATH, "pub fn buildDeferredExecvCall("),
            (EXEC_CMD_SOURCE_PATH, "pub fn samePathIdentity("),
            (EXEC_CMD_SOURCE_PATH, "pub fn planDeferredExecvCall("),
            (EXEC_CMD_SOURCE_PATH, "pub fn planDeferredExeclCallWithPwd("),
        )
        for rel_path, marker in mutations:
            case_root = Path(tmp) / f"case_{cases}"
            shutil.copytree(baseline_root, case_root)
            assert_missing_case(case_root, rel_path, marker)
            cases += 1

        ordered_cases = (
            (
                EXEC_CMD_SLICE_PATH,
                "zig test tools/lib/subcmd/exec-cmd.zig",
                "python3 scripts/zigux/check-phase8-exec-cmd-packet.py",
            ),
            (
                WORKFLOW_PATH,
                " - name: Run focused Phase 8 exec-cmd tests",
                " - name: Run focused Phase 8 help tests",
            ),
        )
        for rel_path, earlier_marker, later_marker in ordered_cases:
            case_root = Path(tmp) / f"case_{cases}"
            shutil.copytree(baseline_root, case_root)
            assert_order_case(case_root, rel_path, earlier_marker, later_marker)
            cases += 1

        boundary_missing_root = Path(tmp) / f"case_{cases}"
        shutil.copytree(baseline_root, boundary_missing_root)
        (boundary_missing_root / BOUNDARY_SURVEY_PATH).unlink()
        boundary_missing_result = run_validator(boundary_missing_root)
        boundary_missing_output = boundary_missing_result.stdout.strip() or boundary_missing_result.stderr.strip() or "no_output"
        boundary_expected = f"missing-file:{BOUNDARY_SURVEY_PATH}"
        if boundary_missing_result.returncode == 0 or boundary_expected not in boundary_missing_output:
            raise SystemExit(f"self-test-missing-file-mismatch:{boundary_missing_output}")
        cases += 1

        missing_file_root = Path(tmp) / f"case_{cases}"
        shutil.copytree(baseline_root, missing_file_root)
        (missing_file_root / EXEC_CMD_ONLY_BUILD_PATH).unlink()
        missing_result = run_validator(missing_file_root)
        missing_output = missing_result.stdout.strip() or missing_result.stderr.strip() or "no_output"
        expected = f"missing-file:{EXEC_CMD_ONLY_BUILD_PATH}"
        if missing_result.returncode == 0 or expected not in missing_output:
            raise SystemExit(f"self-test-missing-file-mismatch:{missing_output}")
        cases += 1

    print("PHASE8_EXEC_CMD_PACKET_SELF_TEST=pass")
    print(f"PHASE8_EXEC_CMD_PACKET_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    problems = validate(root)
    if problems:
        print("PHASE8_EXEC_CMD_PACKET=fail")
        print("PHASE8_EXEC_CMD_PACKET_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE8_EXEC_CMD_PACKET_PROBLEMS_END")
        return 1

    print("PHASE8_EXEC_CMD_PACKET=pass")
    print(f"PHASE8_EXEC_CMD_PACKET_ROOT={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))