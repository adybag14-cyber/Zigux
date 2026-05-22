#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase8-libbpf-shard-routes.py"
VALIDATOR_PATH = "scripts/zigux/validate-phase8.py"
SURVEY_PATH = "Documentation/zigux/phase8-libbpf-segment-survey.md"
MAKEFILE_PATH = "zigux/Makefile"
PHASE8_BUILD_PATH = "zigux/tests/phase8_build.zig"
VERIFY_ROUTING_GAP_TEST_PATH = "zigux/tests/phase8_verify_routing_gap.zig"
VERIFY_ROUTING_GAP_BUILD_PATH = "zigux/tests/phase8_verify_routing_gap_only_build.zig"
LIBBPF_SEGMENTS_TEST_PATH = "zigux/tests/phase8_libbpf_segments.zig"
LIBBPF_SEGMENTS_BUILD_PATH = "zigux/tests/phase8_libbpf_segments_only_build.zig"
VERIFY_PATH = "tools/lib/bpf/zigux_segments/verify.zig"
CPU_MASK_PATH = "tools/lib/bpf/zigux_segments/cpu_mask.zig"
CPU_MASK_VERIFY_PATH = "tools/lib/bpf/zigux_segments/cpu_mask_verify.zig"
LOGGING_PATH = "tools/lib/bpf/zigux_segments/logging.zig"
LOGGING_VERIFY_PATH = "tools/lib/bpf/zigux_segments/logging_verify.zig"
ONLINE_CPU_ROUTING_PATH = "tools/lib/bpf/zigux_segments/online_cpu_routing.zig"
ONLINE_CPU_ROUTING_VERIFY_PATH = "tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig"
PERF_BUFFER_POLL_VERIFY_PATH = "tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig"
PIN_PATH_PATH = "tools/lib/bpf/zigux_segments/pin_path.zig"
PIN_PATH_VERIFY_PATH = "tools/lib/bpf/zigux_segments/pin_path_verify.zig"
READY_BUFFER_ATTEMPT_VERIFY_PATH = "tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig"
READY_BUFFER_FD_VERIFY_PATH = "tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig"
READY_BUFFER_WINDOW_VERIFY_PATH = "tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig"
TYPE_NAMES_VERIFY_PATH = "tools/lib/bpf/zigux_segments/type_names_verify.zig"

REQUIRED_FILES = (
    SCRIPT_PATH,
    VALIDATOR_PATH,
    SURVEY_PATH,
    MAKEFILE_PATH,
    PHASE8_BUILD_PATH,
    VERIFY_ROUTING_GAP_TEST_PATH,
    VERIFY_ROUTING_GAP_BUILD_PATH,
    LIBBPF_SEGMENTS_TEST_PATH,
    LIBBPF_SEGMENTS_BUILD_PATH,
    VERIFY_PATH,
    CPU_MASK_PATH,
    CPU_MASK_VERIFY_PATH,
    LOGGING_PATH,
    LOGGING_VERIFY_PATH,
    ONLINE_CPU_ROUTING_PATH,
    ONLINE_CPU_ROUTING_VERIFY_PATH,
    PERF_BUFFER_POLL_VERIFY_PATH,
    PIN_PATH_PATH,
    PIN_PATH_VERIFY_PATH,
    READY_BUFFER_ATTEMPT_VERIFY_PATH,
    READY_BUFFER_FD_VERIFY_PATH,
    READY_BUFFER_WINDOW_VERIFY_PATH,
    TYPE_NAMES_VERIFY_PATH,
)

REQUIRED_MARKERS = {
    VALIDATOR_PATH: (
        'LIBBPF_SHARD_ROUTES_CHECKER = Path("scripts/zigux/check-phase8-libbpf-shard-routes.py")',
        "LIBBPF_SHARD_ROUTES_CHECKER,",
        "CPU_MASK_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/cpu_mask.zig\")",
        "CPU_MASK_VERIFY_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/cpu_mask_verify.zig\")",
        "LOGGING_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/logging.zig\")",
        "LOGGING_VERIFY_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/logging_verify.zig\")",
        "PIN_PATH_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/pin_path.zig\")",
        "PIN_PATH_VERIFY_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/pin_path_verify.zig\")",
    ),
    SURVEY_PATH: (
        "Current helper-plus-build packet",
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "`tools/lib/bpf/zigux_segments/cpu_mask.zig`",
        "`tools/lib/bpf/zigux_segments/cpu_mask_verify.zig`",
        "`tools/lib/bpf/zigux_segments/logging.zig`",
        "`tools/lib/bpf/zigux_segments/logging_verify.zig`",
        "`tools/lib/bpf/zigux_segments/type_names.zig`",
        "`tools/lib/bpf/zigux_segments/pin_path.zig`",
        "`tools/lib/bpf/zigux_segments/pin_path_verify.zig`",
        "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`",
        "`tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`",
        "`tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig`",
        "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig`",
        "`tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig`",
        "`zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet.",
        "Current authenticated tree readback in this runtime is narrower than some older Phase 8 reminder surfaces:",
        "`tools/lib/bpf/zigux_segments/manifest.json`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, and the focused libbpf bridge-side build companions are not currently materialized through the same direct-read path.",
        "`zigux/tests/phase8_verify_routing_gap.zig` plus `zigux/tests/phase8_verify_routing_gap_only_build.zig`",
        "make -C zigux phase8-perf-buffer-poll-test",
    ),
    MAKEFILE_PATH: (
        "phase8-libbpf-segments-test:",
        "zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
        "phase8-test:",
        "zigux/tests/phase8_build.zig --summary all",
    ),
    PHASE8_BUILD_PATH: (
        "../../tools/lib/bpf/zigux_segments/verify.zig",
        "phase8_libbpf_segments.zig",
        "phase8_verify_routing_gap.zig",
        "phase8-perf-buffer-ready-window-tests",
        "test_step.dependOn(&run_perf_buffer_ready_window_tests.step);",
        "phase8-file-path-handle-boundary-guard-tests",
        "test_step.dependOn(&run_file_path_handle_boundary_guard_tests.step);",
        "phase8-file-path-handle-bridge-manifest-sync-tests",
        "test_step.dependOn(&run_file_path_handle_bridge_manifest_sync_tests.step);",
        "phase8-libbpf-segment-verify-tests",
        "phase8-libbpf-segment-compatibility-tests",
        "phase8-verify-routing-gap-tests",
        "Run the shared Phase 8 tooling tests.",
    ),
    VERIFY_ROUTING_GAP_TEST_PATH: (
        "phase 8 verify routing witness records the current CPU-index verifier closure",
        "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex",
        "phase 8 verify routing witness records the current direct-readback libbpf survey packet",
    ),
    VERIFY_ROUTING_GAP_BUILD_PATH: (
        "phase8_verify_routing_gap.zig",
        "phase8_verify_routing_gap",
        "Run the phase 8 verify routing witness tests.",
    ),
    LIBBPF_SEGMENTS_TEST_PATH: (
        'test "phase 8 libbpf-segment compatibility witness keeps the focused verify-routing replay visible" {',
        'test "phase 8 libbpf-segment compatibility witness keeps the shared no-timer poll boundary explicit" {',
    ),
    LIBBPF_SEGMENTS_BUILD_PATH: (
        'b.path("../../tools/lib/bpf/zigux_segments/verify.zig")',
        '"phase8-libbpf-segment-verify-tests"',
        '"Run focused Phase 8 libbpf segment verify build"',
    ),
    VERIFY_PATH: (
        'const cpu_mask_verify = @import("cpu_mask_verify.zig");',
        'const logging_verify = @import("logging_verify.zig");',
        'const online_cpu_routing_verify = @import("online_cpu_routing_verify.zig");',
        'const pin_path_verify = @import("pin_path_verify.zig");',
        "std.testing.refAllDecls(cpu_mask_verify);",
        "std.testing.refAllDecls(logging_verify);",
        "std.testing.refAllDecls(online_cpu_routing_verify);",
        "std.testing.refAllDecls(pin_path_verify);",
        "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex",
        "resolveReadyBufferFdLookupReturnAtAttempt",
    ),
    CPU_MASK_PATH: (
        "pub fn parseCpuMaskString(",
        "pub fn summarizePossibleCpusFromReader(",
        "pub fn derivePerfBufferAutoCpuCountFromReader(",
    ),
    CPU_MASK_VERIFY_PATH: (
        'test "phase8 cpu-mask helper entrypoints stay explicit" {',
        "derivePerfBufferAutoCpuCountFromReader",
        'test "phase8 cpu-mask helpers keep invalid direct and reader-backed inputs fail-closed" {',
    ),
    LOGGING_PATH: (
        "pub fn parseLogLevelSetting(",
        "pub fn libbpfVersionString(",
        "pub fn formatLibbpfError(",
    ),
    LOGGING_VERIFY_PATH: (
        'test "phase8 logging helper entrypoints stay explicit" {',
        "parseLogLevelSetting",
        "formatLibbpfError",
    ),
    ONLINE_CPU_ROUTING_PATH: (
        "pub fn resolveNextOnlineCpuRouteCpuIndex(",
        "pub fn resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(",
        'test "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex keeps direct errno-shaped route-cpu wrappers aligned" {',
    ),
    ONLINE_CPU_ROUTING_VERIFY_PATH: (
        'test "phase8 online-cpu route helpers keep typed cpu-index wrappers stable" {',
        "resolveNextOnlineCpuRouteCpuIndex(",
        "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(",
    ),
    PERF_BUFFER_POLL_VERIFY_PATH: (
        'test "phase8 perf-buffer poll helper entrypoints stay explicit" {',
        "summarizePollExecutionResultFromWaitResult",
        'test "phase8 perf-buffer poll rejects impossible hand-built summaries and mismatched ready waits" {',
    ),
    PIN_PATH_PATH: (
        'pub const default_bpf_fs_path = "/sys/fs/bpf";',
        "pub fn buildValidatedMapPinPath(",
        "pub fn buildValidatedSanitizedProgramPinPath(",
    ),
    PIN_PATH_VERIFY_PATH: (
        'test "phase8 pin-path helper entrypoints stay explicit" {',
        "buildValidatedSanitizedProgramPinPath",
        'test "phase8 pin-path helpers keep stable map and program outputs explicit" {',
    ),
    READY_BUFFER_ATTEMPT_VERIFY_PATH: (
        'test "phase8 ready-buffer attempt helper entrypoints stay explicit" {',
        "resolveReadyBufferAttemptLookupReturn",
        'test "phase8 ready-buffer attempt helpers keep errno-shaped outputs stable" {',
    ),
    READY_BUFFER_FD_VERIFY_PATH: (
        'test "phase8 ready-buffer fd helper entrypoints stay explicit" {',
        "resolveReadyBufferFdAtAttempt",
        "resolveReadyBufferFdLookupReturnAtAttempt",
    ),
    READY_BUFFER_WINDOW_VERIFY_PATH: (
        'test "phase8 ready-buffer window helper entrypoints stay explicit" {',
        "resolveReadyBufferWindowMappedSizeReturnAtAttempt",
        "resolveReadyBufferWindowLookupReturnAtAttempt",
    ),
    TYPE_NAMES_VERIFY_PATH: (
        'test "phase8 libbpf type-name helper entrypoints stay explicit" {',
        "libbpfBpfMapTypeStr(27)",
        "formatLibbpfBpfProgType(prog_buffer[0..], 33)",
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
    for rel_path, markers in REQUIRED_MARKERS.items():
        write_text(root, rel_path, "\n".join(markers) + "\n")


def assert_missing_case(root: Path, rel_path: str, marker: str) -> None:
    text = read_text(root, rel_path)
    if marker not in text:
        raise SystemExit(f"self-test-fixture-missing:{rel_path}:{marker}")

    (root / rel_path).write_text(text.replace(marker, ""), encoding="utf-8")
    result = run_validator(root)
    expected = f"missing-marker:{rel_path}:{marker}"
    output = result.stdout.strip() or result.stderr.strip() or "no_output"
    if result.returncode == 0:
        raise SystemExit(f"self-test-unexpected-pass:{expected}")
    if expected not in output:
        raise SystemExit(f"self-test-mismatch:{expected}:{output}")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_libbpf_shard_routes_") as tmp:
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

        for rel_path in REQUIRED_FILES[1:]:
            case_root = Path(tmp) / f"case_{cases}"
            shutil.copytree(baseline_root, case_root)
            (case_root / rel_path).unlink()
            result = run_validator(case_root)
            expected = f"missing-file:{rel_path}"
            output = result.stdout.strip() or result.stderr.strip() or "no_output"
            if result.returncode == 0:
                raise SystemExit(f"self-test-unexpected-pass:{expected}")
            if expected not in output:
                raise SystemExit(f"self-test-mismatch:{expected}:{output}")
            cases += 1

        missing_script_root = Path(tmp) / f"case_{cases}"
        shutil.copytree(baseline_root, missing_script_root)
        (missing_script_root / SCRIPT_PATH).unlink()
        missing_result = run_validator(missing_script_root)
        missing_output = (
            missing_result.stdout.strip() or missing_result.stderr.strip() or "no_output"
        )
        if missing_result.returncode == 0 or "can't open file" not in missing_output:
            raise SystemExit(f"self-test-missing-file-mismatch:{missing_output}")
        cases += 1

    print("PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST=pass")
    print(f"PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    problems = validate(root)
    if problems:
        print("PHASE8_LIBBPF_SHARD_ROUTES=fail")
        print("PHASE8_LIBBPF_SHARD_ROUTES_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE8_LIBBPF_SHARD_ROUTES_PROBLEMS_END")
        return 1

    print("PHASE8_LIBBPF_SHARD_ROUTES=pass")
    print(f"PHASE8_LIBBPF_SHARD_ROUTES_ROOT={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
