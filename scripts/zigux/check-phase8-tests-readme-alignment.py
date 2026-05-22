#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase8-tests-readme-alignment.py"
TESTS_README_PATH = "zigux/tests/README.md"
EXEC_CMD_SLICE_PATH = "Documentation/zigux/phase8-exec-cmd-slice.md"
EXEC_CMD_HELPER_PATH = "tools/lib/subcmd/exec-cmd.zig"
EXEC_CMD_TEST_PATH = "zigux/tests/phase8_exec_cmd.zig"
EXEC_CMD_BUILD_PATH = "zigux/tests/phase8_exec_cmd_only_build.zig"
PHASE8_VALIDATE_PATH = "scripts/zigux/validate-phase8.py"

REQUIRED_FILES = (
    SCRIPT_PATH,
    TESTS_README_PATH,
    EXEC_CMD_SLICE_PATH,
    EXEC_CMD_HELPER_PATH,
    EXEC_CMD_TEST_PATH,
    EXEC_CMD_BUILD_PATH,
    PHASE8_VALIDATE_PATH,
)

REQUIRED_MARKERS = {
    TESTS_README_PATH: (
        "current direct-readback Phase 8 anchors:",
        "`scripts/zigux/check-phase8-tests-readme-alignment.py`",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`scripts/zigux/validate-phase8.py`",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`zigux/tests/phase8_perf_buffer_poll.zig`",
        "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`",
        "current mixed-source file-path-handle bridge companions also remain reviewable on current `master` through the public tree and aligned reminder packet:",
        "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`",
        "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
        "`scripts/zigux/validate-phase8.py`",
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`zigux/tests/phase8_file_path_handle_boundary_guard.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`",
        "`zigux/tests/phase8_build.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "current `zigux/tests/phase8_build.zig` also keeps the landed boundary-guard and manifest-sync witnesses inside the shared aggregate replay, so this tests-root reminder should treat both checks as current current-`master` evidence instead of leaving them implied only by the aggregate build route",
        "repo-reality warning for the broader remaining Phase 8 tooling packet:",
        "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
        "`Documentation/zigux/phase8-perf-buffer-poll-slice.md`",
        "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
        "`Documentation/zigux/phase8-help-slice.md`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
        "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
        "`zigux/Makefile`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
        "`make -C zigux phase8-test`",
        "keep the narrower current Phase 8 reminder tied to the directly readable tests-readme checker plus the surviving perf-buffer poll checker, helper, and focused test packet, while also keeping the landed mixed-source file-path-handle bridge packet visible through the shared bridge-boundary survey, bridge slice, validator entrypoint, focused bridge proof, and helper-local replay instead of treating that same-lane bridge surface as missing current-master evidence",
        "current public-tree rereads now rematerialize the broader help, kallsyms, and libbpf-segment companions on `master`, so treat those returned paths as public-tree-backed broader packet evidence rather than as part of the narrow direct-readback anchor set",
        "if future same-lane work rematerializes the remaining broader docs, focused perf-buffer build shard, shared libbpf segment replay, or Makefile routes, or changes the focused bridge shard, the shared build replay, or the libbpf segment review packet, refresh this tests-root summary only after rereading the current direct-readback anchors together with the mixed-source file-path-handle bridge packet on current `master`",
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
        for marker, required_count in Counter(markers).items():
            if text.count(marker) < required_count:
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
    for rel_path, markers in REQUIRED_MARKERS.items():
        write_text(root, rel_path, "\n".join(markers) + "\n")
    write_text(root, EXEC_CMD_SLICE_PATH, "# Phase 8 Exec-Cmd Slice\n")
    write_text(root, EXEC_CMD_HELPER_PATH, "pub fn placeholder() void {}\n")
    write_text(root, EXEC_CMD_TEST_PATH, "test \"placeholder\" {}\n")
    write_text(root, EXEC_CMD_BUILD_PATH, "pub fn build() void {}\n")
    write_text(root, PHASE8_VALIDATE_PATH, "print('phase8 validate placeholder')\n")


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


def assert_missing_file_case(root: Path, rel_path: str) -> None:
    (root / rel_path).unlink()
    result = run_validator(root)
    expected = f"missing-file:{rel_path}"
    output = result.stdout.strip() or result.stderr.strip() or "no_output"
    if result.returncode == 0:
        raise SystemExit(f"self-test-unexpected-pass:{expected}")
    if expected not in output:
        raise SystemExit(f"self-test-mismatch:{expected}:{output}")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_tests_readme_alignment_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = run_validator(baseline_root)
        if baseline.returncode != 0:
            details = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
            raise SystemExit(f"self-test-baseline-failed:{details}")

        for rel_path, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                case_root = Path(tmp) / f"case_{cases}"
                shutil.copytree(baseline_root, case_root)
                assert_missing_case(case_root, rel_path, marker)
                cases += 1

        for rel_path in (
            TESTS_README_PATH,
            EXEC_CMD_SLICE_PATH,
            EXEC_CMD_HELPER_PATH,
            EXEC_CMD_TEST_PATH,
            EXEC_CMD_BUILD_PATH,
            PHASE8_VALIDATE_PATH,
        ):
            case_root = Path(tmp) / f"case_{cases}"
            shutil.copytree(baseline_root, case_root)
            assert_missing_file_case(case_root, rel_path)
            cases += 1

        missing_file_root = Path(tmp) / f"case_{cases}"
        shutil.copytree(baseline_root, missing_file_root)
        (missing_file_root / SCRIPT_PATH).unlink()
        missing_result = run_validator(missing_file_root)
        missing_output = (
            missing_result.stdout.strip()
            or missing_result.stderr.strip()
            or "no_output"
        )
        if missing_result.returncode == 0 or "can't open file" not in missing_output:
            raise SystemExit(f"self-test-missing-file-mismatch:{missing_output}")
        cases += 1

    print("PHASE8_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE8_TESTS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    problems = validate(root)
    if problems:
        print("PHASE8_TESTS_README_ALIGNMENT=fail")
        print("PHASE8_TESTS_README_ALIGNMENT_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE8_TESTS_README_ALIGNMENT_PROBLEMS_END")
        return 1

    print("PHASE8_TESTS_README_ALIGNMENT=pass")
    print(f"PHASE8_TESTS_README_ALIGNMENT_ROOT={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
