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
HELP_KALLSYMS_BUILD_SHARD_CHECKER = Path("scripts/zigux/check-phase8-help-kallsyms-build-shard.py")
PERF_BUFFER_POLL_GATE_CHECKER = Path("scripts/zigux/check-phase8-perf-buffer-poll-gate.py")
LIBBPF_SHARD_ROUTES_CHECKER = Path("scripts/zigux/check-phase8-libbpf-shard-routes.py")
LIBBPF_SEGMENT_GATE_CHECKER = Path("scripts/zigux/check-phase8-libbpf-segment-gate.py")
EXEC_CMD_PACKET_CHECKER = Path("scripts/zigux/check-phase8-exec-cmd-packet.py")
VALIDATOR = Path("scripts/zigux/validate-phase8.py")
BRIDGE_BOUNDARY_SURVEY = Path("Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md")
LIBBPF_SEGMENT_SURVEY = Path("Documentation/zigux/phase8-libbpf-segment-survey.md")
LIBBPF_SEGMENT_MANIFEST = Path("tools/lib/bpf/zigux_segments/manifest.json")
EXEC_CMD_SLICE = Path("Documentation/zigux/phase8-exec-cmd-slice.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
VERIFY_ROUTING_GAP_TEST = Path("zigux/tests/phase8_verify_routing_gap.zig")
VERIFY_ROUTING_GAP_BUILD = Path("zigux/tests/phase8_verify_routing_gap_only_build.zig")
VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/verify.zig")
CPU_MASK_SEGMENT = Path("tools/lib/bpf/zigux_segments/cpu_mask.zig")
CPU_MASK_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/cpu_mask_verify.zig")
LOGGING_SEGMENT = Path("tools/lib/bpf/zigux_segments/logging.zig")
PERF_BUFFER_POLL_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig")
PERF_BUFFER_WAIT_BUDGET_SEGMENT = Path("tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig")
PERF_BUFFER_READY_WINDOW_SEGMENT = Path("tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig")
READY_BUFFER_FD_LOOKUP_SEGMENT = Path("tools/lib/bpf/zigux_segments/ready_buffer_fd_lookup.zig")
ONLINE_CPU_ROUTING_SEGMENT = Path("tools/lib/bpf/zigux_segments/online_cpu_routing.zig")
ONLINE_CPU_ROUTING_MASK_BRIDGE_SEGMENT = Path("tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge.zig")
ONLINE_CPU_ROUTING_MASK_BRIDGE_VERIFY_SEGMENT = Path(
    "tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge_verify.zig"
)
PIN_PATH_SEGMENT = Path("tools/lib/bpf/zigux_segments/pin_path.zig")
LOGGING_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/logging_verify.zig")
ONLINE_CPU_ROUTING_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig")
PIN_PATH_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/pin_path_verify.zig")
READY_BUFFER_ATTEMPT_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig")
READY_BUFFER_FD_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig")
READY_BUFFER_WINDOW_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig")
TYPE_NAMES_SEGMENT = Path("tools/lib/bpf/zigux_segments/type_names.zig")
TYPE_NAMES_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/type_names_verify.zig")
EXEC_CMD_HELPER = Path("tools/lib/subcmd/exec-cmd.zig")
EXEC_CMD_TEST = Path("zigux/tests/phase8_exec_cmd.zig")
EXEC_CMD_BUILD = Path("zigux/tests/phase8_exec_cmd_only_build.zig")
PERF_BUFFER_POLL_BUILD = Path("zigux/tests/phase8_perf_buffer_poll_only_build.zig")
LIBBPF_SEGMENTS_TEST = Path("zigux/tests/phase8_libbpf_segments.zig")
LIBBPF_SEGMENTS_BUILD = Path("zigux/tests/phase8_libbpf_segments_only_build.zig")
FILE_PATH_HANDLE_BOUNDARY_GUARD_TEST = Path("zigux/tests/phase8_file_path_handle_boundary_guard.zig")
FILE_PATH_HANDLE_BRIDGE_MANIFEST_SYNC_TEST = Path(
    "zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig"
)

REQUIRED_FILES = (
    Path(".github/workflows/zigux-bootstrap.yml"),
    Path("Documentation/zigux/README.md"),
    EXEC_CMD_SLICE,
    BRIDGE_BOUNDARY_SURVEY,
    LIBBPF_SEGMENT_SURVEY,
    LIBBPF_SEGMENT_MANIFEST,
    REVIEW_CHECKLIST,
    Path("scripts/zigux/README.md"),
    TESTS_ALIGNMENT_CHECKER,
    HELP_KALLSYMS_PACKET_CHECKER,
    HELP_KALLSYMS_BUILD_SHARD_CHECKER,
    PERF_BUFFER_POLL_GATE_CHECKER,
    LIBBPF_SHARD_ROUTES_CHECKER,
    LIBBPF_SEGMENT_GATE_CHECKER,
    EXEC_CMD_PACKET_CHECKER,
    VALIDATOR,
    Path("zigux/Makefile"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/phase8_build.zig"),
    EXEC_CMD_HELPER,
    EXEC_CMD_TEST,
    EXEC_CMD_BUILD,
    LIBBPF_SEGMENTS_TEST,
    LIBBPF_SEGMENTS_BUILD,
    Path("zigux/tests/phase8_file_path_handle_bridge.zig"),
    Path("zigux/tests/phase8_file_path_handle_bridge_only_build.zig"),
    FILE_PATH_HANDLE_BOUNDARY_GUARD_TEST,
    FILE_PATH_HANDLE_BRIDGE_MANIFEST_SYNC_TEST,
    Path("zigux/tests/phase8_perf_buffer_poll.zig"),
    PERF_BUFFER_POLL_BUILD,
    VERIFY_ROUTING_GAP_TEST,
    VERIFY_ROUTING_GAP_BUILD,
    Path("tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"),
    Path("tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
    PERF_BUFFER_WAIT_BUDGET_SEGMENT,
    VERIFY_SEGMENT,
    CPU_MASK_SEGMENT,
    CPU_MASK_VERIFY_SEGMENT,
    LOGGING_SEGMENT,
    PERF_BUFFER_POLL_VERIFY_SEGMENT,
    PERF_BUFFER_READY_WINDOW_SEGMENT,
    READY_BUFFER_FD_LOOKUP_SEGMENT,
    ONLINE_CPU_ROUTING_SEGMENT,
    ONLINE_CPU_ROUTING_MASK_BRIDGE_SEGMENT,
    ONLINE_CPU_ROUTING_MASK_BRIDGE_VERIFY_SEGMENT,
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
    EXEC_CMD_SLICE: (
        "phase8-exec-cmd",
        "exec-cmd review packet",
        "buildDeferredExeclCall()",
        "buildDeferredExecvCall()",
        "make -C zigux phase8-validate",
        "kernel/workqueue.c remains a Phase 14 boundary-study target",
        "no retry scheduling, timer-backed backoff, timeout handling, or poll-loop ownership around deferred execution",
        "no queue ownership, wakeup routing, worker-pool control, or scheduler-visible execution substrate",
        "deferred-execution runtime, a broader task queue, or any workqueue-style execution substrate",
    ),
    BRIDGE_BOUNDARY_SURVEY: (
        "`PHASE8_SURVEY=userspace-kernel-bridge-boundary-readback`",
        "The separate Phase 8 command-side anchors under `tools/lib/subcmd/` and `tools/lib/symbol/` keep their own parked packets.",
        "This survey stays limited to the libbpf-side syscall, descriptor, and routing boundary from `tools/lib/bpf/libbpf.c`.",
        "The landed `fdinfo-path-and-reuse-name-footholds` slice therefore now mirrors the manifest rationale exactly: This materializes the shared bridge destination with side-effect-free pathname shaping and bounded reused-map name retention while leaving direct procfs reads, live bpffs opens, token materialization, `bpf_obj_get()` reopen flow, and descriptor ownership side effects to the deferred file-path-and-handle bridge boundary.",
        "The neighboring `fdinfo-map-info-helpers` slice now stays explicit as landed helper-only bridge proof rather than queued groundwork: current helper source already keeps proc-fdinfo pathname shaping, fdinfo line splitting, numeric map-info decoding, and compact completion summaries reviewable without crossing into direct procfs reads, descriptor ownership, or pinned-object reopen flow.",
        "The sibling `map-reuse-compatibility` slice likewise now stays explicit as landed helper-only bridge proof rather than queued groundwork: current helper source already keeps reuse observations, compatibility summaries, and helper-only comparison behavior reviewable without widening into FD duplication, close-on-replacement, or pinned-map reopen side effects.",
        "That broader deferred packet still includes `/sys/devices/system/cpu/online` reads, `libbpf_num_possible_cpus()`, online CPU filtering, per-CPU perf-event-array map updates, per-CPU `perf_event_open()` setup, `mmap()` setup, `PERF_EVENT_IOC_ENABLE` enablement, epoll-backed perf FD registration, and poll waits.",
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
        "Current authenticated helper readback in this runtime now serves only the narrow bridge-side reminder packet directly: the helper set above stays the exact authenticated helper anchor, while the same contents path now returns `tools/lib/bpf/zigux_segments/manifest.json`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, and `Documentation/zigux/phase8-file-path-handle-bridge-slice.md` on current `master`. The broader bridge helper and focused build-route companions, including `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` and `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, remain public-tree-backed reminder vocabulary until the same authenticated contents path serves them directly again. Keep those bridge-facing paths explicit without folding them back into the exact helper set or promoting the deferred resource boundary into helper-first proof.",
        "`tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig` now keeps wait classification, poll summary, execution summary, and impossible-summary fail-closed outputs explicit beside that same stable-output helper packet.",
        "`zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet.",
        "The directly readable verifier packet now also keeps dedicated stable-output witnesses for cpu-mask parse, string-backed summary, reader-backed summary, auto-count, and fail-closed outputs, logging env/version/error outputs, perf-buffer wait-classification, poll-summary, execution-summary, and impossible-summary fail-closed outputs, pin-path map/program output and validation wrappers, online-CPU route CPU-index and buffer-FD wrappers, ready-buffer attempt wrappers, ready-buffer FD wrappers, ready-buffer window mapped-size and lookup-return wrappers, and type-name lookup plus formatter wrappers explicit beside the aggregate `verify.zig` replay surface.",
        "`tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig`",
        "Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/logging_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`, `tools/lib/bpf/zigux_segments/pin_path_verify.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, and `tools/lib/bpf/zigux_segments/type_names_verify.zig` explicit.",
        "standalone timer or clockevent helper behavior",
        "no standalone timer helper behavior",
        "no standalone clockevent helper behavior",
        "broader timeout-sensitive routing behavior",
    ),
    LIBBPF_SEGMENT_MANIFEST: (
        '"lane_key": "P8-L13"',
        '"phase": "Phase 8"',
        '"slug": "fdinfo-map-info-helpers",\n      "status": "starter_landed"',
        '"why_now": "The shared file-path bridge destination already carries the bounded procfs path construction and fdinfo text parsing helpers, so this landed slice should stay explicitly smaller than direct file reads, descriptor ownership, or pinned-object reopen flow."',
        '"slug": "map-reuse-compatibility",\n      "status": "starter_landed"',
        '"why_now": "The shared bridge surface now already carries the reused-map-name chooser and compatibility comparison as landed helper-only behavior, and it should stay reviewable without widening into FD duplication, close-on-replacement, or pinned-map reopen side effects."',
        '"slug": "file-path-and-handle-bridge",\n      "status": "deferred_high_risk",\n      "kind": "resource_boundary"',
        '"slug": "fdinfo-path-and-reuse-name-footholds",\n      "status": "starter_landed"',
        '"why_now": "This materializes the shared bridge destination with side-effect-free pathname shaping and bounded reused-map name retention while leaving direct procfs reads, live bpffs opens, token materialization, `bpf_obj_get()` reopen flow, and descriptor ownership side effects to the deferred file-path-and-handle bridge boundary."',
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
        "scripts/zigux/check-phase8-exec-cmd-packet.py",
        "scripts/zigux/validate-phase8.py",
        "zigux/tests/phase8_perf_buffer_poll.zig",
        "Phase 8 flow - the current userspace-adjacent tooling reminder should keep the direct exec-cmd command packet explicit beside the surviving perf-buffer poll packet and the mixed-source file-path-handle bridge packet, while treating the returned help, kallsyms, and broader libbpf-segment companions as public-tree-backed broader packet evidence instead of as missing routes or direct scripts-root anchors",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/check-phase8-tests-readme-alignment.py`, `scripts/zigux/validate-phase8.py`, `zigux/tests/README.md`, and `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig` keep the directly readable checker, validator, tests-root reminder, helper, and focused perf-buffer packet explicit from the scripts root",
        "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_file_path_handle_boundary_guard.zig`, `zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`, `zigux/tests/phase8_build.zig`, `scripts/zigux/validate-phase8.py`, `make -C zigux phase8-file-path-handle-bridge-test`, `make -C zigux phase8`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the mixed-source file-path-handle bridge packet explicit on current `master` beside the surviving perf-buffer poll route",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "zigux/tests/phase8_file_path_handle_boundary_guard.zig",
        "zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig",
        "tools/lib/symbol/kallsyms.zig",
        "current public-tree rereads plus the shared packet guards `scripts/zigux/check-phase8-help-kallsyms-packet.py` and `scripts/zigux/check-phase8-libbpf-shard-routes.py` rematerialize those broader help, kallsyms, and libbpf-segment companions on `master`",
    ),
    Path("zigux/Makefile"): (
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py",
        "scripts/zigux/check-phase8-libbpf-segment-gate.py",
        "phase8-help-test:",
        "phase8-help-kallsyms-test:",
        "phase8-kallsyms-test:",
        "phase8-libbpf-segments-test:",
        "phase8-file-path-handle-bridge-test:",
        "phase8-perf-buffer-poll-test:",
        "phase8: phase8-validate",
        "phase8-test:",
    ),
    Path("zigux/tests/README.md"): (
        "current direct-readback Phase 8 anchors:",
        "`scripts/zigux/check-phase8-tests-readme-alignment.py`",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`zigux/tests/phase8_perf_buffer_poll.zig`",
        "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`",
        "Keep the currently returned help-and-kallsyms focused packet explicit too; current `master` now rematerializes the dedicated shard files and their route-level companions even though the broader note still treats them as public-tree-backed companion evidence:",
        "`Documentation/zigux/phase8-help-slice.md`",
        "`Documentation/zigux/phase8-kallsyms-slice.md`",
        "`zigux/tests/phase8_help_only_build.zig`",
        "`zigux/tests/phase8_help_kallsyms_only_build.zig`",
        "`zigux/tests/phase8_kallsyms_only_build.zig`",
        "`make -C zigux phase8-help-test`",
        "`make -C zigux phase8-help-kallsyms-test`",
        "`make -C zigux phase8-kallsyms-test`",
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
        "`zigux/tests/phase8_verify_routing_gap.zig`",
        "`zigux/tests/phase8_verify_routing_gap_only_build.zig`",
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
        "../../tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig",
        'perf_buffer_wait_budget_module.addImport("perf_buffer_poll", perf_buffer_poll_module);',
        "phase8-perf-buffer-wait-budget-tests",
        "test_step.dependOn(&run_perf_buffer_wait_budget_tests.step);",
        "../../tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig",
        "../../tools/lib/bpf/zigux_segments/ready_buffer_fd_lookup.zig",
        "phase8-ready-buffer-fd-lookup-tests",
        "test_step.dependOn(&run_ready_buffer_fd_lookup_tests.step);",
        "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "phase8_file_path_handle_bridge.zig",
        "../../tools/lib/bpf/zigux_segments/verify.zig",
        "phase8_libbpf_segments.zig",
        "phase8_verify_routing_gap.zig",
    ),
}

CHECKERS = (
    TESTS_ALIGNMENT_CHECKER,
    HELP_KALLSYMS_PACKET_CHECKER,
    HELP_KALLSYMS_BUILD_SHARD_CHECKER,
    PERF_BUFFER_POLL_GATE_CHECKER,
    LIBBPF_SHARD_ROUTES_CHECKER,
    LIBBPF_SEGMENT_GATE_CHECKER,
    EXEC_CMD_PACKET_CHECKER,
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
    _write(
        root / HELP_KALLSYMS_BUILD_SHARD_CHECKER,
        _passing_checker("PHASE8_HELP_KALLSYMS_BUILD_SHARD"),
    )
    _write(root / PERF_BUFFER_POLL_GATE_CHECKER, _passing_checker("PHASE8_PERF_BUFFER_POLL_GATE"))
    _write(root / LIBBPF_SHARD_ROUTES_CHECKER, _passing_checker("PHASE8_LIBBPF_SHARD_ROUTES"))
    _write(root / LIBBPF_SEGMENT_GATE_CHECKER, _passing_checker("PHASE8_LIBBPF_SEGMENT_GATE"))
    _write(root / EXEC_CMD_PACKET_CHECKER, _passing_checker("PHASE8_EXEC_CMD_PACKET"))


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
            root / TESTS_ALIGNMENT_CHECKER,
            _failing_checker(
                "PHASE8_TESTS_README_ALIGNMENT",
                'missing-marker:zigux/tests/README.md:`scripts/zigux/validate-phase8.py`',
            ),
        )
        failing_tests_alignment_checker = validate_root(root)
        tests_alignment_checker_output = failing_tests_alignment_checker.checker_failures.get(
            TESTS_ALIGNMENT_CHECKER.as_posix()
        )
        if (
            tests_alignment_checker_output is None
            or "PHASE8_TESTS_README_ALIGNMENT=fail" not in tests_alignment_checker_output
            or 'missing-marker:zigux/tests/README.md:`scripts/zigux/validate-phase8.py`'
            not in tests_alignment_checker_output
        ):
            raise AssertionError("expected failing tests-readme alignment checker output to be reported")
        case_count += 1
        _write(
            root / TESTS_ALIGNMENT_CHECKER,
            _passing_checker("PHASE8_TESTS_README_ALIGNMENT"),
        )

        _write(
            root / HELP_KALLSYMS_PACKET_CHECKER,
            _failing_checker(
                "PHASE8_HELP_KALLSYMS_PACKET",
                'missing-marker:Documentation/zigux/phase8-kallsyms-slice.md:`zigux/tests/phase8_kallsyms.zig`',
            ),
        )
        failing_help_kallsyms_checker = validate_root(root)
        help_kallsyms_checker_output = failing_help_kallsyms_checker.checker_failures.get(
            HELP_KALLSYMS_PACKET_CHECKER.as_posix()
        )
        if (
            help_kallsyms_checker_output is None
            or "PHASE8_HELP_KALLSYMS_PACKET=fail" not in help_kallsyms_checker_output
            or 'missing-marker:Documentation/zigux/phase8-kallsyms-slice.md:`zigux/tests/phase8_kallsyms.zig`'
            not in help_kallsyms_checker_output
        ):
            raise AssertionError("expected failing help-kallsyms checker output to be reported")
        case_count += 1
        _write(root / HELP_KALLSYMS_PACKET_CHECKER, _passing_checker("PHASE8_HELP_KALLSYMS_PACKET"))

        _write(
            root / HELP_KALLSYMS_BUILD_SHARD_CHECKER,
            _failing_checker(
                "PHASE8_HELP_KALLSYMS_BUILD_SHARD",
                "missing-marker:zigux/tests/phase8_help_kallsyms_only_build.zig:test_step.dependOn(&run_kallsyms_tests.step);",
            ),
        )
        failing_help_kallsyms_build_shard_checker = validate_root(root)
        help_kallsyms_build_shard_output = failing_help_kallsyms_build_shard_checker.checker_failures.get(
            HELP_KALLSYMS_BUILD_SHARD_CHECKER.as_posix()
        )
        if (
            help_kallsyms_build_shard_output is None
            or "PHASE8_HELP_KALLSYMS_BUILD_SHARD=fail" not in help_kallsyms_build_shard_output
            or "missing-marker:zigux/tests/phase8_help_kallsyms_only_build.zig:test_step.dependOn(&run_kallsyms_tests.step);"
            not in help_kallsyms_build_shard_output
        ):
            raise AssertionError("expected failing help-kallsyms build shard output to be reported")
        case_count += 1
        _write(
            root / HELP_KALLSYMS_BUILD_SHARD_CHECKER,
            _passing_checker("PHASE8_HELP_KALLSYMS_BUILD_SHARD"),
        )

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

        _write(
            root / EXEC_CMD_PACKET_CHECKER,
            _failing_checker(
                "PHASE8_EXEC_CMD_PACKET",
                'missing-marker:Documentation/zigux/phase8-exec-cmd-slice.md:`PHASE8_SLICE=exec-cmd-deferred-exec-packet`',
            ),
        )
        failing_exec_cmd_checker = validate_root(root)
        exec_cmd_checker_output = failing_exec_cmd_checker.checker_failures.get(
            EXEC_CMD_PACKET_CHECKER.as_posix()
        )
        if (
            exec_cmd_checker_output is None
            or "PHASE8_EXEC_CMD_PACKET=fail" not in exec_cmd_checker_output
            or 'missing-marker:Documentation/zigux/phase8-exec-cmd-slice.md:`PHASE8_SLICE=exec-cmd-deferred-exec-packet`'
            not in exec_cmd_checker_output
        ):
            raise AssertionError("expected failing exec_cmd checker output to be reported")
        case_count += 1
        _write(root / EXEC_CMD_PACKET_CHECKER, _passing_checker("PHASE8_EXEC_CMD_PACKET"))

        for relative_path, markers in FILE_MARKERS.items():
            path = root / relative_path
            if not path.exists():
                continue
            original = _read(path)
            for marker in markers:
                path.write_text(original.replace(marker, ""), encoding="utf-8")
                result = validate_root(root)
                expected = f"{relative_path}:{marker}"
                if expected not in result.missing_markers:
                    raise AssertionError(f"expected missing marker to be reported: {expected}")
                path.write_text(original, encoding="utf-8")
                case_count += 1

        for relative_path in REQUIRED_FILES:
            if relative_path in CHECKERS:
                continue
            path = root / relative_path
            original = _read(path)
            path.unlink()
            result = validate_root(root)
            expected = relative_path.as_posix()
            if expected not in result.missing_files:
                raise AssertionError(f"expected missing file to be reported: {expected}")
            _write(path, original)
            case_count += 1

    print("PHASE8_SELF_TEST=pass")
    print(f"PHASE8_SELF_TEST_CASE_COUNT={case_count}")
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
