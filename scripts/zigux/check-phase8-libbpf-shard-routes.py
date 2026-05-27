#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase8-libbpf-shard-routes.py"
VALIDATOR_PATH = "scripts/zigux/validate-phase8.py"
SURVEY_PATH = "Documentation/zigux/phase8-libbpf-segment-survey.md"
BRIDGE_BOUNDARY_SURVEY_PATH = "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"
BRIDGE_SLICE_PATH = "Documentation/zigux/phase8-file-path-handle-bridge-slice.md"
MAKEFILE_PATH = "zigux/Makefile"
BRIDGE_TEST_PATH = "zigux/tests/phase8_file_path_handle_bridge.zig"
BRIDGE_BOUNDARY_GUARD_TEST_PATH = "zigux/tests/phase8_file_path_handle_boundary_guard.zig"
BRIDGE_MANIFEST_SYNC_TEST_PATH = "zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig"
MANIFEST_PATH = "tools/lib/bpf/zigux_segments/manifest.json"
PHASE8_BUILD_PATH = "zigux/tests/phase8_build.zig"
VERIFY_ROUTING_GAP_TEST_PATH = "zigux/tests/phase8_verify_routing_gap.zig"
VERIFY_ROUTING_GAP_BUILD_PATH = "zigux/tests/phase8_verify_routing_gap_only_build.zig"
LIBBPF_SEGMENTS_TEST_PATH = "zigux/tests/phase8_libbpf_segments.zig"
LIBBPF_SEGMENTS_BUILD_PATH = "zigux/tests/phase8_libbpf_segments_only_build.zig"
VERIFY_PATH = "tools/lib/bpf/zigux_segments/verify.zig"
CPU_MASK_PATH = "tools/lib/bpf/zigux_segments/cpu_mask.zig"
CPU_MASK_VERIFY_PATH = "tools/lib/bpf/zigux_segments/cpu_mask_verify.zig"
FILE_PATH_HANDLE_BRIDGE_VERIFY_PATH = "tools/lib/bpf/zigux_segments/file_path_handle_bridge_verify.zig"
LOGGING_PATH = "tools/lib/bpf/zigux_segments/logging.zig"
LOGGING_VERIFY_PATH = "tools/lib/bpf/zigux_segments/logging_verify.zig"
ONLINE_CPU_ROUTING_PATH = "tools/lib/bpf/zigux_segments/online_cpu_routing.zig"
ONLINE_CPU_ROUTING_MASK_BRIDGE_PATH = "tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge.zig"
ONLINE_CPU_ROUTING_MASK_BRIDGE_VERIFY_PATH = "tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge_verify.zig"
ONLINE_CPU_ROUTING_VERIFY_PATH = "tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig"
PERF_BUFFER_POLL_PATH = "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"
PERF_BUFFER_POLL_VERIFY_PATH = "tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig"
PERF_BUFFER_WAIT_BUDGET_PATH = "tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig"
PERF_BUFFER_READY_WINDOW_PATH = "tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig"
PIN_PATH_PATH = "tools/lib/bpf/zigux_segments/pin_path.zig"
PIN_PATH_VERIFY_PATH = "tools/lib/bpf/zigux_segments/pin_path_verify.zig"
READY_BUFFER_ATTEMPT_VERIFY_PATH = "tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig"
READY_BUFFER_FD_LOOKUP_PATH = "tools/lib/bpf/zigux_segments/ready_buffer_fd_lookup.zig"
READY_BUFFER_FD_VERIFY_PATH = "tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig"
READY_BUFFER_WINDOW_VERIFY_PATH = "tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig"
TYPE_NAMES_PATH = "tools/lib/bpf/zigux_segments/type_names.zig"
TYPE_NAMES_VERIFY_PATH = "tools/lib/bpf/zigux_segments/type_names_verify.zig"

REQUIRED_FILES = (
    SCRIPT_PATH,
    VALIDATOR_PATH,
    SURVEY_PATH,
    BRIDGE_BOUNDARY_SURVEY_PATH,
    BRIDGE_SLICE_PATH,
    MAKEFILE_PATH,
    BRIDGE_TEST_PATH,
    BRIDGE_BOUNDARY_GUARD_TEST_PATH,
    BRIDGE_MANIFEST_SYNC_TEST_PATH,
    MANIFEST_PATH,
    PHASE8_BUILD_PATH,
    VERIFY_ROUTING_GAP_TEST_PATH,
    VERIFY_ROUTING_GAP_BUILD_PATH,
    LIBBPF_SEGMENTS_TEST_PATH,
    LIBBPF_SEGMENTS_BUILD_PATH,
    VERIFY_PATH,
    CPU_MASK_PATH,
    CPU_MASK_VERIFY_PATH,
    FILE_PATH_HANDLE_BRIDGE_VERIFY_PATH,
    LOGGING_PATH,
    LOGGING_VERIFY_PATH,
    ONLINE_CPU_ROUTING_PATH,
    ONLINE_CPU_ROUTING_MASK_BRIDGE_PATH,
    ONLINE_CPU_ROUTING_MASK_BRIDGE_VERIFY_PATH,
    ONLINE_CPU_ROUTING_VERIFY_PATH,
    PERF_BUFFER_POLL_PATH,
    PERF_BUFFER_POLL_VERIFY_PATH,
    PERF_BUFFER_WAIT_BUDGET_PATH,
    PERF_BUFFER_READY_WINDOW_PATH,
    PIN_PATH_PATH,
    PIN_PATH_VERIFY_PATH,
    READY_BUFFER_ATTEMPT_VERIFY_PATH,
    READY_BUFFER_FD_LOOKUP_PATH,
    READY_BUFFER_FD_VERIFY_PATH,
    READY_BUFFER_WINDOW_VERIFY_PATH,
    TYPE_NAMES_PATH,
    TYPE_NAMES_VERIFY_PATH,
)

REQUIRED_MARKERS = {
    VALIDATOR_PATH: (
        'LIBBPF_SHARD_ROUTES_CHECKER = Path("scripts/zigux/check-phase8-libbpf-shard-routes.py")',
        "LIBBPF_SHARD_ROUTES_CHECKER,",
        'CPU_MASK_SEGMENT = Path("tools/lib/bpf/zigux_segments/cpu_mask.zig")',
        'CPU_MASK_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/cpu_mask_verify.zig")',
        'LOGGING_SEGMENT = Path("tools/lib/bpf/zigux_segments/logging.zig")',
        'LOGGING_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/logging_verify.zig")',
        'ONLINE_CPU_ROUTING_SEGMENT = Path("tools/lib/bpf/zigux_segments/online_cpu_routing.zig")',
        'ONLINE_CPU_ROUTING_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig")',
        'PERF_BUFFER_POLL_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig")',
        'PERF_BUFFER_WAIT_BUDGET_SEGMENT = Path("tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig")',
        'PERF_BUFFER_READY_WINDOW_SEGMENT = Path("tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig")',
        'PIN_PATH_SEGMENT = Path("tools/lib/bpf/zigux_segments/pin_path.zig")',
        'PIN_PATH_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/pin_path_verify.zig")',
        'READY_BUFFER_ATTEMPT_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig")',
        'READY_BUFFER_FD_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig")',
        'READY_BUFFER_WINDOW_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig")',
        'TYPE_NAMES_SEGMENT = Path("tools/lib/bpf/zigux_segments/type_names.zig")',
        'TYPE_NAMES_VERIFY_SEGMENT = Path("tools/lib/bpf/zigux_segments/type_names_verify.zig")',
    ),
    SURVEY_PATH: (
        "Current helper-plus-build packet",
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "`tools/lib/bpf/zigux_segments/cpu_mask.zig`",
        "`tools/lib/bpf/zigux_segments/cpu_mask_verify.zig`",
        "`tools/lib/bpf/zigux_segments/logging.zig`",
        "`tools/lib/bpf/zigux_segments/logging_verify.zig`",
        "`tools/lib/bpf/zigux_segments/type_names.zig`",
        "`tools/lib/bpf/zigux_segments/type_names_verify.zig`",
        "`tools/lib/bpf/zigux_segments/pin_path.zig`",
        "`tools/lib/bpf/zigux_segments/pin_path_verify.zig`",
        "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`",
        "`tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig`",
        "`tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`",
        "`tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig`",
        "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig`",
        "`tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig`",
        "bounded wait-budget normalization",
        "`zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet.",
        "`zigux/tests/phase8_libbpf_segments.zig` plus `zigux/tests/phase8_libbpf_segments_only_build.zig` now keep the shared stable-output verifier, mixed-source bridge, focused verify-routing, and no-timer poll-boundary packet explicit from the tests root beside that same helper-first shard packet.",
        "Current authenticated contents readback in this runtime now reaches the mixed-source bridge reminder packet more directly: the stable-output helper set above stays the exact authenticated helper anchor, while the same contents path now also serves `tools/lib/bpf/zigux_segments/manifest.json`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and `zigux/tests/phase8_file_path_handle_bridge.zig` on current `master`.",
        "The focused bridge-only build and broader replay companions, including `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, remain reminder vocabulary outside the exact stable-output helper set. Keep those bridge-facing paths explicit without folding them back into the exact helper set or promoting the deferred resource boundary into helper-first proof.",
        "`zigux/tests/phase8_verify_routing_gap.zig` plus `zigux/tests/phase8_verify_routing_gap_only_build.zig`",
        "make -C zigux phase8-perf-buffer-poll-test",
        "`tools/lib/bpf/zigux_segments/manifest.json` has since advanced both `fdinfo-map-info-helpers` and `map-reuse-compatibility` as landed helper-first slices with the newer shared bridge rationale, so the smallest same-family reminder drift is now whether sibling reminder surfaces continue to reflect those same landed `why_now` strings whenever they restate the focused bridge packet.",
    ),
    BRIDGE_BOUNDARY_SURVEY_PATH: (
        "Current mixed-source bridge packet",
        "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`zigux/tests/phase8_file_path_handle_boundary_guard.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`",
        "`scripts/zigux/validate-phase8.py`",
        "make -C zigux phase8-file-path-handle-bridge-test",
        "make -C zigux phase8",
        "resolveReusePinnedMapAttempt()",
        "planTokenPreparation()",
        "live procfs reads, live bpffs opens, token materialization, `bpf_obj_get()` reopen flow, descriptor replacement, or broader fd ownership behavior",
    ),
    BRIDGE_SLICE_PATH: (
        "Current helper packet",
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`zigux/tests/phase8_file_path_handle_boundary_guard.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`",
        "`scripts/zigux/validate-phase8.py`",
        "`make -C zigux phase8`",
        "resolveReusePinnedMapAttempt()",
        "planTokenPreparation() gating explicit",
        "no descriptor replacement, transfer, or close ownership semantics",
    ),
    MAKEFILE_PATH: (
        "phase8-libbpf-segments-test:",
        "zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
        "phase8-test:",
        "zigux/tests/phase8_build.zig --summary all",
    ),
    BRIDGE_TEST_PATH: (
        "phase 8 file-path handle bridge proof keeps the manifest-backed helper and deferred bridge split explicit",
        '"slug": "fdinfo-map-info-helpers", "status": "starter_landed"',
        '"slug": "map-reuse-compatibility", "status": "starter_landed"',
        '"slug": "file-path-and-handle-bridge", "status": "deferred_high_risk", "kind": "resource_boundary"',
    ),
    BRIDGE_BOUNDARY_GUARD_TEST_PATH: (
        'test "phase 8 file-path-handle boundary guard keeps the deferred bridge aligned across the manifest, slice, survey, and shared replay" {',
        '"slug": "fdinfo-map-info-helpers"',
        '"slug": "file-path-and-handle-bridge"',
        "planning-only `planTokenPreparation()` gating",
        "phase8_file_path_handle_bridge_manifest_sync.zig",
        "phase8-file-path-handle-boundary-guard-tests",
        "no descriptor replacement, transfer, or close ownership semantics",
    ),
    BRIDGE_MANIFEST_SYNC_TEST_PATH: (
        'test "phase 8 file-path handle bridge manifest keeps the landed helper wording explicit" {',
        '"lane_key": "P8-L13"',
        '"id": "P8-L13-S07"',
        '"slug": "file-path-and-handle-bridge", "status": "deferred_high_risk", "kind": "resource_boundary"',
        "planning-only token-readiness gating as a reviewable landed helper slice",
    ),
    MANIFEST_PATH: (
        '"slug": "fdinfo-map-info-helpers", "status": "starter_landed"',
        '"why_now": "The shared file-path bridge destination already carries the bounded procfs path construction and fdinfo text parsing helpers, so this landed slice should stay explicitly smaller than direct file reads, descriptor ownership, or pinned-object reopen flow."',
        '"slug": "map-reuse-compatibility", "status": "starter_landed"',
        '"why_now": "The shared bridge surface now already carries the reused-map-name chooser and compatibility comparison as landed helper-only behavior, and it should stay reviewable without widening into FD duplication, close-on-replacement, or pinned-map reopen side effects."',
        '"slug": "file-path-and-handle-bridge", "status": "deferred_high_risk", "kind": "resource_boundary"',
        '"why_now": "This remaining file-path and handle bridge still crosses real procfs reads, bpffs opens, token creation, bpf_obj_get() reopen flow, and fd ownership semantics, so the helper-first packet should keep it deferred."',
        "direct procfs reads and descriptor ownership flow",
        "token creation, bpffs reopen flow, and other fd-handle bridge side effects",
    ),
    PHASE8_BUILD_PATH: (
        "../../tools/lib/bpf/zigux_segments/verify.zig",
        "phase8_libbpf_segments.zig",
        "phase8_verify_routing_gap.zig",
        "../../tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig",
        'perf_buffer_wait_budget_module.addImport("perf_buffer_poll", perf_buffer_poll_module);',
        "phase8-perf-buffer-wait-budget-tests",
        "test_step.dependOn(&run_perf_buffer_wait_budget_tests.step);",
        "phase8-perf-buffer-ready-window-tests",
        "test_step.dependOn(&run_perf_buffer_ready_window_tests.step);",
        "phase8-file-path-handle-bridge-tests",
        "test_step.dependOn(&run_file_path_handle_bridge_tests.step);",
        "phase8-file-path-handle-boundary-guard-tests",
        "test_step.dependOn(&run_file_path_handle_boundary_guard_tests.step);",
        "phase8-file-path-handle-bridge-manifest-sync-tests",
        "test_step.dependOn(&run_file_path_handle_bridge_manifest_sync_tests.step);",
        "phase8-libbpf-segment-verify-tests",
        "test_step.dependOn(&run_libbpf_segment_verify_tests.step);",
        "phase8-libbpf-segment-compatibility-tests",
        "test_step.dependOn(&run_libbpf_segments_tests.step);",
        "phase8-verify-routing-gap-tests",
        "test_step.dependOn(&run_verify_routing_gap_tests.step);",
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
        '`tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig`',
        "phase8 perf-buffer wait budget normalizes bounded waits into ms and ns budgets",
        "PERF_BUFFER_WAIT_BUDGET_SEGMENT = Path(",
        'test "phase 8 libbpf-segment compatibility witness keeps the mixed-source bridge packet visible" {',
        'test "phase 8 libbpf-segment compatibility witness keeps stable-output verifier shards visible" {',
    ),
    LIBBPF_SEGMENTS_BUILD_PATH: (
        'b.path("../../tools/lib/bpf/zigux_segments/verify.zig")',
        '"phase8-libbpf-segment-verify-tests"',
        '"Run focused Phase 8 libbpf segment verify build"',
    ),
    VERIFY_PATH: (
        'const cpu_mask = @import("cpu_mask.zig");',
        'const cpu_mask_verify = @import("cpu_mask_verify.zig");',
        'const logging = @import("logging.zig");',
        'const logging_verify = @import("logging_verify.zig");',
        'const online_cpu_routing = @import("online_cpu_routing.zig");',
        'const online_cpu_routing_mask_bridge = @import("online_cpu_routing_mask_bridge.zig");',
        'const online_cpu_routing_mask_bridge_verify = @import("online_cpu_routing_mask_bridge_verify.zig");',
        'const online_cpu_routing_verify = @import("online_cpu_routing_verify.zig");',
        'const perf_buffer_poll = @import("perf_buffer_poll.zig");',
        'const perf_buffer_poll_verify = @import("perf_buffer_poll_verify.zig");',
        'const perf_buffer_ready_window = @import("perf_buffer_ready_window.zig");',
        'const file_path_handle_bridge_verify = @import("file_path_handle_bridge_verify.zig");',
        'const pin_path = @import("pin_path.zig");',
        'const pin_path_verify = @import("pin_path_verify.zig");',
        'const ready_buffer_attempt_verify = @import("ready_buffer_attempt_verify.zig");',
        'const ready_buffer_fd_lookup = @import("ready_buffer_fd_lookup.zig");',
        'const ready_buffer_fd_verify = @import("ready_buffer_fd_verify.zig");',
        'const ready_buffer_window_verify = @import("ready_buffer_window_verify.zig");',
        'const type_names = @import("type_names.zig");',
        'const type_names_verify = @import("type_names_verify.zig");',
        "std.testing.refAllDecls(cpu_mask_verify);",
        "std.testing.refAllDecls(logging_verify);",
        "std.testing.refAllDecls(online_cpu_routing_mask_bridge);",
        "std.testing.refAllDecls(online_cpu_routing_mask_bridge_verify);",
        "std.testing.refAllDecls(online_cpu_routing_verify);",
        "std.testing.refAllDecls(perf_buffer_poll_verify);",
        "std.testing.refAllDecls(perf_buffer_ready_window);",
        "std.testing.refAllDecls(file_path_handle_bridge_verify);",
        "std.testing.refAllDecls(pin_path_verify);",
        "std.testing.refAllDecls(ready_buffer_attempt_verify);",
        "std.testing.refAllDecls(ready_buffer_fd_lookup);",
        "std.testing.refAllDecls(ready_buffer_fd_verify);",
        "std.testing.refAllDecls(ready_buffer_window_verify);",
        "std.testing.refAllDecls(type_names);",
        "std.testing.refAllDecls(type_names_verify);",
        "materialized tools/lib/bpf Zigux segments keep stable online-CPU route-cpu wrappers explicit",
        "resolveNextOnlineCpuRouteCpuIndex(",
        "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex",
        "materialized tools/lib/bpf Zigux segments keep stable online-CPU route-fd wrappers explicit",
        "resolveNextOnlineCpuRouteBufferFd(",
        "resolveNextOnlineCpuRouteBufferFdAtIndex",
        "resolveNextOnlineCpuRouteBufferFdReturnAtIndex",
        "materialized tools/lib/bpf Zigux segments keep stable online-CPU mask-bridge wrappers explicit",
        "summarizeOnlineCpuRoutingFromString(",
        "summarizeOnlineCpuRoutingFromReader(",
        "materialized tools/lib/bpf Zigux segments keep stable ready-buffer fd wrappers explicit",
        "resolveReadyBufferFdAtAttempt",
        "resolveReadyBufferFdLookupReturnAtAttempt",
        "materialized tools/lib/bpf Zigux segments keep stable ready-buffer fd-lookup wrappers explicit",
        "summarizeReadyBufferFdLookupAtAttempt(",
        "resolveReadyBufferFdLookupReturn(",
        "materialized tools/lib/bpf Zigux segments keep stable ready-buffer window wrappers explicit",
        "resolveReadyBufferWindowMappedSizeAtAttempt",
        "resolveReadyBufferWindowMappedSizeReturnAtAttempt",
        "resolveReadyBufferWindowLookupReturnAtAttempt",
        "materialized tools/lib/bpf Zigux segments keep stable libbpf type-name formatters explicit",
        "formatLibbpfBpfLinkType",
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
    FILE_PATH_HANDLE_BRIDGE_VERIFY_PATH: (
        'test "phase8 file-path bridge entrypoints stay explicit" {',
        'try std.testing.expect(@hasDecl(bridge, "planTokenPreparation"));',
        'test "phase8 file-path bridge keeps helper-only outputs stable" {',
        'test "phase8 file-path bridge keeps fdinfo-map-info and planning helpers stable" {',
        'test "phase8 file-path bridge keeps reuse-flag normalization and mismatch reporting stable" {',
        'test "phase8 file-path bridge keeps validation and errno outputs stable" {',
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
        "pub fn advanceOnlineCpuCursor(",
        "pub fn summarizeNextOnlineCpuRoute(",
        "pub fn summarizeOnlineCpuRouting(",
        "pub fn resolveNextOnlineCpuRouteCpuIndex(",
        "pub fn resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(",
        'test "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex keeps direct errno-shaped route-cpu wrappers aligned" {',
    ),
    ONLINE_CPU_ROUTING_MASK_BRIDGE_PATH: (
        "pub const ChunkReader = cpu_mask.ChunkReader;",
        "pub const ParseCpuMaskError = cpu_mask.ParseCpuMaskError;",
        "pub const OnlineCpuRoutingSummary = online_cpu_routing.OnlineCpuRoutingSummary;",
        "pub fn summarizeOnlineCpuRoutingFromString(",
        "pub fn summarizeOnlineCpuRoutingFromReader(",
    ),
    ONLINE_CPU_ROUTING_MASK_BRIDGE_VERIFY_PATH: (
        'test "phase8 online-cpu routing mask bridge entrypoints stay explicit" {',
        "summarizeOnlineCpuRoutingFromString(",
        'test "phase8 online-cpu routing mask bridge keeps reader-backed summaries aligned" {',
        "summarizeOnlineCpuRoutingFromReader(",
        'test "phase8 online-cpu routing mask bridge keeps malformed mask inputs fail-closed" {',
    ),
    ONLINE_CPU_ROUTING_VERIFY_PATH: (
        'test "phase8 online-cpu route helpers keep typed cpu-index wrappers stable" {',
        "resolveNextOnlineCpuRouteCpuIndex(",
        'test "phase8 online-cpu route helpers keep errno-shaped cpu-index wrappers stable" {',
        "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(",
        'test "phase8 online-cpu route helpers keep typed buffer-fd wrappers stable" {',
        "resolveNextOnlineCpuRouteBufferFd(",
        "resolveNextOnlineCpuRouteBufferFdAtIndex(",
        'test "phase8 online-cpu route helpers keep errno-shaped buffer-fd wrappers stable" {',
        "resolveNextOnlineCpuRouteBufferFdReturn(",
        "resolveNextOnlineCpuRouteBufferFdReturnAtIndex(",
        'test "phase8 online-cpu route helpers fail closed when a hand-built CPU index exceeds i32" {',
        "resolveNextOnlineCpuRouteCpuIndexReturn(impossible)",
    ),
    PERF_BUFFER_POLL_PATH: (
        "pub const BufferFdLookupDisposition = enum {",
        "pub fn resolveReadyBufferFdAtAttempt(",
        "pub fn resolveReadyBufferFdLookupReturnAtAttempt(",
        "pub fn summarizeBufferWindowLookup(",
    ),
    PERF_BUFFER_POLL_VERIFY_PATH: (
        'test "phase8 perf-buffer poll helper entrypoints stay explicit" {',
        "summarizePollExecutionResultFromWaitResult",
        'test "phase8 perf-buffer poll rejects impossible hand-built summaries and mismatched ready waits" {',
    ),
    PERF_BUFFER_WAIT_BUDGET_PATH: (
        "pub const WaitBudgetSummary = struct {",
        "pub fn summarizeWaitBudget(",
        "pub fn summarizeWaitBudgetFromPollSummary(",
        'test "phase8 perf-buffer wait budget normalizes bounded waits into ms and ns budgets" {',
        'test "phase8 perf-buffer wait budget rejects invalid negative waits" {',
    ),
    PERF_BUFFER_READY_WINDOW_PATH: (
        "pub fn summarizeReadyBufferWindowLookupAtAttempt(",
        "pub fn resolveReadyBufferWindowMappedSizeReturnAtAttempt(",
        "pub fn resolveReadyBufferWindowLookupReturnAtAttempt(",
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
    READY_BUFFER_FD_LOOKUP_PATH: (
        "pub fn summarizeReadyBufferFdLookupAtAttempt(",
        "pub fn resolveReadyBufferFdAtAttempt(",
        "pub fn resolveReadyBufferFdLookupReturnAtAttempt(",
        'test "phase8 ready-buffer fd lookup helper keeps errno-shaped outputs stable" {',
    ),
    READY_BUFFER_FD_VERIFY_PATH: (
        'const ready_buffer_fd_lookup = @import("ready_buffer_fd_lookup.zig");',
        'test "phase8 ready-buffer fd helper entrypoints stay explicit" {',
        "resolveReadyBufferFdAtAttempt",
        "resolveReadyBufferFdLookupReturnAtAttempt",
        'test "phase8 ready-buffer fd helpers keep errno-shaped outputs stable" {',
    ),
    READY_BUFFER_WINDOW_VERIFY_PATH: (
        'test "phase8 ready-buffer window helper entrypoints stay explicit" {',
        "resolveReadyBufferWindowMappedSizeReturnAtAttempt",
        "resolveReadyBufferWindowLookupReturnAtAttempt",
        'test "phase8 ready-buffer window helpers keep lookup-return outputs stable" {',
    ),
    TYPE_NAMES_PATH: (
        "pub fn libbpfBpfMapTypeStr(",
        "pub fn libbpfBpfAttachTypeStr(",
        "pub fn formatLibbpfBpfProgType(",
    ),
    TYPE_NAMES_VERIFY_PATH: (
        'test "phase8 libbpf type-name helper entrypoints stay explicit" {',
        "libbpfBpfMapTypeStr(27)",
        "formatLibbpfBpfProgType(prog_buffer[0..], 33)",
        'test "phase8 libbpf type-name formatters still fail closed on short buffers" {',
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


def emit_result(problems: list[str]) -> int:
    if problems:
        print("PHASE8_LIBBPF_SHARD_ROUTES=fail")
        print("PHASE8_LIBBPF_SHARD_ROUTES_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE8_LIBBPF_SHARD_ROUTES_PROBLEMS_END")
        return 1

    print("PHASE8_LIBBPF_SHARD_ROUTES=pass")
    print(f"PHASE8_LIBBPF_SHARD_ROUTES_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_LIBBPF_SHARD_ROUTES_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


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
    if "PHASE8_LIBBPF_SHARD_ROUTES=fail" not in output:
        raise SystemExit(f"self-test-missing-fail-banner:{output}")
    if "PHASE8_LIBBPF_SHARD_ROUTES_PROBLEMS_START" not in output:
        raise SystemExit(f"self-test-missing-problem-banner:{output}")
    if expected not in output:
        raise SystemExit(f"self-test-mismatch:{expected}:{output}")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_libbpf_shard_routes_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = run_validator(baseline_root)
        baseline_output = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
        if baseline.returncode != 0:
            raise SystemExit(f"self-test-baseline-failed:{baseline_output}")
        if "PHASE8_LIBBPF_SHARD_ROUTES=pass" not in baseline_output:
            raise SystemExit(f"self-test-missing-pass-banner:{baseline_output}")
        if (
            f"PHASE8_LIBBPF_SHARD_ROUTES_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}"
            not in baseline_output
        ):
            raise SystemExit(f"self-test-missing-file-count:{baseline_output}")
        if (
            "PHASE8_LIBBPF_SHARD_ROUTES_REQUIRED_MARKER_COUNT="
            f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
            not in baseline_output
        ):
            raise SystemExit(f"self-test-missing-marker-count:{baseline_output}")

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
            if "PHASE8_LIBBPF_SHARD_ROUTES=fail" not in output:
                raise SystemExit(f"self-test-missing-fail-banner:{output}")
            if "PHASE8_LIBBPF_SHARD_ROUTES_PROBLEMS_START" not in output:
                raise SystemExit(f"self-test-missing-problem-banner:{output}")
            if expected not in output:
                raise SystemExit(f"self-test-mismatch:{expected}:{output}")
            cases += 1

    return cases


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        cases = run_self_test()
        print("PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST=pass")
        print(f"PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST_CASE_COUNT={cases}")
        return 0

    return emit_result(validate(args.root))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
