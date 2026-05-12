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
        "Phase 8 flow - the current shared Phase 8 review surface on `master` is",
        "`scripts/zigux/check-phase8-exec-cmd-packet.py`",
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
    EXEC_CMD_SLICE_PATH: (
        "PHASE8_SLICE=exec-cmd-deferred-exec-packet",
        "helper-first, output-stable deferred-exec planning",
        "identity-based `sameFileLocation()`, `samePathIdentity()`, `choosePwdCwdFromFileIdentity()`, and `choosePwdCwdFromIdentities()` helpers",
        "make -C zigux phase8-validate",
        "zigux/tests/phase8_exec_cmd_only_build.zig",
    ),
    EXEC_CMD_TEST_PATH: (
        'test "phase 8 exec-cmd module imports cleanly" {',
        'test "phase 8 exec-cmd slice note keeps the helper-vs-phase ownership boundary explicit" {',
        'test "phase 8 exec-cmd scripts root summary keeps the focused replay route explicit" {',
    ),
    EXEC_CMD_SOURCE_PATH: (
        "pub fn buildDeferredExecvCall(",
        "pub fn buildDeferredExeclCall(",
    ),
    EXEC_CMD_C_PATH: (
        "int execv_cmd",
        "int execl_cmd",
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
        markers = REQUIRED_MARKERS.get(rel_path)
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
            (SCRIPTS_README_PATH, "`scripts/zigux/check-phase8-exec-cmd-packet.py`"),
            (DOCS_ROOT_PATH, "`make -C zigux phase8-exec-cmd-test`"),
            (WORKFLOW_PATH, "Run focused Phase 8 exec-cmd tests"),
            (MAKEFILE_PATH, "phase8-exec-cmd-test:"),
            (EXEC_CMD_SLICE_PATH, "PHASE8_SLICE=exec-cmd-deferred-exec-packet"),
            (EXEC_CMD_SLICE_PATH, "identity-based `sameFileLocation()`, `samePathIdentity()`, `choosePwdCwdFromFileIdentity()`, and `choosePwdCwdFromIdentities()` helpers"),
            (EXEC_CMD_TEST_PATH, 'test "phase 8 exec-cmd scripts root summary keeps the focused replay route explicit" {'),
            (EXEC_CMD_SOURCE_PATH, "pub fn buildDeferredExecvCall("),
        )
        for rel_path, marker in mutations:
            case_root = Path(tmp) / f"case_{cases}"
            shutil.copytree(baseline_root, case_root)
            assert_missing_case(case_root, rel_path, marker)
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
