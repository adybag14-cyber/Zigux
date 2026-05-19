#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


def _default_root() -> Path:
    resolved = Path(__file__).resolve()
    if len(resolved.parents) >= 3:
        return resolved.parents[2]
    return resolved.parent


ROOT = _default_root()
TESTS_ALIGNMENT_CHECKER = Path("scripts/zigux/check-phase8-tests-readme-alignment.py")
PERF_BUFFER_POLL_GATE_CHECKER = Path("scripts/zigux/check-phase8-perf-buffer-poll-gate.py")

REQUIRED_FILES = (
    Path(".github/workflows/zigux-bootstrap.yml"),
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("scripts/zigux/README.md"),
    TESTS_ALIGNMENT_CHECKER,
    PERF_BUFFER_POLL_GATE_CHECKER,
    Path("zigux/Makefile"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/phase8_exec_cmd.zig"),
    Path("zigux/tests/phase8_exec_cmd_only_build.zig"),
    Path("zigux/tests/phase8_perf_buffer_poll.zig"),
    Path("tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
)

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    Path("zigux/Makefile"): (
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py",
        "phase8-exec-cmd-test:",
        "phase8-file-path-handle-bridge-test:",
        "phase8-libbpf-segments-test:",
        "phase8-perf-buffer-poll-test:",
        "phase8-test:",
    ),
    Path(".github/workflows/zigux-bootstrap.yml"): (
        "Validate Phase 8 tooling routes",
        "make -C zigux phase8-validate",
        "Run focused Phase 8 exec-cmd tests",
        "Run Phase 8 tooling tests",
    ),
    Path("Documentation/zigux/README.md"): (
        "Phase 8 notes",
        "tools/lib/subcmd/exec-cmd.zig",
        "scripts/zigux/validate-phase8.py",
    ),
    Path("Documentation/zigux/review-checklist.md"): (
        "if the change touches the parked Phase 8 `exec-cmd` packet",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8-validate`",
        "separate `kernel/workqueue.c` Phase 14 boundary-study target",
    ),
    Path("scripts/zigux/README.md"): (
        "## Phase 8",
        "scripts/zigux/validate-phase8.py",
    ),
    Path("zigux/tests/phase8_exec_cmd.zig"): (
        'test "phase 8 exec-cmd review witness keeps the surviving shared reminder surfaces explicit" {',
        '"scripts/zigux/validate-phase8.py"',
        '"Documentation/zigux/review-checklist.md"',
        '"kernel/workqueue.c"',
    ),
    Path("zigux/tests/phase8_exec_cmd_only_build.zig"): (
        '.root_source_file = b.path("phase8_exec_cmd.zig")',
        '.name = "phase8_exec_cmd"',
        'b.step("test", "Run the phase 8 exec-cmd review witness tests.")',
    ),
}


@dataclass
class ValidationResult:
    missing_files: list[str]
    missing_markers: list[str]
    checker_failures: dict[str, list[str]]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _collect_missing_markers(root: Path) -> list[str]:
    missing_markers: list[str] = []
    for relative_path, markers in FILE_MARKERS.items():
        path = root / relative_path
        if not path.exists():
            continue
        text = _read(path)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{relative_path}:{marker}")
    return missing_markers


def _run_checker(root: Path, checker: Path) -> list[str]:
    result = subprocess.run(
        [sys.executable, str(root / checker)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return []
    output = result.stdout.strip() or result.stderr.strip() or "no_output"
    return output.splitlines()


def validate_root(root: Path) -> ValidationResult:
    missing_files = [
        path.as_posix()
        for path in REQUIRED_FILES
        if not (root / path).exists()
    ]
    missing_markers = _collect_missing_markers(root)

    checker_failures: dict[str, list[str]] = {}
    if not missing_files and not missing_markers:
        for checker in (TESTS_ALIGNMENT_CHECKER, PERF_BUFFER_POLL_GATE_CHECKER):
            output = _run_checker(root, checker)
            if output:
                checker_failures[checker.as_posix()] = output

    return ValidationResult(
        missing_files=missing_files,
        missing_markers=missing_markers,
        checker_failures=checker_failures,
    )


def emit_result(result: ValidationResult) -> int:
    if result.missing_files or result.missing_markers or result.checker_failures:
        print("PHASE8_VALIDATION=fail")
        if result.missing_files:
            print("PHASE8_MISSING_FILES_START")
            for item in result.missing_files:
                print(item)
            print("PHASE8_MISSING_FILES_END")
        if result.missing_markers:
            print("PHASE8_MISSING_MARKERS_START")
            for item in result.missing_markers:
                print(item)
            print("PHASE8_MISSING_MARKERS_END")
        if result.checker_failures:
            for checker, lines in result.checker_failures.items():
                print(f"PHASE8_CHECKER_FAILURE_START={checker}")
                for line in lines:
                    print(line)
                print(f"PHASE8_CHECKER_FAILURE_END={checker}")
        return 1

    print("PHASE8_VALIDATION=pass")
    print(f"PHASE8_SHARED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE8_MARKER_COUNT={sum(len(markers) for markers in FILE_MARKERS.values())}")
    print("PHASE8_CHECKER_COUNT=2")
    return 0


def _passing_checker(token: str) -> str:
    return "\n".join(
        (
            "#!/usr/bin/env python3",
            "from __future__ import annotations",
            "",
            f'print("{token}=pass")',
            "",
        )
    )


def _failing_checker(token: str, reason: str) -> str:
    return "\n".join(
        (
            "#!/usr/bin/env python3",
            "from __future__ import annotations",
            "",
            f'print("{token}=fail")',
            f'print("{reason}")',
            "raise SystemExit(1)",
            "",
        )
    )


def _passing_fixture(root: Path) -> None:
    _write(root / "zigux/Makefile", "\n".join(FILE_MARKERS[Path("zigux/Makefile")]))
    _write(
        root / ".github/workflows/zigux-bootstrap.yml",
        "\n".join(FILE_MARKERS[Path(".github/workflows/zigux-bootstrap.yml")]),
    )
    _write(
        root / "Documentation/zigux/README.md",
        "\n".join(FILE_MARKERS[Path("Documentation/zigux/README.md")]),
    )
    _write(
        root / "Documentation/zigux/review-checklist.md",
        "\n".join(FILE_MARKERS[Path("Documentation/zigux/review-checklist.md")]),
    )
    _write(
        root / "scripts/zigux/README.md",
        "\n".join(FILE_MARKERS[Path("scripts/zigux/README.md")]),
    )
    _write(root / "zigux/tests/README.md", "Phase 8 tests reminder\n")
    _write(
        root / "zigux/tests/phase8_exec_cmd.zig",
        "\n".join(FILE_MARKERS[Path("zigux/tests/phase8_exec_cmd.zig")]),
    )
    _write(
        root / "zigux/tests/phase8_exec_cmd_only_build.zig",
        "\n".join(FILE_MARKERS[Path("zigux/tests/phase8_exec_cmd_only_build.zig")]),
    )
    _write(root / "zigux/tests/phase8_perf_buffer_poll.zig", "phase8 perf-buffer poll test\n")
    _write(
        root / "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "pub fn summarizePollExecutionResultFromWaitResult() void {}\n",
    )
    _write(
        root / TESTS_ALIGNMENT_CHECKER,
        _passing_checker("PHASE8_TESTS_README_ALIGNMENT"),
    )
    _write(
        root / PERF_BUFFER_POLL_GATE_CHECKER,
        _passing_checker("PHASE8_PERF_BUFFER_POLL_GATE"),
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase8-validate-selftest-") as tmp:
        root = Path(tmp)
        _passing_fixture(root)

        passing = validate_root(root)
        if passing.missing_files or passing.missing_markers or passing.checker_failures:
            raise AssertionError("expected passing fixture to validate")

        broken_checker = root / PERF_BUFFER_POLL_GATE_CHECKER
        _write(
            broken_checker,
            _failing_checker(
                "PHASE8_PERF_BUFFER_POLL_GATE",
                "missing_marker:zigux/tests/phase8_perf_buffer_poll.zig:surviving direct Phase 8 replay surface",
            ),
        )
        failing_checker = validate_root(root)
        checker_output = failing_checker.checker_failures.get(PERF_BUFFER_POLL_GATE_CHECKER.as_posix())
        if not checker_output or "missing_marker:zigux/tests/phase8_perf_buffer_poll.zig:surviving direct Phase 8 replay surface" not in checker_output:
            raise AssertionError("expected checker failure output to be reported")
        _write(broken_checker, _passing_checker("PHASE8_PERF_BUFFER_POLL_GATE"))

        makefile = root / "zigux/Makefile"
        original_makefile = _read(makefile)
        makefile.write_text(
            original_makefile.replace("phase8-libbpf-segments-test:\n", "", 1),
            encoding="utf-8",
        )
        missing_make_marker = validate_root(root)
        expected_make_marker = "zigux/Makefile:phase8-libbpf-segments-test:"
        if expected_make_marker not in missing_make_marker.missing_markers:
            raise AssertionError("expected missing makefile libbpf route marker to be reported")
        makefile.write_text(original_makefile, encoding="utf-8")

        exec_test = root / "zigux/tests/phase8_exec_cmd.zig"
        original_exec_test = _read(exec_test)
        exec_test.write_text(
            original_exec_test.replace('"kernel/workqueue.c"', "", 1),
            encoding="utf-8",
        )
        missing_exec_marker = validate_root(root)
        expected_exec_marker = 'zigux/tests/phase8_exec_cmd.zig:"kernel/workqueue.c"'
        if expected_exec_marker not in missing_exec_marker.missing_markers:
            raise AssertionError("expected missing exec-cmd witness marker to be reported")
        exec_test.write_text(original_exec_test, encoding="utf-8")

        perf_test = root / "zigux/tests/phase8_perf_buffer_poll.zig"
        perf_test.unlink()
        missing_perf_test = validate_root(root)
        if "zigux/tests/phase8_perf_buffer_poll.zig" not in missing_perf_test.missing_files:
            raise AssertionError("expected missing perf-buffer test file to be reported")
        _write(perf_test, "phase8 perf-buffer poll test\n")

        perf_helper = root / "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"
        perf_helper.unlink()
        missing_perf_helper = validate_root(root)
        if "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig" not in missing_perf_helper.missing_files:
            raise AssertionError("expected missing perf-buffer helper file to be reported")
        _write(perf_helper, "pub fn summarizePollExecutionResultFromWaitResult() void {}\n")

        tests_checker = root / TESTS_ALIGNMENT_CHECKER
        tests_checker.unlink()
        missing_checker = validate_root(root)
        if TESTS_ALIGNMENT_CHECKER.as_posix() not in missing_checker.missing_files:
            raise AssertionError("expected missing tests-alignment checker to be reported")
        _write(tests_checker, _passing_checker("PHASE8_TESTS_README_ALIGNMENT"))

    print("PHASE8_VALIDATE_SELF_TEST=pass")
    print("PHASE8_VALIDATE_SELF_TEST_CASE_COUNT=6")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return emit_result(validate_root(args.root))


if __name__ == "__main__":
    raise SystemExit(main())
