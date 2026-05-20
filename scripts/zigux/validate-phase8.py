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
    Path("Documentation/zigux/phase8-file-path-handle-bridge-slice.md"),
    Path("Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"),
    Path("scripts/zigux/README.md"),
    TESTS_ALIGNMENT_CHECKER,
    PERF_BUFFER_POLL_GATE_CHECKER,
    Path("zigux/Makefile"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/phase8_build.zig"),
    Path("zigux/tests/phase8_file_path_handle_bridge.zig"),
    Path("zigux/tests/phase8_file_path_handle_bridge_only_build.zig"),
    Path("zigux/tests/phase8_perf_buffer_poll.zig"),
    Path("tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"),
    Path("tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
)

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    Path("zigux/Makefile"): (
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py",
        "phase8-file-path-handle-bridge-test:",
        "phase8-perf-buffer-poll-test:",
        "phase8-test:",
    ),
    Path(".github/workflows/zigux-bootstrap.yml"): (
        "Validate Phase 8 tooling routes",
        "make -C zigux phase8-validate",
        "Run Phase 8 tooling tests",
    ),
    Path("Documentation/zigux/README.md"): (
        "Phase 8 notes",
        "scripts/zigux/validate-phase8.py",
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
    ),
    Path("Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"): (
        "phase8-userspace-kernel-bridge-boundary",
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
    ),
    Path("Documentation/zigux/phase8-file-path-handle-bridge-slice.md"): (
        "phase8-file-path-handle-bridge",
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
    ),
    Path("scripts/zigux/README.md"): (
        "## Phase 8",
        "scripts/zigux/check-phase8-tests-readme-alignment.py",
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "scripts/zigux/validate-phase8.py",
        "zigux/tests/phase8_perf_buffer_poll.zig",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ),
    Path("zigux/tests/README.md"): (
        "current direct-readback Phase 8 anchors:",
        "`scripts/zigux/check-phase8-tests-readme-alignment.py`",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`zigux/tests/phase8_perf_buffer_poll.zig`",
        "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`",
        "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`",
        "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`zigux/tests/phase8_build.zig`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
    ),
    Path("zigux/tests/phase8_perf_buffer_poll.zig"): (
        "phase 8 perf-buffer poll tests README keeps the current direct-readback packet explicit",
        "\"zigux/tests/README.md\"",
        "\"scripts/zigux/README.md\"",
        "resolveReadyBufferFdAtAttempt",
        "resolveReadyBufferFdLookupReturnAtAttempt",
        "summarizePollExecutionResultFromWaitResult",
        "summarizeBufferFdLookup",
        "summarizeBufferWindowLookup",
    ),
    Path("zigux/tests/phase8_file_path_handle_bridge.zig"): (
        "phase 8 file-path-handle bridge",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ),
    Path("zigux/tests/phase8_file_path_handle_bridge_only_build.zig"): (
        "phase8_file_path_handle_bridge.zig",
        "phase8_file_path_handle_bridge",
        "Run the phase 8 file-path-handle bridge tests.",
    ),
    Path("zigux/tests/phase8_build.zig"): (
        "phase8_perf_buffer_poll",
        "phase8_file_path_handle_bridge",
    ),
    Path("tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"): (
        "pub const BufferFdLookupDisposition = enum {",
        "pub fn resolveReadyBufferFdAtAttempt(",
        "pub fn resolveReadyBufferFdLookupReturnAtAttempt(",
        "pub fn summarizeBufferWindowLookup(",
        "test \"phase8 perf-buffer poll resolves ready-buffer fd lookups without manual slot plumbing\" {",
    ),
    Path("tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"): (
        "file_path_handle_bridge",
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
    for relative_path, markers in FILE_MARKERS.items():
        _write(root / relative_path, "\n".join(markers) + "\n")
    _write(root / TESTS_ALIGNMENT_CHECKER, _passing_checker("PHASE8_TESTS_README_ALIGNMENT"))
    _write(root / PERF_BUFFER_POLL_GATE_CHECKER, _passing_checker("PHASE8_PERF_BUFFER_POLL_GATE"))


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
                "missing_marker:zigux/tests/phase8_perf_buffer_poll.zig:resolveReadyBufferFdAtAttempt",
            ),
        )
        failing_checker = validate_root(root)
        checker_output = failing_checker.checker_failures.get(PERF_BUFFER_POLL_GATE_CHECKER.as_posix())
        if not checker_output or "resolveReadyBufferFdAtAttempt" not in "\n".join(checker_output):
            raise AssertionError("expected checker failure output to be reported")
        _write(broken_checker, _passing_checker("PHASE8_PERF_BUFFER_POLL_GATE"))

        makefile = root / "zigux/Makefile"
        original_makefile = _read(makefile)
        makefile.write_text(
            original_makefile.replace("phase8-perf-buffer-poll-test:\n", "", 1),
            encoding="utf-8",
        )
        missing_make_marker = validate_root(root)
        expected_make_marker = "zigux/Makefile:phase8-perf-buffer-poll-test:"
        if expected_make_marker not in missing_make_marker.missing_markers:
            raise AssertionError("expected missing Makefile Phase 8 marker to be reported")
        makefile.write_text(original_makefile, encoding="utf-8")

        bridge_test = root / "zigux/tests/phase8_file_path_handle_bridge.zig"
        original_bridge_test = _read(bridge_test)
        bridge_test.write_text(
            original_bridge_test.replace("tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig", "", 1),
            encoding="utf-8",
        )
        missing_bridge_marker = validate_root(root)
        expected_bridge_marker = (
            "zigux/tests/phase8_file_path_handle_bridge.zig:"
            "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"
        )
        if expected_bridge_marker not in missing_bridge_marker.missing_markers:
            raise AssertionError("expected missing bridge replay marker to be reported")
        bridge_test.write_text(original_bridge_test, encoding="utf-8")

        missing_helper = root / "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"
        missing_helper.unlink()
        missing_perf_helper = validate_root(root)
        if "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig" not in missing_perf_helper.missing_files:
            raise AssertionError("expected missing perf-buffer helper file to be reported")
        _write(missing_helper, "\n".join(FILE_MARKERS[Path("tools/lib/bpf/zigux_segments/perf_buffer_poll.zig")]) + "\n")

        missing_bridge_build = root / "zigux/tests/phase8_file_path_handle_bridge_only_build.zig"
        missing_bridge_build.unlink()
        missing_build = validate_root(root)
        if "zigux/tests/phase8_file_path_handle_bridge_only_build.zig" not in missing_build.missing_files:
            raise AssertionError("expected missing bridge build shard to be reported")
        _write(
            missing_bridge_build,
            "\n".join(FILE_MARKERS[Path("zigux/tests/phase8_file_path_handle_bridge_only_build.zig")]) + "\n",
        )

    print("PHASE8_VALIDATE_SELF_TEST=pass")
    print("PHASE8_VALIDATE_SELF_TEST_CASE_COUNT=5")
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
