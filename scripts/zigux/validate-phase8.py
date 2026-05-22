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
LIBBPF_SEGMENT_GATE_CHECKER = Path("scripts/zigux/check-phase8-libbpf-segment-gate.py")
LIBBPF_SEGMENT_SURVEY = Path("Documentation/zigux/phase8-libbpf-segment-survey.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
VERIFY_ROUTING_GAP_TEST = Path("zigux/tests/phase8_verify_routing_gap.zig")
VERIFY_ROUTING_GAP_BUILD = Path("zigux/tests/phase8_verify_routing_gap_only_build.zig")
VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/verify.zig")
CPU_MASK_SEGMENT = Path("tools/lib/bpf/zigux_segments/cpu_mask.zig")
CPU_MASK_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/cpu_mask_verify.zig")
LOGGING_SEGMENT = Path("tools/lib/bpf/zigux_segments/logging.zig")
PERF_BUFFER_POLL_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig")
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
PERF_BUFFER_POLL_BUILD = Path("zigux/tests/phase8_perf_buffer_poll_only_build.zig")
LIBBPF_SEGMENTS_TEST = Path("zigux/tests/phase8_libbpf_segments.zig")
LIBBPF_SEGMENTS_BUILD = Path("zigux/tests/phase8_libbpf_segments_only_build.zig")

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
    LIBBPF_SEGMENT_GATE_CHECKER,
    Path("zigux/Makefile"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/phase8_build.zig"),
    EXEC_CMD_TEST,
    EXEC_CMD_BUILD,
    LIBBPF_SEGMENTS_TEST,
    LIBBPF_SEGMENTS_BUILD,
    Path("zigux/tests/phase8_file_path_handle_bridge.zig"),
    Path("zigux/tests/phase8_file_path_handle_bridge_only_build.zig"),
    Path("zigux/tests/phase8_perf_buffer_poll.zig"),
    PERF_BUFFER_POLL_BUILD,
    VERIFY_ROUTING_GAP_TEST,
    VERIFY_ROUTING_GAP_BUILD,
    Path("tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"),
    Path("tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
    VERIFY_SEGMENT,
    CPU_MASK_SEGMENT,
    CPU_MASK_VERIFY_SEGMENT,
    LOGGING_SEGMENT,
    PERF_BUFFER_POLL_VERIFY_SEGMENT,
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
    Path("Documentation/zigux/phase8-file-path-handle-bridge-slice.md"): (
        "phase8-file-path-handle-bridge",
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
    ),
    Path("Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"): (
        "phase8-userspace-kernel-bridge-boundary",
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
    ),
    LIBBPF_SEGMENT_SURVEY: (
        "Current helper-plus-build packet",
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "`tools/lib/bpf/zigux_segments/type_names.zig`",
        "`tools/lib/bpf/zigux_segments/pin_path.zig`",
        "`tools/lib/bpf/zigux_segments/manifest.json`",
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
        "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig`",
        "`tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig`",
        "`zigux/tests/phase8_build.zig`",
        "`zigux/tests/phase8_verify_routing_gap.zig`",
        "`zigux/tests/phase8_verify_routing_gap_only_build.zig`",
        "Current authenticated tree readback in this runtime is narrower than some older Phase 8 reminder surfaces:",
        "`tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig` now keeps wait classification, poll summary, execution summary, and impossible-summary fail-closed outputs explicit beside that same stable-output helper packet.",
        "`zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet.",
        "The directly readable verifier packet now also keeps dedicated stable-output witnesses for cpu-mask parse, string-backed summary, reader-backed summary, auto-count, and fail-closed outputs, logging env/version/error outputs, perf-buffer wait-classification, poll-summary, execution-summary, and impossible-summary fail-closed outputs, pin-path map/program output and validation wrappers, online-CPU route CPU-index and buffer-FD wrappers, ready-buffer attempt wrappers, ready-buffer FD wrappers, ready-buffer window mapped-size and lookup-return wrappers, and type-name lookup plus formatter wrappers explicit beside the aggregate `verify.zig` replay surface.",
        "`tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig`",
        "Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/logging_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`, `tools/lib/bpf/zigux_segments/pin_path_verify.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, and `tools/lib/bpf/zigux_segments/type_names_verify.zig` explicit.",
        "standalone timer or clockevent helper behavior",
        "broader timeout-sensitive routing behavior",
    ),
    REVIEW_CHECKLIST: (
        "if the change touches the shared Phase 8 userspace-adjacent tooling packet",
        "`make -C zigux phase8-validate`",
        "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context",
        "runtime-substrate or bridge-readiness evidence",
    ),
    Path("scripts/zigux/README.md"): (
        "## Phase 8",
        "scripts/zigux/check-phase8-tests-readme-alignment.py",
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "scripts/zigux/validate-phase8.py",
        "zigux/tests/phase8_perf_buffer_poll.zig",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ),
    Path("zigux/Makefile"): (
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py",
        "scripts/zigux/check-phase8-libbpf-segment-gate.py",
        "phase8-help-kallsyms-test:",
        "phase8-libbpf-segments-test:",
        "phase8-file-path-handle-bridge-test:",
        "phase8-perf-buffer-poll-test:",
        "phase8-test:",
    ),
    Path("zigux/tests/README.md"): (
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
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`zigux/tests/phase8_build.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
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
    Path("zigux/tests/phase8_build.zig"): (
        "../../tools/lib/subcmd/exec-cmd.zig",
        "phase8_exec_cmd.zig",
        "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "phase8_perf_buffer_poll.zig",
        "../../tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig",
        "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "phase8_file_path_handle_bridge.zig",
        "../../tools/lib/bpf/zigux_segments/verify.zig",
        "phase8_libbpf_segments.zig",
        "phase8_verify_routing_gap.zig",
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
        "Run focused Phase 8 exec-cmd tests",
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
    LIBBPF_SEGMENTS_TEST: (
        "test \"phase 8 libbpf-segment compatibility witness keeps the focused verify-routing replay visible\" {",
        "test \"phase 8 libbpf-segment compatibility witness keeps the shared no-timer poll boundary explicit\" {",
        "test \"phase 8 libbpf-segment compatibility witness keeps the mixed-source bridge packet visible\" {",
    ),
    LIBBPF_SEGMENTS_BUILD: (
        "b.path(\"../../tools/lib/bpf/zigux_segments/verify.zig\")",
        "\"phase8-libbpf-segment-verify-tests\"",
        "\"Run focused Phase 8 libbpf segment verify build\"",
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
    PERF_BUFFER_POLL_BUILD: (
        "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "phase8_perf_buffer_poll.zig",
        "phase8-perf-buffer-poll-tests",
        "Run focused Phase 8 perf-buffer poll tests",
    ),
    VERIFY_ROUTING_GAP_TEST: (
        "phase 8 verify routing witness records the current CPU-index verifier closure",
        "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex",
        "materialized tools/lib/bpf Zigux segments keep stable online-CPU route-cpu wrappers explicit",
        "phase 8 verify routing witness records the current direct-readback libbpf survey packet",
    ),
    VERIFY_ROUTING_GAP_BUILD: (
        "phase8_verify_routing_gap.zig",
        "phase8_verify_routing_gap",
        "Run the phase 8 verify routing witness tests.",
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
    ONLINE_CPU_ROUTING_SEGMENT: (
        "pub fn resolveNextOnlineCpuRouteCpuIndex(",
        "pub fn resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(",
        "test \"resolveNextOnlineCpuRouteCpuIndexReturnAtIndex keeps direct errno-shaped route-cpu wrappers aligned\" {",
    ),
    ONLINE_CPU_ROUTING_VERIFY_SEGMENT: (
        "phase8 online-cpu route helpers keep typed cpu-index wrappers stable",
        "resolveNextOnlineCpuRouteCpuIndex",
        "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex",
    ),
    PIN_PATH_SEGMENT: (
        "pub const default_bpf_fs_path = \"/sys/fs/bpf\";",
        "pub fn buildValidatedMapPinPath(",
        "pub fn buildValidatedSanitizedProgramPinPath(",
        "test \"program pin-path helpers mirror the bounded libbpf program pin contract\" {",
    ),
    PIN_PATH_VERIFY_SEGMENT: (
        "phase8 pin-path helper entrypoints stay explicit",
        "buildValidatedSanitizedProgramPinPath",
        "phase8 pin-path helpers keep stable map and program outputs explicit",
    ),
    Path("tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"): (
        "pub const BufferFdLookupDisposition = enum {",
        "pub fn resolveReadyBufferFdAtAttempt(",
        "pub fn resolveReadyBufferFdLookupReturnAtAttempt(",
        "pub fn summarizeBufferWindowLookup(",
        "test \"phase8 perf-buffer poll resolves ready-buffer fd lookups without manual slot plumbing\" {",
    ),
    PERF_BUFFER_POLL_VERIFY_SEGMENT: (
        "phase8 perf-buffer poll helper entrypoints stay explicit",
        "summarizePollExecutionResultFromWaitResult",
        "phase8 perf-buffer poll rejects impossible hand-built summaries and mismatched ready waits",
    ),
    READY_BUFFER_ATTEMPT_VERIFY_SEGMENT: (
        "phase8 ready-buffer attempt helper entrypoints stay explicit",
        "resolveReadyBufferAttemptLookupReturn",
        "phase8 ready-buffer attempt helpers keep errno-shaped outputs stable",
    ),
    READY_BUFFER_FD_VERIFY_SEGMENT: (
        "phase8 ready-buffer fd helper entrypoints stay explicit",
        "resolveReadyBufferFdAtAttempt",
        "resolveReadyBufferFdLookupReturnAtAttempt",
    ),
    READY_BUFFER_WINDOW_VERIFY_SEGMENT: (
        "phase8 ready-buffer window helper entrypoints stay explicit",
        "resolveReadyBufferWindowMappedSizeReturnAtAttempt",
        "resolveReadyBufferWindowLookupReturnAtAttempt",
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
        "resolveReadyBufferWindowMappedSizeReturnAtAttempt",
        "resolveReadyBufferWindowLookupReturnAtAttempt",
        "materialized tools/lib/bpf Zigux segments keep stable libbpf type-name formatters explicit",
        "formatLibbpfBpfLinkType",
    ),
    Path("tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"): (
        "file_path_handle_bridge",
    ),
}

CHECKERS = (
    TESTS_ALIGNMENT_CHECKER,
    HELP_KALLSYMS_PACKET_CHECKER,
    PERF_BUFFER_POLL_GATE_CHECKER,
    LIBBPF_SHARD_ROUTES_CHECKER,
    LIBBPF_SEGMENT_GATE_CHECKER,
)


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
    missing_files = [path.as_posix() for path in REQUIRED_FILES if not (root / path).exists()]
    missing_markers = _collect_missing_markers(root)
    checker_failures: dict[str, list[str]] = {}
    if not missing_files and not missing_markers:
        for checker in CHECKERS:
            output = _run_checker(root, checker)
            if output:
                checker_failures[checker.as_posix()] = output
    return ValidationResult(missing_files, missing_markers, checker_failures)


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
        for checker, lines in result.checker_failures.items():
            print(f"PHASE8_CHECKER_FAILURE_START={checker}")
            for line in lines:
                print(line)
            print(f"PHASE8_CHECKER_FAILURE_END={checker}")
        return 1
    print("PHASE8_VALIDATION=pass")
    print(f"PHASE8_SHARED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE8_MARKER_COUNT={sum(len(markers) for markers in FILE_MARKERS.values())}")
    print(f"PHASE8_CHECKER_COUNT={len(CHECKERS)}")
    return 0


def _passing_fixture(root: Path) -> None:
    for path in REQUIRED_FILES:
        if path in CHECKERS:
            continue
        if path in FILE_MARKERS:
            _write(root / path, "\n".join(FILE_MARKERS[path]) + "\n")
        else:
            _write(root / path, f"{path.as_posix()}\n")
    _write(root / TESTS_ALIGNMENT_CHECKER, _passing_checker("PHASE8_TESTS_README_ALIGNMENT"))
    _write(root / HELP_KALLSYMS_PACKET_CHECKER, _passing_checker("PHASE8_HELP_KALLSYMS_PACKET"))
    _write(root / PERF_BUFFER_POLL_GATE_CHECKER, _passing_checker("PHASE8_PERF_BUFFER_POLL_GATE"))
    _write(root / LIBBPF_SHARD_ROUTES_CHECKER, _passing_checker("PHASE8_LIBBPF_SHARD_ROUTES"))
    _write(root / LIBBPF_SEGMENT_GATE_CHECKER, _passing_checker("PHASE8_LIBBPF_SEGMENT_GATE"))


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase8-validate-selftest-") as tmp:
        root = Path(tmp)
        _passing_fixture(root)

        passing = validate_root(root)
        if passing.missing_files or passing.missing_markers or passing.checker_failures:
            raise AssertionError("expected passing fixture to validate")
        case_count += 1

        _write(
            root / HELP_KALLSYMS_PACKET_CHECKER,
            _failing_checker(
                "PHASE8_HELP_KALLSYMS_PACKET",
                "missing-marker:Documentation/zigux/phase8-kallsyms-slice.md:`zigux/tests/phase8_kallsyms.zig`",
            ),
        )
        failing_help_kallsyms_checker = validate_root(root)
        help_kallsyms_checker_output = failing_help_kallsyms_checker.checker_failures.get(
            HELP_KALLSYMS_PACKET_CHECKER.as_posix()
        )
        if (
            help_kallsyms_checker_output is None
            or "PHASE8_HELP_KALLSYMS_PACKET=fail" not in help_kallsyms_checker_output
            or "missing-marker:Documentation/zigux/phase8-kallsyms-slice.md:`zigux/tests/phase8_kallsyms.zig`"
            not in help_kallsyms_checker_output
        ):
            raise AssertionError("expected failing help-kallsyms checker output to be reported")
        case_count += 1
        _write(root / HELP_KALLSYMS_PACKET_CHECKER, _passing_checker("PHASE8_HELP_KALLSYMS_PACKET"))

        _write(
            root / PERF_BUFFER_POLL_GATE_CHECKER,
            _failing_checker(
                "PHASE8_PERF_BUFFER_POLL_GATE",
                "missing_marker:zigux/tests/phase8_perf_buffer_poll.zig:resolveReadyBufferFdAtAttempt",
            ),
        )
        failing_checker = validate_root(root)
        checker_output = failing_checker.checker_failures.get(PERF_BUFFER_POLL_GATE_CHECKER.as_posix())
        if checker_output is None or "PHASE8_PERF_BUFFER_POLL_GATE=fail" not in checker_output:
            raise AssertionError("expected failing checker output to be reported")
        case_count += 1
        _write(root / PERF_BUFFER_POLL_GATE_CHECKER, _passing_checker("PHASE8_PERF_BUFFER_POLL_GATE"))

        _write(
            root / LIBBPF_SHARD_ROUTES_CHECKER,
            _failing_checker(
                "PHASE8_LIBBPF_SHARD_ROUTES",
                "missing-marker:Documentation/zigux/phase8-libbpf-segment-survey.md:`tools/lib/bpf/zigux_segments/verify.zig`",
            ),
        )
        failing_libbpf_checker = validate_root(root)
        libbpf_checker_output = failing_libbpf_checker.checker_failures.get(
            LIBBPF_SHARD_ROUTES_CHECKER.as_posix()
        )
        if (
            libbpf_checker_output is None
            or "PHASE8_LIBBPF_SHARD_ROUTES=fail" not in libbpf_checker_output
            or "missing-marker:Documentation/zigux/phase8-libbpf-segment-survey.md:`tools/lib/bpf/zigux_segments/verify.zig`" not in libbpf_checker_output
        ):
            raise AssertionError("expected failing libbpf shard-routes checker output to be reported")
        case_count += 1
        _write(root / LIBBPF_SHARD_ROUTES_CHECKER, _passing_checker("PHASE8_LIBBPF_SHARD_ROUTES"))

        _write(
            root / LIBBPF_SEGMENT_GATE_CHECKER,
            _failing_checker(
                "PHASE8_LIBBPF_SEGMENT_GATE",
                "missing-marker:zigux/Makefile:scripts/zigux/check-phase8-libbpf-segment-gate.py",
            ),
        )
        failing_libbpf_segment_gate_checker = validate_root(root)
        libbpf_segment_gate_output = failing_libbpf_segment_gate_checker.checker_failures.get(
            LIBBPF_SEGMENT_GATE_CHECKER.as_posix()
        )
        if (
            libbpf_segment_gate_output is None
            or "PHASE8_LIBBPF_SEGMENT_GATE=fail" not in libbpf_segment_gate_output
            or "missing-marker:zigux/Makefile:scripts/zigux/check-phase8-libbpf-segment-gate.py"
            not in libbpf_segment_gate_output
        ):
            raise AssertionError("expected failing libbpf segment gate output to be reported")
        case_count += 1
        _write(root / LIBBPF_SEGMENT_GATE_CHECKER, _passing_checker("PHASE8_LIBBPF_SEGMENT_GATE"))

        for relative_path, markers in FILE_MARKERS.items():
            original = _read(root / relative_path)
            for marker in markers:
                (root / relative_path).write_text(original.replace(marker, ""), encoding="utf-8")
                result = validate_root(root)
                expected = f"{relative_path}:{marker}"
                if expected not in result.missing_markers:
                    raise AssertionError(f"expected missing marker to be reported: {expected}")
                case_count += 1
                (root / relative_path).write_text(original, encoding="utf-8")

        for relative_path in REQUIRED_FILES:
            original = _read(root / relative_path)
            (root / relative_path).unlink()
            result = validate_root(root)
            expected = relative_path.as_posix()
            if expected not in result.missing_files:
                raise AssertionError(f"expected missing file to be reported: {expected}")
            case_count += 1
            _write(root / relative_path, original)

    print("PHASE8_VALIDATE_SELF_TEST=pass")
    print(f"PHASE8_VALIDATE_SELF_TEST_CASE_COUNT={case_count}")
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
