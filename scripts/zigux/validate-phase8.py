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
HELP_KALLSYMS_PACKET_CHECKER = Path("scripts/zigux/check-phase8-help-kallsyms-packet.py")
PERF_BUFFER_POLL_GATE_CHECKER = Path("scripts/zigux/check-phase8-perf-buffer-poll-gate.py")
LIBBPF_SHARD_ROUTES_CHECKER = Path("scripts/zigux/check-phase8-libbpf-shard-routes.py")
LIBBPF_SEGMENT_SURVEY = Path("Documentation/zigux/phase8-libbpf-segment-survey.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
VERIFY_ROUTING_GAP_TEST = Path("zigux/tests/phase8_verify_routing_gap.zig")
VERIFY_ROUTING_GAP_BUILD = Path("zigux/tests/phase8_verify_routing_gap_only_build.zig")
VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/verify.zig")
CPU_MASK_SEGMENT = Path("tools/lib/bpf/zigux_segments/cpu_mask.zig")
CPU_MASK_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/cpu_mask_verify.zig")
LOGGING_SEGMENT = Path("tools/lib/bpf/zigux_segments/logging.zig")
PERF_BUFFER_READY_WINDOW_SEGMENT = Path("tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig")
ONLINE_CPU_ROUTING_SEGMENT = Path("tools/lib/bpf/zigux_segments/online_cpu_routing.zig")
PIN_PATH_SEGMENT = Path("tools/lib/bpf/zigux_segments/pin_path.zig")
LOGGING_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/logging_verify.zig")
ONLINE_CPU_ROUTING_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig")
PIN_PATH_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/pin_path_verify.zig")
READY_BUFFER_ATTEMPT_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig")
READY_BUFFER_FD_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig")
READY_BUFFER_WINDOW_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig")
TYPE_NAMES_SEGMENT = Path("tools/lib/bpf/zigux_segments/type_names.zig")
TYPE_NAMES_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/type_names_verify.zig")
EXEC_CMD_TEST = Path("zigux/tests/phase8_exec_cmd.zig")
EXEC_CMD_BUILD = Path("zigux/tests/phase8_exec_cmd_only_build.zig")

REQUIRED_FILES = (
    Path(".github/workflows/zigux-bootstrap.yml"),
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/phase8-file-path-handle-bridge-slice.md"),
    Path("Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"),
    LIBBPF_SEGMENT_SURVEY,
    REVIEW_CHECKLIST,
    Path("scripts/zigux/README.md"),
    TESTS_ALIGNMENT_CHECKER,
    HELP_KALLSYMS_PACKET_CHECKER,
    PERF_BUFFER_POLL_GATE_CHECKER,
    LIBBPF_SHARD_ROUTES_CHECKER,
    Path("zigux/Makefile"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/phase8_build.zig"),
    EXEC_CMD_TEST,
    EXEC_CMD_BUILD,
    Path("zigux/tests/phase8_file_path_handle_bridge.zig"),
    Path("zigux/tests/phase8_file_path_handle_bridge_only_build.zig"),
    Path("zigux/tests/phase8_perf_buffer_poll.zig"),
    VERIFY_ROUTING_GAP_TEST,
    VERIFY_ROUTING_GAP_BUILD,
    Path("tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"),
    Path("tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
    VERIFY_SEGMENT,
    CPU_MASK_SEGMENT,
    CPU_MASK_VERIFY_SEGMENT,
    LOGGING_SEGMENT,
    PERF_BUFFER_READY_WINDOW_SEGMENT,
    ONLINE_CPU_ROUTING_SEGMENT,
    PIN_PATH_SEGMENT,
    LOGGING_VERIFY_SEGMENT,
    ONLINE_CPU_ROUTING_VERIFY_SEGMENT,
    PIN_PATH_VERIFY_SEGMENT,
    READY_BUFFER_ATTEMPT_VERIFY_SEGMENT,
    READY_BUFFER_FD_VERIFY_SEGMENT,
    READY_BUFFER_WINDOW_VERIFY_SEGMENT,
    TYPE_NAMES_SEGMENT,
    TYPE_NAMES_VERIFY_SEGMENT,
)

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    Path("zigux/Makefile"): (
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py",
        "phase8-help-kallsyms-test:",
        "phase8-libbpf-segments-test:",
        "phase8-file-path-handle-bridge-test:",
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
        "scripts/zigux/validate-phase8.py",
        "tools/lib/subcmd/exec-cmd.zig",
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
    ),
    REVIEW_CHECKLIST: (
        "if the change touches the shared Phase 8 userspace-adjacent tooling packet",
        "`make -C zigux phase8-validate`",
        "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context",
        "runtime-substrate or bridge-readiness evidence",
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
    LIBBPF_SEGMENT_SURVEY: (
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "`tools/lib/bpf/zigux_segments/cpu_mask_verify.zig`",
        "`tools/lib/bpf/zigux_segments/logging_verify.zig`",
        "`tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig`",
        "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig`",
        "`tools/lib/bpf/zigux_segments/pin_path.zig`",
        "`tools/lib/bpf/zigux_segments/pin_path_verify.zig`",
        "`tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig`",
        "`tools/lib/bpf/zigux_segments/type_names_verify.zig`",
        "The already-readable helper packet is now stable-output backed through `tools/lib/bpf/zigux_segments/verify.zig`",
        "`tools/lib/bpf/zigux_segments/cpu_mask_verify.zig` now keeps direct parse, string-backed summary, reader-backed summary, auto-count, and fail-closed cpu-mask outputs explicit beside that same stable-output helper packet.",
        "Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/logging_verify.zig`, `tools/lib/bpf/zigux_segments/pin_path_verify.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, and `tools/lib/bpf/zigux_segments/type_names_verify.zig` explicit.",
        "standalone timer or clockevent helper behavior",
        "broader timeout-sensitive routing behavior",
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
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`zigux/tests/phase8_perf_buffer_poll.zig`",
        "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`",
        "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`",
        "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`zigux/tests/phase8_build.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "current public-tree rereads now rematerialize the broader help, kallsyms, and libbpf-segment companions on `master`, so treat those returned paths as public-tree-backed broader packet evidence rather than as part of the narrow direct-readback anchor set",
    ),
    EXEC_CMD_TEST: (
        "phase 8 exec-cmd review witness keeps the surviving shared reminder surfaces explicit",
        "scripts/zigux/validate-phase8.py",
        "tools/lib/subcmd/exec-cmd.zig",
        "Run focused Phase 8 exec-cmd tests",
        "expectMissingPath(\"tools/lib/subcmd/exec-cmd.zig\")",
    ),
    EXEC_CMD_BUILD: (
        "phase8_exec_cmd.zig",
        "phase8_exec_cmd",
        "Run the phase 8 exec-cmd review witness tests.",
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
    VERIFY_ROUTING_GAP_TEST: (
        "phase 8 verify routing witness records the current CPU-index verifier closure",
        "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex",
        "materialized tools/lib/bpf Zigux segments keep stable online-CPU route-cpu wrappers explicit",
        "phase 8 verify routing witness records the current direct-readback libbpf survey packet",
    ),
    Path("zigux/tests/phase8_file_path_handle_bridge.zig"): (
        "phase 8 file-path handle bridge",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ),
    Path("zigux/tests/phase8_file_path_handle_bridge_only_build.zig"): (
        "phase8_file_path_handle_bridge.zig",
        "phase8_file_path_handle_bridge",
        "Run the phase 8 file-path-handle bridge tests.",
    ),
    VERIFY_ROUTING_GAP_BUILD: (
        "phase8_verify_routing_gap.zig",
        "phase8_verify_routing_gap",
        "Run the phase 8 verify routing witness tests.",
    ),
    Path("zigux/tests/phase8_build.zig"): (
        "../../tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig",
        "phase8_perf_buffer_poll",
        "phase8_file_path_handle_bridge",
    ),
    CPU_MASK_SEGMENT: (
        "pub fn parseCpuMaskString(",
        "pub fn summarizePossibleCpusFromReader(",
        "pub fn derivePerfBufferAutoCpuCountFromReader(",
    ),
    CPU_MASK_VERIFY_SEGMENT: (
        "phase8 cpu-mask helper entrypoints stay explicit",
        "derivePerfBufferAutoCpuCountFromReader",
        "phase8 cpu-mask helpers keep invalid direct and reader-backed inputs fail-closed",
    ),
    Path("tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"): (
        "pub const BufferFdLookupDisposition = enum {",
        "pub fn resolveReadyBufferFdAtAttempt(",
        "pub fn resolveReadyBufferFdLookupReturnAtAttempt(",
        "pub fn summarizeBufferWindowLookup(",
        "test \"phase8 perf-buffer poll resolves ready-buffer fd lookups without manual slot plumbing\" {",
    ),
    VERIFY_SEGMENT: (
        "const cpu_mask_verify = @import(\"cpu_mask_verify.zig\");",
        "const logging_verify = @import(\"logging_verify.zig\");",
        "const online_cpu_routing_verify = @import(\"online_cpu_routing_verify.zig\");",
        "const pin_path_verify = @import(\"pin_path_verify.zig\");",
        "const ready_buffer_attempt_verify = @import(\"ready_buffer_attempt_verify.zig\");",
        "const ready_buffer_fd_verify = @import(\"ready_buffer_fd_verify.zig\");",
        "const ready_buffer_window_verify = @import(\"ready_buffer_window_verify.zig\");",
        "const type_names_verify = @import(\"type_names_verify.zig\");",
        "std.testing.refAllDecls(cpu_mask_verify);",
        "std.testing.refAllDecls(logging_verify);",
        "std.testing.refAllDecls(online_cpu_routing_verify);",
        "std.testing.refAllDecls(pin_path_verify);",
        "std.testing.refAllDecls(ready_buffer_attempt_verify);",
        "std.testing.refAllDecls(ready_buffer_fd_verify);",
        "std.testing.refAllDecls(ready_buffer_window_verify);",
        "std.testing.refAllDecls(type_names_verify);",
        "materialized tools/lib/bpf Zigux segments keep stable online-CPU route-cpu wrappers explicit",
        "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex",
        "materialized tools/lib/bpf Zigux segments keep stable online-CPU route-fd wrappers explicit",
        "resolveNextOnlineCpuRouteBufferFdReturnAtIndex",
        "materialized tools/lib/bpf Zigux segments keep stable ready-buffer fd wrappers explicit",
        "resolveReadyBufferFdLookupReturnAtAttempt",
        "materialized tools/lib/bpf Zigux segments keep stable ready-buffer window wrappers explicit",
        "resolveReadyBufferWindowLookupReturnAtAttempt",
        "materialized tools/lib/bpf Zigux segments keep stable libbpf type-name formatters explicit",
        "formatLibbpfBpfLinkType",
    ),
    ONLINE_CPU_ROUTING_SEGMENT: (
        "pub fn resolveNextOnlineCpuRouteCpuIndex(",
        "pub fn resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(",
        "test \"resolveNextOnlineCpuRouteCpuIndexReturnAtIndex keeps direct errno-shaped route-cpu wrappers aligned\" {",
    ),
    PIN_PATH_SEGMENT: (
        "pub const default_bpf_fs_path = \"/sys/fs/bpf\";",
        "pub fn buildValidatedMapPinPath(",
        "pub fn buildValidatedSanitizedProgramPinPath(",
        "test \"program pin-path helpers mirror the bounded libbpf program pin contract\" {",
    ),
    LOGGING_SEGMENT: (
        "pub fn parseLogLevelSetting(",
        "pub fn libbpfVersionString(",
        "pub fn formatLibbpfError(",
    ),
    LOGGING_VERIFY_SEGMENT: (
        "phase8 logging helper entrypoints stay explicit",
        "parseLogLevelSetting",
        "formatLibbpfError",
    ),
    ONLINE_CPU_ROUTING_VERIFY_SEGMENT: (
        "phase8 online-cpu routing verifier keeps cpu-index wrappers explicit",
        "resolveNextOnlineCpuRouteCpuIndex",
        "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex",
    ),
    PIN_PATH_VERIFY_SEGMENT: (
        "phase8 pin-path helper entrypoints stay explicit",
        "buildValidatedSanitizedProgramPinPath",
        "phase8 pin-path helpers keep stable map and program outputs explicit",
    ),
    READY_BUFFER_ATTEMPT_VERIFY_SEGMENT: (
        "phase8 ready-buffer attempt helper entrypoints stay explicit",
        "resolveReadyBufferAttemptLookupReturn",
        "phase8 ready-buffer attempt helpers keep errno-shaped outputs stable",
    ),
    READY_BUFFER_FD_VERIFY_SEGMENT: (
        "phase8 ready-buffer fd verifier keeps lookup-return wrappers explicit",
        "resolveReadyBufferFdAtAttempt",
        "resolveReadyBufferFdLookupReturnAtAttempt",
    ),
    READY_BUFFER_WINDOW_VERIFY_SEGMENT: (
        "phase8 ready-buffer window verifier keeps mapped-size and lookup-return wrappers explicit",
        "summarizeBufferWindowMappedSize",
        "summarizeBufferWindowLookupReturn",
    ),
    TYPE_NAMES_SEGMENT: (
        "pub fn libbpfBpfMapTypeStr(",
        "pub fn libbpfBpfAttachTypeStr(",
        "pub fn formatLibbpfBpfProgType(",
    ),
    TYPE_NAMES_VERIFY_SEGMENT: (
        "phase8 libbpf type-name helper entrypoints stay explicit",
        "libbpfBpfMapTypeStr",
        "formatLibbpfBpfProgType",
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
        for checker in (
            TESTS_ALIGNMENT_CHECKER,
            HELP_KALLSYMS_PACKET_CHECKER,
            PERF_BUFFER_POLL_GATE_CHECKER,
            LIBBPF_SHARD_ROUTES_CHECKER,
        ):
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
    print("PHASE8_CHECKER_COUNT=4")
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
    _write(root / HELP_KALLSYMS_PACKET_CHECKER, _passing_checker("PHASE8_HELP_KALLSYMS_PACKET"))
    _write(root / PERF_BUFFER_POLL_GATE_CHECKER, _passing_checker("PHASE8_PERF_BUFFER_POLL_GATE"))
    _write(root / LIBBPF_SHARD_ROUTES_CHECKER, _passing_checker("PHASE8_LIBBPF_SHARD_ROUTES"))
    _write(root / PERF_BUFFER_READY_WINDOW_SEGMENT, "pub fn placeholder() void {}\n")
    for helper in (
        CPU_MASK_VERIFY_SEGMENT,
        LOGGING_VERIFY_SEGMENT,
        ONLINE_CPU_ROUTING_VERIFY_SEGMENT,
        PIN_PATH_VERIFY_SEGMENT,
        READY_BUFFER_ATTEMPT_VERIFY_SEGMENT,
        READY_BUFFER_FD_VERIFY_SEGMENT,
        READY_BUFFER_WINDOW_VERIFY_SEGMENT,
        TYPE_NAMES_VERIFY_SEGMENT,
    ):
        _write(root / helper, "\n".join(FILE_MARKERS[helper]) + "\n")


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

        help_kallsyms_checker = root / HELP_KALLSYMS_PACKET_CHECKER
        _write(
            help_kallsyms_checker,
            _failing_checker(
                "PHASE8_HELP_KALLSYMS_PACKET",
                "missing_marker:zigux/tests/phase8_help_kallsyms_only_build.zig:phase8_kallsyms.zig",
            ),
        )
        failing_help_kallsyms_checker = validate_root(root)
        help_kallsyms_output = failing_help_kallsyms_checker.checker_failures.get(
            HELP_KALLSYMS_PACKET_CHECKER.as_posix()
        )
        if not help_kallsyms_output or "phase8_kallsyms.zig" not in "\n".join(help_kallsyms_output):
            raise AssertionError("expected help+kallsyms checker failure output to be reported")
        _write(help_kallsyms_checker, _passing_checker("PHASE8_HELP_KALLSYMS_PACKET"))

        makefile = root / "zigux/Makefile"
        original_makefile = _read(makefile)
        makefile.write_text(
            original_makefile.replace("phase8-help-kallsyms-test:\n", "", 1),
            encoding="utf-8",
        )
        missing_shared_route_marker = validate_root(root)
        expected_shared_route_marker = "zigux/Makefile:phase8-help-kallsyms-test:"
        if expected_shared_route_marker not in missing_shared_route_marker.missing_markers:
            raise AssertionError("expected missing shared help+kallsyms make marker to be reported")
        makefile.write_text(original_makefile, encoding="utf-8")

        makefile.write_text(
            original_makefile.replace("phase8-perf-buffer-poll-test:\n", "", 1),
            encoding="utf-8",
        )
        missing_make_marker = validate_root(root)
        expected_make_marker = "zigux/Makefile:phase8-perf-buffer-poll-test:"
        if expected_make_marker not in missing_make_marker.missing_markers:
            raise AssertionError("expected missing Makefile Phase 8 marker to be reported")
        makefile.write_text(original_makefile, encoding="utf-8")

        checklist = root / REVIEW_CHECKLIST
        original_checklist = _read(checklist)
        shared_phase8_marker = "if the change touches the shared Phase 8 userspace-adjacent tooling packet"
        checklist.write_text(
            original_checklist.replace(shared_phase8_marker, "", 1),
            encoding="utf-8",
        )
        missing_checklist_marker = validate_root(root)
        expected_checklist_marker = f"{REVIEW_CHECKLIST}:{shared_phase8_marker}"
        if expected_checklist_marker not in missing_checklist_marker.missing_markers:
            raise AssertionError("expected missing checklist Phase 8 marker to be reported")
        checklist.write_text(original_checklist, encoding="utf-8")

        workqueue_boundary_marker = "runtime-substrate or bridge-readiness evidence"
        checklist.write_text(
            original_checklist.replace(workqueue_boundary_marker, "", 1),
            encoding="utf-8",
        )
        missing_workqueue_boundary_marker = validate_root(root)
        expected_workqueue_boundary_marker = f"{REVIEW_CHECKLIST}:{workqueue_boundary_marker}"
        if expected_workqueue_boundary_marker not in missing_workqueue_boundary_marker.missing_markers:
            raise AssertionError("expected missing workqueue study-boundary marker to be reported")
        checklist.write_text(original_checklist, encoding="utf-8")

        exec_cmd_test = root / EXEC_CMD_TEST
        exec_cmd_test.unlink()
        missing_exec_cmd = validate_root(root)
        if EXEC_CMD_TEST.as_posix() not in missing_exec_cmd.missing_files:
            raise AssertionError("expected missing exec-cmd witness file to be reported")
        _write(exec_cmd_test, "\n".join(FILE_MARKERS[EXEC_CMD_TEST]) + "\n")

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

        survey = root / LIBBPF_SEGMENT_SURVEY
        original_survey = _read(survey)
        unique_survey_marker = (
            "Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/logging_verify.zig`, `tools/lib/bpf/zigux_segments/pin_path_verify.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, and `tools/lib/bpf/zigux_segments/type_names_verify.zig` explicit."
        )
        survey.write_text(
            original_survey.replace(unique_survey_marker, "", 1),
            encoding="utf-8",
        )
        missing_survey_marker = validate_root(root)
        expected_survey_marker = (
            "Documentation/zigux/phase8-libbpf-segment-survey.md:" + unique_survey_marker
        )
        if expected_survey_marker not in missing_survey_marker.missing_markers:
            raise AssertionError("expected missing survey routing marker to be reported")
        survey.write_text(original_survey, encoding="utf-8")

        timer_boundary_marker = "standalone timer or clockevent helper behavior"
        survey.write_text(
            original_survey.replace(timer_boundary_marker, "", 1),
            encoding="utf-8",
        )
        missing_timer_boundary_marker = validate_root(root)
        expected_timer_boundary_marker = (
            "Documentation/zigux/phase8-libbpf-segment-survey.md:" + timer_boundary_marker
        )
        if expected_timer_boundary_marker not in missing_timer_boundary_marker.missing_markers:
            raise AssertionError("expected missing timer/clockevent survey marker to be reported")
        survey.write_text(original_survey, encoding="utf-8")

        cpu_mask_verify_survey_marker = (
            "`tools/lib/bpf/zigux_segments/cpu_mask_verify.zig` now keeps direct parse, string-backed summary, reader-backed summary, auto-count, and fail-closed cpu-mask outputs explicit beside that same stable-output helper packet."
        )
        survey.write_text(
            original_survey.replace(cpu_mask_verify_survey_marker, "", 1),
            encoding="utf-8",
        )
        missing_cpu_mask_verify_survey_marker = validate_root(root)
        expected_cpu_mask_verify_survey_marker = (
            "Documentation/zigux/phase8-libbpf-segment-survey.md:" + cpu_mask_verify_survey_marker
        )
        if expected_cpu_mask_verify_survey_marker not in missing_cpu_mask_verify_survey_marker.missing_markers:
            raise AssertionError("expected missing cpu-mask verify survey marker to be reported")
        survey.write_text(original_survey, encoding="utf-8")

        build_file = root / "zigux/tests/phase8_build.zig"
        original_build_file = _read(build_file)
        build_file.write_text(
            original_build_file.replace("../../tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig", "", 1),
            encoding="utf-8",
        )
        missing_ready_window_marker = validate_root(root)
        expected_ready_window_marker = (
            "zigux/tests/phase8_build.zig:../../tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig"
        )
        if expected_ready_window_marker not in missing_ready_window_marker.missing_markers:
            raise AssertionError("expected missing ready-buffer window build marker to be reported")
        build_file.write_text(original_build_file, encoding="utf-8")

        verify_file = root / VERIFY_SEGMENT
        original_verify_file = _read(verify_file)
        verify_file.write_text(
            original_verify_file.replace('const cpu_mask_verify = @import("cpu_mask_verify.zig");\n', "", 1),
            encoding="utf-8",
        )
        missing_verify_import = validate_root(root)
        expected_verify_import = 'tools/lib/bpf/zigux_segments/verify.zig:const cpu_mask_verify = @import("cpu_mask_verify.zig");'
        if expected_verify_import not in missing_verify_import.missing_markers:
            raise AssertionError("expected missing aggregate verifier cpu-mask import to be reported")
        verify_file.write_text(original_verify_file, encoding="utf-8")

        verify_file.write_text(
            original_verify_file.replace("std.testing.refAllDecls(ready_buffer_window_verify);", "", 1),
            encoding="utf-8",
        )
        missing_verify_refalldecls = validate_root(root)
        expected_verify_refalldecls = "tools/lib/bpf/zigux_segments/verify.zig:std.testing.refAllDecls(ready_buffer_window_verify);"
        if expected_verify_refalldecls not in missing_verify_refalldecls.missing_markers:
            raise AssertionError("expected missing aggregate verifier ready-buffer-window refAllDecls marker to be reported")
        verify_file.write_text(original_verify_file, encoding="utf-8")

        verify_file.write_text(
            original_verify_file.replace("resolveNextOnlineCpuRouteBufferFdReturnAtIndex", "", 1),
            encoding="utf-8",
        )
        missing_route_fd_wrapper = validate_root(root)
        expected_route_fd_wrapper = "tools/lib/bpf/zigux_segments/verify.zig:resolveNextOnlineCpuRouteBufferFdReturnAtIndex"
        if expected_route_fd_wrapper not in missing_route_fd_wrapper.missing_markers:
            raise AssertionError("expected missing aggregate verifier route-fd wrapper marker to be reported")
        verify_file.write_text(original_verify_file, encoding="utf-8")

        verify_file.write_text(
            original_verify_file.replace("resolveReadyBufferFdLookupReturnAtAttempt", "", 1),
            encoding="utf-8",
        )
        missing_ready_buffer_fd_wrapper = validate_root(root)
        expected_ready_buffer_fd_wrapper = "tools/lib/bpf/zigux_segments/verify.zig:resolveReadyBufferFdLookupReturnAtAttempt"
        if expected_ready_buffer_fd_wrapper not in missing_ready_buffer_fd_wrapper.missing_markers:
            raise AssertionError("expected missing aggregate verifier ready-buffer fd wrapper marker to be reported")
        verify_file.write_text(original_verify_file, encoding="utf-8")

        verify_file.write_text(
            original_verify_file.replace("resolveReadyBufferWindowLookupReturnAtAttempt", "", 1),
            encoding="utf-8",
        )
        missing_ready_buffer_window_wrapper = validate_root(root)
        expected_ready_buffer_window_wrapper = "tools/lib/bpf/zigux_segments/verify.zig:resolveReadyBufferWindowLookupReturnAtAttempt"
        if expected_ready_buffer_window_wrapper not in missing_ready_buffer_window_wrapper.missing_markers:
            raise AssertionError("expected missing aggregate verifier ready-buffer window wrapper marker to be reported")
        verify_file.write_text(original_verify_file, encoding="utf-8")

        verify_file.write_text(
            original_verify_file.replace("formatLibbpfBpfLinkType", "", 1),
            encoding="utf-8",
        )
        missing_type_formatter = validate_root(root)
        expected_type_formatter = "tools/lib/bpf/zigux_segments/verify.zig:formatLibbpfBpfLinkType"
        if expected_type_formatter not in missing_type_formatter.missing_markers:
            raise AssertionError("expected missing aggregate verifier type-name formatter marker to be reported")
        verify_file.write_text(original_verify_file, encoding="utf-8")

        logging_verify = root / LOGGING_VERIFY_SEGMENT
        logging_verify.unlink()
        missing_logging_verify = validate_root(root)
        if LOGGING_VERIFY_SEGMENT.as_posix() not in missing_logging_verify.missing_files:
            raise AssertionError("expected missing logging verify file to be reported")
        _write(logging_verify, "\n".join(FILE_MARKERS[LOGGING_VERIFY_SEGMENT]) + "\n")

        online_cpu_verify = root / ONLINE_CPU_ROUTING_VERIFY_SEGMENT
        online_cpu_verify.unlink()
        missing_online_cpu_verify = validate_root(root)
        if ONLINE_CPU_ROUTING_VERIFY_SEGMENT.as_posix() not in missing_online_cpu_verify.missing_files:
            raise AssertionError("expected missing online-cpu routing verify file to be reported")
        _write(online_cpu_verify, "\n".join(FILE_MARKERS[ONLINE_CPU_ROUTING_VERIFY_SEGMENT]) + "\n")

        pin_path_verify = root / PIN_PATH_VERIFY_SEGMENT
        pin_path_verify.unlink()
        missing_pin_path_verify = validate_root(root)
        if PIN_PATH_VERIFY_SEGMENT.as_posix() not in missing_pin_path_verify.missing_files:
            raise AssertionError("expected missing pin-path verify file to be reported")
        _write(pin_path_verify, "\n".join(FILE_MARKERS[PIN_PATH_VERIFY_SEGMENT]) + "\n")

        ready_buffer_attempt_verify = root / READY_BUFFER_ATTEMPT_VERIFY_SEGMENT
        ready_buffer_attempt_verify.unlink()
        missing_ready_buffer_attempt_verify = validate_root(root)
        if READY_BUFFER_ATTEMPT_VERIFY_SEGMENT.as_posix() not in missing_ready_buffer_attempt_verify.missing_files:
            raise AssertionError("expected missing ready-buffer attempt verify file to be reported")
        _write(ready_buffer_attempt_verify, "\n".join(FILE_MARKERS[READY_BUFFER_ATTEMPT_VERIFY_SEGMENT]) + "\n")

        ready_buffer_fd_verify = root / READY_BUFFER_FD_VERIFY_SEGMENT
        ready_buffer_fd_verify.unlink()
        missing_ready_buffer_fd_verify = validate_root(root)
        if READY_BUFFER_FD_VERIFY_SEGMENT.as_posix() not in missing_ready_buffer_fd_verify.missing_files:
            raise AssertionError("expected missing ready-buffer fd verify file to be reported")
        _write(ready_buffer_fd_verify, "\n".join(FILE_MARKERS[READY_BUFFER_FD_VERIFY_SEGMENT]) + "\n")

        ready_buffer_window_verify = root / READY_BUFFER_WINDOW_VERIFY_SEGMENT
        ready_buffer_window_verify.unlink()
        missing_ready_buffer_window_verify = validate_root(root)
        if READY_BUFFER_WINDOW_VERIFY_SEGMENT.as_posix() not in missing_ready_buffer_window_verify.missing_files:
            raise AssertionError("expected missing ready-buffer window verify file to be reported")
        _write(ready_buffer_window_verify, "\n".join(FILE_MARKERS[READY_BUFFER_WINDOW_VERIFY_SEGMENT]) + "\n")

        type_names_verify = root / TYPE_NAMES_VERIFY_SEGMENT
        type_names_verify.unlink()
        missing_type_names_verify = validate_root(root)
        if TYPE_NAMES_VERIFY_SEGMENT.as_posix() not in missing_type_names_verify.missing_files:
            raise AssertionError("expected missing type-name verify file to be reported")
        _write(type_names_verify, "\n".join(FILE_MARKERS[TYPE_NAMES_VERIFY_SEGMENT]) + "\n")

        missing_helper = root / "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"
        missing_helper.unlink()
        missing_perf_helper = validate_root(root)
        if "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig" not in missing_perf_helper.missing_files:
            raise AssertionError("expected missing perf-buffer helper file to be reported")
        _write(missing_helper, "\n".join(FILE_MARKERS[Path("tools/lib/bpf/zigux_segments/perf_buffer_poll.zig")]) + "\n")

        cpu_mask_helper = root / CPU_MASK_SEGMENT
        cpu_mask_helper.unlink()
        missing_cpu_mask_helper = validate_root(root)
        if CPU_MASK_SEGMENT.as_posix() not in missing_cpu_mask_helper.missing_files:
            raise AssertionError("expected missing cpu-mask helper file to be reported")
        _write(cpu_mask_helper, "\n".join(FILE_MARKERS[CPU_MASK_SEGMENT]) + "\n")

        cpu_mask_verify = root / CPU_MASK_VERIFY_SEGMENT
        cpu_mask_verify.unlink()
        missing_cpu_mask_verify = validate_root(root)
        if CPU_MASK_VERIFY_SEGMENT.as_posix() not in missing_cpu_mask_verify.missing_files:
            raise AssertionError("expected missing cpu-mask verify file to be reported")
        _write(cpu_mask_verify, "\n".join(FILE_MARKERS[CPU_MASK_VERIFY_SEGMENT]) + "\n")

        logging_helper = root / LOGGING_SEGMENT
        logging_helper.unlink()
        missing_logging_helper = validate_root(root)
        if LOGGING_SEGMENT.as_posix() not in missing_logging_helper.missing_files:
            raise AssertionError("expected missing logging helper file to be reported")
        _write(logging_helper, "\n".join(FILE_MARKERS[LOGGING_SEGMENT]) + "\n")

        pin_path_helper = root / PIN_PATH_SEGMENT
        pin_path_helper.unlink()
        missing_pin_path_helper = validate_root(root)
        if PIN_PATH_SEGMENT.as_posix() not in missing_pin_path_helper.missing_files:
            raise AssertionError("expected missing pin-path helper file to be reported")
        _write(pin_path_helper, "\n".join(FILE_MARKERS[PIN_PATH_SEGMENT]) + "\n")

        missing_bridge_build = root / "zigux/tests/phase8_file_path_handle_bridge_only_build.zig"
        missing_bridge_build.unlink()
        missing_build = validate_root(root)
        if "zigux/tests/phase8_file_path_handle_bridge_only_build.zig" not in missing_build.missing_files:
            raise AssertionError("expected missing bridge build shard to be reported")
        _write(
            missing_bridge_build,
            "\n".join(FILE_MARKERS[Path("zigux/tests/phase8_file_path_handle_bridge_only_build.zig")]) + "\n",
        )

        verify_build = root / VERIFY_ROUTING_GAP_BUILD
        verify_build.unlink()
        missing_verify_build = validate_root(root)
        if VERIFY_ROUTING_GAP_BUILD.as_posix() not in missing_verify_build.missing_files:
            raise AssertionError("expected missing verify-routing build shard to be reported")
        _write(verify_build, "\n".join(FILE_MARKERS[VERIFY_ROUTING_GAP_BUILD]) + "\n")

        help_kallsyms_checker = root / HELP_KALLSYMS_PACKET_CHECKER
        help_kallsyms_checker.unlink()
        missing_help_kallsyms_checker = validate_root(root)
        if HELP_KALLSYMS_PACKET_CHECKER.as_posix() not in missing_help_kallsyms_checker.missing_files:
            raise AssertionError("expected missing help+kallsyms checker file to be reported")
        _write(help_kallsyms_checker, _passing_checker("PHASE8_HELP_KALLSYMS_PACKET"))

        type_names_helper = root / TYPE_NAMES_SEGMENT
        type_names_helper.unlink()
        missing_type_names_helper = validate_root(root)
        if TYPE_NAMES_SEGMENT.as_posix() not in missing_type_names_helper.missing_files:
            raise AssertionError("expected missing type-names helper file to be reported")
        _write(type_names_helper, "\n".join(FILE_MARKERS[TYPE_NAMES_SEGMENT]) + "\n")

        online_cpu_routing = root / ONLINE_CPU_ROUTING_SEGMENT
        online_cpu_routing.unlink()
        missing_online_cpu_routing = validate_root(root)
        if ONLINE_CPU_ROUTING_SEGMENT.as_posix() not in missing_online_cpu_routing.missing_files:
            raise AssertionError("expected missing online-cpu routing helper file to be reported")
        _write(online_cpu_routing, "\n".join(FILE_MARKERS[ONLINE_CPU_ROUTING_SEGMENT]) + "\n")

    print("PHASE8_VALIDATE_SELF_TEST=pass")
    print("PHASE8_VALIDATE_SELF_TEST_CASE_COUNT=34")
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
