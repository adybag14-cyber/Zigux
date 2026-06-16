const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE8_LIBBPF_SHARD_ROUTES=pass";
pub const self_test_pass_marker = "PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST=pass";

const SCRIPT_PATH = [_][]const u8{
    "scripts\\zigux/check_phase8_libbpf_shard_routes.zig",
};

const VALIDATOR_PATH = [_][]const u8{
    "scripts\\zigux/validate_phase8.zig",
};

const SURVEY_PATH = [_][]const u8{
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
};

const BRIDGE_BOUNDARY_SURVEY_PATH = [_][]const u8{
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
};

const BRIDGE_SLICE_PATH = [_][]const u8{
    "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

const BRIDGE_TEST_PATH = [_][]const u8{
    "zigux/tests/phase8_file_path_handle_bridge.zig",
};

const BRIDGE_BOUNDARY_GUARD_TEST_PATH = [_][]const u8{
    "zigux/tests/phase8_file_path_handle_boundary_guard.zig",
};

const BRIDGE_MANIFEST_SYNC_TEST_PATH = [_][]const u8{
    "zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig",
};

const MANIFEST_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/manifest.json",
};

const PHASE8_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase8_build.zig",
};

const VERIFY_ROUTING_GAP_TEST_PATH = [_][]const u8{
    "zigux/tests/phase8_verify_routing_gap.zig",
};

const VERIFY_ROUTING_GAP_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase8_verify_routing_gap_only_build.zig",
};

const LIBBPF_SEGMENTS_TEST_PATH = [_][]const u8{
    "zigux/tests/phase8_libbpf_segments.zig",
};

const LIBBPF_SEGMENTS_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase8_libbpf_segments_only_build.zig",
};

const VERIFY_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/verify.zig",
};

const CPU_MASK_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/cpu_mask.zig",
};

const CPU_MASK_VERIFY_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/cpu_mask_verify.zig",
};

const FILE_PATH_HANDLE_BRIDGE_VERIFY_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge_verify.zig",
};

const LOGGING_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/logging.zig",
};

const LOGGING_VERIFY_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/logging_verify.zig",
};

const ONLINE_CPU_ROUTING_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
};

const ONLINE_CPU_ROUTING_MASK_BRIDGE_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge.zig",
};

const ONLINE_CPU_ROUTING_MASK_BRIDGE_VERIFY_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge_verify.zig",
};

const ONLINE_CPU_ROUTING_VERIFY_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig",
};

const PERF_BUFFER_POLL_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
};

const PERF_BUFFER_POLL_VERIFY_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig",
};

const PERF_BUFFER_WAIT_BUDGET_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig",
};

const PERF_BUFFER_READY_WINDOW_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig",
};

const PIN_PATH_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/pin_path.zig",
};

const PIN_PATH_VERIFY_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/pin_path_verify.zig",
};

const READY_BUFFER_ATTEMPT_VERIFY_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig",
};

const READY_BUFFER_FD_LOOKUP_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/ready_buffer_fd_lookup.zig",
};

const READY_BUFFER_FD_VERIFY_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig",
};

const READY_BUFFER_WINDOW_VERIFY_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig",
};

const TYPE_NAMES_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/type_names.zig",
};

const TYPE_NAMES_VERIFY_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/type_names_verify.zig",
};

const REQUIRED_MARKERS__scripts_zigux_validate-phase8_py = [_][]const u8{
    "LIBBPF_SHARD_ROUTES_CHECKER = Path(\"scripts\\zigux/check_phase8_libbpf_shard_routes.zig\")",
    "LIBBPF_SHARD_ROUTES_CHECKER,",
    "CPU_MASK_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/cpu_mask.zig\")",
    "CPU_MASK_VERIFY_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/cpu_mask_verify.zig\")",
    "LOGGING_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/logging.zig\")",
    "LOGGING_VERIFY_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/logging_verify.zig\")",
    "ONLINE_CPU_ROUTING_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/online_cpu_routing.zig\")",
    "ONLINE_CPU_ROUTING_VERIFY_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/online_cpu_routing_verify.zig\")",
    "PERF_BUFFER_POLL_VERIFY_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig\")",
    "PERF_BUFFER_WAIT_BUDGET_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig\")",
    "PERF_BUFFER_READY_WINDOW_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig\")",
    "PIN_PATH_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/pin_path.zig\")",
    "PIN_PATH_VERIFY_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/pin_path_verify.zig\")",
    "READY_BUFFER_ATTEMPT_VERIFY_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig\")",
    "READY_BUFFER_FD_VERIFY_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig\")",
    "READY_BUFFER_WINDOW_VERIFY_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig\")",
    "TYPE_NAMES_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/type_names.zig\")",
    "TYPE_NAMES_VERIFY_SEGMENT = Path(\"tools/lib/bpf/zigux_segments/type_names_verify.zig\")",
};

const REQUIRED_MARKERS__Documentation_zigux_phase8-libbpf-segment-survey_md = [_][]const u8{
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
};

const REQUIRED_MARKERS__Documentation_zigux_phase8-userspace-kernel-bridge-boundary-survey_md = [_][]const u8{
    "Current mixed-source bridge packet",
    "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
    "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
    "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
    "`zigux/tests/phase8_file_path_handle_boundary_guard.zig`",
    "`zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`",
    "`scripts\\zigux/validate_phase8.zig`",
    "make -C zigux phase8-file-path-handle-bridge-test",
    "make -C zigux phase8",
    "resolveReusePinnedMapAttempt()",
    "planTokenPreparation()",
    "live procfs reads, live bpffs opens, token materialization, `bpf_obj_get()` reopen flow, descriptor replacement, or broader fd ownership behavior",
};

const REQUIRED_MARKERS__Documentation_zigux_phase8-file-path-handle-bridge-slice_md = [_][]const u8{
    "Current helper packet",
    "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
    "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
    "`zigux/tests/phase8_file_path_handle_boundary_guard.zig`",
    "`zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`",
    "`scripts\\zigux/validate_phase8.zig`",
    "`make -C zigux phase8`",
    "resolveReusePinnedMapAttempt()",
    "planTokenPreparation() gating explicit",
    "no descriptor replacement, transfer, or close ownership semantics",
};

const REQUIRED_MARKERS__zigux_Makefile = [_][]const u8{
    "phase8-libbpf-segments-test:",
    "zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
    "phase8-test:",
    "zigux/tests/phase8_build.zig --summary all",
};

const REQUIRED_MARKERS__zigux_tests_phase8_file_path_handle_bridge_zig = [_][]const u8{
    "phase 8 file-path handle bridge proof keeps the manifest-backed helper and deferred bridge split explicit",
    "\"slug\": \"fdinfo-map-info-helpers\", \"status\": \"starter_landed\"",
    "\"slug\": \"map-reuse-compatibility\", \"status\": \"starter_landed\"",
    "\"slug\": \"file-path-and-handle-bridge\", \"status\": \"deferred_high_risk\", \"kind\": \"resource_boundary\"",
};

const REQUIRED_MARKERS__zigux_tests_phase8_file_path_handle_boundary_guard_zig = [_][]const u8{
    "test \"phase 8 file-path-handle boundary guard keeps the deferred bridge aligned across the manifest, slice, survey, and shared replay\" {",
    "\"slug\": \"fdinfo-map-info-helpers\"",
    "\"slug\": \"file-path-and-handle-bridge\"",
    "planning-only `planTokenPreparation()` gating",
    "phase8_file_path_handle_bridge_manifest_sync.zig",
    "phase8-file-path-handle-boundary-guard-tests",
    "no descriptor replacement, transfer, or close ownership semantics",
};

const REQUIRED_MARKERS__zigux_tests_phase8_file_path_handle_bridge_manifest_sync_zig = [_][]const u8{
    "test \"phase 8 file-path handle bridge manifest keeps the landed helper wording explicit\" {",
    "\"lane_key\": \"P8-L13\"",
    "\"id\": \"P8-L13-S07\"",
    "\"slug\": \"file-path-and-handle-bridge\", \"status\": \"deferred_high_risk\", \"kind\": \"resource_boundary\"",
    "planning-only token-readiness gating as a reviewable landed helper slice",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_manifest_json = [_][]const u8{
    "\"slug\": \"fdinfo-map-info-helpers\", \"status\": \"starter_landed\"",
    "\"why_now\": \"The shared file-path bridge destination already carries the bounded procfs path construction and fdinfo text parsing helpers, so this landed slice should stay explicitly smaller than direct file reads, descriptor ownership, or pinned-object reopen flow.\"",
    "\"slug\": \"map-reuse-compatibility\", \"status\": \"starter_landed\"",
    "\"why_now\": \"The shared bridge surface now already carries the reused-map-name chooser and compatibility comparison as landed helper-only behavior, and it should stay reviewable without widening into FD duplication, close-on-replacement, or pinned-map reopen side effects.\"",
    "\"slug\": \"file-path-and-handle-bridge\", \"status\": \"deferred_high_risk\", \"kind\": \"resource_boundary\"",
    "\"why_now\": \"This remaining file-path and handle bridge still crosses real procfs reads, bpffs opens, token creation, bpf_obj_get() reopen flow, and fd ownership semantics, so the helper-first packet should keep it deferred.\"",
    "direct procfs reads and descriptor ownership flow",
    "token creation, bpffs reopen flow, and other fd-handle bridge side effects",
};

const REQUIRED_MARKERS__zigux_tests_phase8_build_zig = [_][]const u8{
    "../../tools/lib/bpf/zigux_segments/verify.zig",
    "phase8_libbpf_segments.zig",
    "phase8_verify_routing_gap.zig",
    "../../tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig",
    "perf_buffer_wait_budget_module.addImport(\"perf_buffer_poll\", perf_buffer_poll_module);",
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
};

const REQUIRED_MARKERS__zigux_tests_phase8_verify_routing_gap_zig = [_][]const u8{
    "phase 8 verify routing witness records the current CPU-index verifier closure",
    "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex",
    "phase 8 verify routing witness records the current direct-readback libbpf survey packet",
};

const REQUIRED_MARKERS__zigux_tests_phase8_verify_routing_gap_only_build_zig = [_][]const u8{
    "phase8_verify_routing_gap.zig",
    "phase8_verify_routing_gap",
    "Run the phase 8 verify routing witness tests.",
};

const REQUIRED_MARKERS__zigux_tests_phase8_libbpf_segments_zig = [_][]const u8{
    "test \"phase 8 libbpf-segment compatibility witness keeps the focused verify-routing replay visible\" {",
    "test \"phase 8 libbpf-segment compatibility witness keeps the shared no-timer poll boundary explicit\" {",
    "`tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig`",
    "phase8 perf-buffer wait budget normalizes bounded waits into ms and ns budgets",
    "PERF_BUFFER_WAIT_BUDGET_SEGMENT = Path(",
    "test \"phase 8 libbpf-segment compatibility witness keeps the mixed-source bridge packet visible\" {",
    "test \"phase 8 libbpf-segment compatibility witness keeps stable-output verifier shards visible\" {",
};

const REQUIRED_MARKERS__zigux_tests_phase8_libbpf_segments_only_build_zig = [_][]const u8{
    "b.path(\"../../tools/lib/bpf/zigux_segments/verify.zig\")",
    "\"phase8-libbpf-segment-verify-tests\"",
    "\"Run focused Phase 8 libbpf segment verify build\"",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_verify_zig = [_][]const u8{
    "const cpu_mask = @import(\"cpu_mask.zig\");",
    "const cpu_mask_verify = @import(\"cpu_mask_verify.zig\");",
    "const logging = @import(\"logging.zig\");",
    "const logging_verify = @import(\"logging_verify.zig\");",
    "const online_cpu_routing = @import(\"online_cpu_routing.zig\");",
    "const online_cpu_routing_mask_bridge = @import(\"online_cpu_routing_mask_bridge.zig\");",
    "const online_cpu_routing_mask_bridge_verify = @import(\"online_cpu_routing_mask_bridge_verify.zig\");",
    "const online_cpu_routing_verify = @import(\"online_cpu_routing_verify.zig\");",
    "const perf_buffer_poll = @import(\"perf_buffer_poll.zig\");",
    "const perf_buffer_poll_verify = @import(\"perf_buffer_poll_verify.zig\");",
    "const perf_buffer_ready_window = @import(\"perf_buffer_ready_window.zig\");",
    "const file_path_handle_bridge_verify = @import(\"file_path_handle_bridge_verify.zig\");",
    "const pin_path = @import(\"pin_path.zig\");",
    "const pin_path_verify = @import(\"pin_path_verify.zig\");",
    "const ready_buffer_attempt_verify = @import(\"ready_buffer_attempt_verify.zig\");",
    "const ready_buffer_fd_lookup = @import(\"ready_buffer_fd_lookup.zig\");",
    "const ready_buffer_fd_verify = @import(\"ready_buffer_fd_verify.zig\");",
    "const ready_buffer_window_verify = @import(\"ready_buffer_window_verify.zig\");",
    "const type_names = @import(\"type_names.zig\");",
    "const type_names_verify = @import(\"type_names_verify.zig\");",
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
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_cpu_mask_zig = [_][]const u8{
    "pub fn parseCpuMaskString(",
    "pub fn summarizePossibleCpusFromReader(",
    "pub fn derivePerfBufferAutoCpuCountFromReader(",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_cpu_mask_verify_zig = [_][]const u8{
    "test \"phase8 cpu-mask helper entrypoints stay explicit\" {",
    "derivePerfBufferAutoCpuCountFromReader",
    "test \"phase8 cpu-mask helpers keep invalid direct and reader-backed inputs fail-closed\" {",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_file_path_handle_bridge_verify_zig = [_][]const u8{
    "test \"phase8 file-path bridge entrypoints stay explicit\" {",
    "try std.testing.expect(@hasDecl(bridge, \"planTokenPreparation\"));",
    "test \"phase8 file-path bridge keeps helper-only outputs stable\" {",
    "test \"phase8 file-path bridge keeps fdinfo-map-info and planning helpers stable\" {",
    "test \"phase8 file-path bridge keeps reuse-flag normalization and mismatch reporting stable\" {",
    "test \"phase8 file-path bridge keeps validation and errno outputs stable\" {",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_logging_zig = [_][]const u8{
    "pub fn parseLogLevelSetting(",
    "pub fn libbpfVersionString(",
    "pub fn formatLibbpfError(",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_logging_verify_zig = [_][]const u8{
    "test \"phase8 logging helper entrypoints stay explicit\" {",
    "parseLogLevelSetting",
    "formatLibbpfError",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_online_cpu_routing_zig = [_][]const u8{
    "pub fn advanceOnlineCpuCursor(",
    "pub fn summarizeNextOnlineCpuRoute(",
    "pub fn summarizeOnlineCpuRouting(",
    "pub fn resolveNextOnlineCpuRouteCpuIndex(",
    "pub fn resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(",
    "test \"resolveNextOnlineCpuRouteCpuIndexReturnAtIndex keeps direct errno-shaped route-cpu wrappers aligned\" {",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_online_cpu_routing_mask_bridge_zig = [_][]const u8{
    "pub const ChunkReader = cpu_mask.ChunkReader;",
    "pub const ParseCpuMaskError = cpu_mask.ParseCpuMaskError;",
    "pub const OnlineCpuRoutingSummary = online_cpu_routing.OnlineCpuRoutingSummary;",
    "pub fn summarizeOnlineCpuRoutingFromString(",
    "pub fn summarizeOnlineCpuRoutingFromReader(",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_online_cpu_routing_mask_bridge_verify_zig = [_][]const u8{
    "test \"phase8 online-cpu routing mask bridge entrypoints stay explicit\" {",
    "summarizeOnlineCpuRoutingFromString(",
    "test \"phase8 online-cpu routing mask bridge keeps reader-backed summaries aligned\" {",
    "summarizeOnlineCpuRoutingFromReader(",
    "test \"phase8 online-cpu routing mask bridge keeps malformed mask inputs fail-closed\" {",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_online_cpu_routing_verify_zig = [_][]const u8{
    "test \"phase8 online-cpu route helpers keep typed cpu-index wrappers stable\" {",
    "resolveNextOnlineCpuRouteCpuIndex(",
    "test \"phase8 online-cpu route helpers keep errno-shaped cpu-index wrappers stable\" {",
    "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex(",
    "test \"phase8 online-cpu route helpers keep typed buffer-fd wrappers stable\" {",
    "resolveNextOnlineCpuRouteBufferFd(",
    "resolveNextOnlineCpuRouteBufferFdAtIndex(",
    "test \"phase8 online-cpu route helpers keep errno-shaped buffer-fd wrappers stable\" {",
    "resolveNextOnlineCpuRouteBufferFdReturn(",
    "resolveNextOnlineCpuRouteBufferFdReturnAtIndex(",
    "test \"phase8 online-cpu route helpers fail closed when a hand-built CPU index exceeds i32\" {",
    "resolveNextOnlineCpuRouteCpuIndexReturn(impossible)",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_perf_buffer_poll_zig = [_][]const u8{
    "pub const BufferFdLookupDisposition = enum {",
    "pub fn resolveReadyBufferFdAtAttempt(",
    "pub fn resolveReadyBufferFdLookupReturnAtAttempt(",
    "pub fn summarizeBufferWindowLookup(",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_perf_buffer_poll_verify_zig = [_][]const u8{
    "test \"phase8 perf-buffer poll helper entrypoints stay explicit\" {",
    "summarizePollExecutionResultFromWaitResult",
    "test \"phase8 perf-buffer poll rejects impossible hand-built summaries and mismatched ready waits\" {",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_perf_buffer_wait_budget_zig = [_][]const u8{
    "pub const WaitBudgetSummary = struct {",
    "pub fn summarizeWaitBudget(",
    "pub fn summarizeWaitBudgetFromPollSummary(",
    "test \"phase8 perf-buffer wait budget normalizes bounded waits into ms and ns budgets\" {",
    "test \"phase8 perf-buffer wait budget rejects invalid negative waits\" {",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_perf_buffer_ready_window_zig = [_][]const u8{
    "pub fn summarizeReadyBufferWindowLookupAtAttempt(",
    "pub fn resolveReadyBufferWindowMappedSizeReturnAtAttempt(",
    "pub fn resolveReadyBufferWindowLookupReturnAtAttempt(",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_pin_path_zig = [_][]const u8{
    "pub const default_bpf_fs_path = \"/sys/fs/bpf\";",
    "pub fn buildValidatedMapPinPath(",
    "pub fn buildValidatedSanitizedProgramPinPath(",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_pin_path_verify_zig = [_][]const u8{
    "test \"phase8 pin-path helper entrypoints stay explicit\" {",
    "buildValidatedSanitizedProgramPinPath",
    "test \"phase8 pin-path helpers keep stable map and program outputs explicit\" {",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_ready_buffer_attempt_verify_zig = [_][]const u8{
    "test \"phase8 ready-buffer attempt helper entrypoints stay explicit\" {",
    "resolveReadyBufferAttemptLookupReturn",
    "test \"phase8 ready-buffer attempt helpers keep errno-shaped outputs stable\" {",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_ready_buffer_fd_lookup_zig = [_][]const u8{
    "pub fn summarizeReadyBufferFdLookupAtAttempt(",
    "pub fn resolveReadyBufferFdAtAttempt(",
    "pub fn resolveReadyBufferFdLookupReturnAtAttempt(",
    "test \"phase8 ready-buffer fd lookup helper keeps errno-shaped outputs stable\" {",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_ready_buffer_fd_verify_zig = [_][]const u8{
    "const ready_buffer_fd_lookup = @import(\"ready_buffer_fd_lookup.zig\");",
    "test \"phase8 ready-buffer fd helper entrypoints stay explicit\" {",
    "resolveReadyBufferFdAtAttempt",
    "resolveReadyBufferFdLookupReturnAtAttempt",
    "test \"phase8 ready-buffer fd helpers keep errno-shaped outputs stable\" {",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_ready_buffer_window_verify_zig = [_][]const u8{
    "test \"phase8 ready-buffer window helper entrypoints stay explicit\" {",
    "resolveReadyBufferWindowMappedSizeReturnAtAttempt",
    "resolveReadyBufferWindowLookupReturnAtAttempt",
    "test \"phase8 ready-buffer window helpers keep lookup-return outputs stable\" {",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_type_names_zig = [_][]const u8{
    "pub fn libbpfBpfMapTypeStr(",
    "pub fn libbpfBpfAttachTypeStr(",
    "pub fn formatLibbpfBpfProgType(",
};

const REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_type_names_verify_zig = [_][]const u8{
    "test \"phase8 libbpf type-name helper entrypoints stay explicit\" {",
    "libbpfBpfMapTypeStr(27)",
    "formatLibbpfBpfProgType(prog_buffer[0..], 33)",
    "test \"phase8 libbpf type-name formatters still fail closed on short buffers\" {",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_script_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_script_path_path);
    const text_script_path = try guard.readUtf8File(io, allocator, text_script_path_path);
    defer allocator.free(text_script_path);
    for (SCRIPT_PATH) |marker| try guard.requireMarker(text_script_path, marker);
    const text_validator_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_validator_path_path);
    const text_validator_path = try guard.readUtf8File(io, allocator, text_validator_path_path);
    defer allocator.free(text_validator_path);
    for (VALIDATOR_PATH) |marker| try guard.requireMarker(text_validator_path, marker);
    const text_survey_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_survey_path_path);
    const text_survey_path = try guard.readUtf8File(io, allocator, text_survey_path_path);
    defer allocator.free(text_survey_path);
    for (SURVEY_PATH) |marker| try guard.requireMarker(text_survey_path, marker);
    const text_bridge_boundary_survey_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_bridge_boundary_survey_path_path);
    const text_bridge_boundary_survey_path = try guard.readUtf8File(io, allocator, text_bridge_boundary_survey_path_path);
    defer allocator.free(text_bridge_boundary_survey_path);
    for (BRIDGE_BOUNDARY_SURVEY_PATH) |marker| try guard.requireMarker(text_bridge_boundary_survey_path, marker);
    const text_bridge_slice_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_bridge_slice_path_path);
    const text_bridge_slice_path = try guard.readUtf8File(io, allocator, text_bridge_slice_path_path);
    defer allocator.free(text_bridge_slice_path);
    for (BRIDGE_SLICE_PATH) |marker| try guard.requireMarker(text_bridge_slice_path, marker);
    const text_makefile_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_makefile_path_path);
    const text_makefile_path = try guard.readUtf8File(io, allocator, text_makefile_path_path);
    defer allocator.free(text_makefile_path);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text_makefile_path, marker);
    const text_bridge_test_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_bridge_test_path_path);
    const text_bridge_test_path = try guard.readUtf8File(io, allocator, text_bridge_test_path_path);
    defer allocator.free(text_bridge_test_path);
    for (BRIDGE_TEST_PATH) |marker| try guard.requireMarker(text_bridge_test_path, marker);
    const text_bridge_boundary_guard_test_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_bridge_boundary_guard_test_path_path);
    const text_bridge_boundary_guard_test_path = try guard.readUtf8File(io, allocator, text_bridge_boundary_guard_test_path_path);
    defer allocator.free(text_bridge_boundary_guard_test_path);
    for (BRIDGE_BOUNDARY_GUARD_TEST_PATH) |marker| try guard.requireMarker(text_bridge_boundary_guard_test_path, marker);
    const text_bridge_manifest_sync_test_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_bridge_manifest_sync_test_path_path);
    const text_bridge_manifest_sync_test_path = try guard.readUtf8File(io, allocator, text_bridge_manifest_sync_test_path_path);
    defer allocator.free(text_bridge_manifest_sync_test_path);
    for (BRIDGE_MANIFEST_SYNC_TEST_PATH) |marker| try guard.requireMarker(text_bridge_manifest_sync_test_path, marker);
    const text_manifest_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_manifest_path_path);
    const text_manifest_path = try guard.readUtf8File(io, allocator, text_manifest_path_path);
    defer allocator.free(text_manifest_path);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text_manifest_path, marker);
    const text_phase8_build_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_phase8_build_path_path);
    const text_phase8_build_path = try guard.readUtf8File(io, allocator, text_phase8_build_path_path);
    defer allocator.free(text_phase8_build_path);
    for (PHASE8_BUILD_PATH) |marker| try guard.requireMarker(text_phase8_build_path, marker);
    const text_verify_routing_gap_test_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_verify_routing_gap_test_path_path);
    const text_verify_routing_gap_test_path = try guard.readUtf8File(io, allocator, text_verify_routing_gap_test_path_path);
    defer allocator.free(text_verify_routing_gap_test_path);
    for (VERIFY_ROUTING_GAP_TEST_PATH) |marker| try guard.requireMarker(text_verify_routing_gap_test_path, marker);
    const text_verify_routing_gap_build_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_verify_routing_gap_build_path_path);
    const text_verify_routing_gap_build_path = try guard.readUtf8File(io, allocator, text_verify_routing_gap_build_path_path);
    defer allocator.free(text_verify_routing_gap_build_path);
    for (VERIFY_ROUTING_GAP_BUILD_PATH) |marker| try guard.requireMarker(text_verify_routing_gap_build_path, marker);
    const text_libbpf_segments_test_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_libbpf_segments_test_path_path);
    const text_libbpf_segments_test_path = try guard.readUtf8File(io, allocator, text_libbpf_segments_test_path_path);
    defer allocator.free(text_libbpf_segments_test_path);
    for (LIBBPF_SEGMENTS_TEST_PATH) |marker| try guard.requireMarker(text_libbpf_segments_test_path, marker);
    const text_libbpf_segments_build_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_libbpf_segments_build_path_path);
    const text_libbpf_segments_build_path = try guard.readUtf8File(io, allocator, text_libbpf_segments_build_path_path);
    defer allocator.free(text_libbpf_segments_build_path);
    for (LIBBPF_SEGMENTS_BUILD_PATH) |marker| try guard.requireMarker(text_libbpf_segments_build_path, marker);
    const text_verify_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_verify_path_path);
    const text_verify_path = try guard.readUtf8File(io, allocator, text_verify_path_path);
    defer allocator.free(text_verify_path);
    for (VERIFY_PATH) |marker| try guard.requireMarker(text_verify_path, marker);
    const text_cpu_mask_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_cpu_mask_path_path);
    const text_cpu_mask_path = try guard.readUtf8File(io, allocator, text_cpu_mask_path_path);
    defer allocator.free(text_cpu_mask_path);
    for (CPU_MASK_PATH) |marker| try guard.requireMarker(text_cpu_mask_path, marker);
    const text_cpu_mask_verify_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_cpu_mask_verify_path_path);
    const text_cpu_mask_verify_path = try guard.readUtf8File(io, allocator, text_cpu_mask_verify_path_path);
    defer allocator.free(text_cpu_mask_verify_path);
    for (CPU_MASK_VERIFY_PATH) |marker| try guard.requireMarker(text_cpu_mask_verify_path, marker);
    const text_file_path_handle_bridge_verify_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_file_path_handle_bridge_verify_path_path);
    const text_file_path_handle_bridge_verify_path = try guard.readUtf8File(io, allocator, text_file_path_handle_bridge_verify_path_path);
    defer allocator.free(text_file_path_handle_bridge_verify_path);
    for (FILE_PATH_HANDLE_BRIDGE_VERIFY_PATH) |marker| try guard.requireMarker(text_file_path_handle_bridge_verify_path, marker);
    const text_logging_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_logging_path_path);
    const text_logging_path = try guard.readUtf8File(io, allocator, text_logging_path_path);
    defer allocator.free(text_logging_path);
    for (LOGGING_PATH) |marker| try guard.requireMarker(text_logging_path, marker);
    const text_logging_verify_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_logging_verify_path_path);
    const text_logging_verify_path = try guard.readUtf8File(io, allocator, text_logging_verify_path_path);
    defer allocator.free(text_logging_verify_path);
    for (LOGGING_VERIFY_PATH) |marker| try guard.requireMarker(text_logging_verify_path, marker);
    const text_online_cpu_routing_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_online_cpu_routing_path_path);
    const text_online_cpu_routing_path = try guard.readUtf8File(io, allocator, text_online_cpu_routing_path_path);
    defer allocator.free(text_online_cpu_routing_path);
    for (ONLINE_CPU_ROUTING_PATH) |marker| try guard.requireMarker(text_online_cpu_routing_path, marker);
    const text_online_cpu_routing_mask_bridge_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_online_cpu_routing_mask_bridge_path_path);
    const text_online_cpu_routing_mask_bridge_path = try guard.readUtf8File(io, allocator, text_online_cpu_routing_mask_bridge_path_path);
    defer allocator.free(text_online_cpu_routing_mask_bridge_path);
    for (ONLINE_CPU_ROUTING_MASK_BRIDGE_PATH) |marker| try guard.requireMarker(text_online_cpu_routing_mask_bridge_path, marker);
    const text_online_cpu_routing_mask_bridge_verify_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_online_cpu_routing_mask_bridge_verify_path_path);
    const text_online_cpu_routing_mask_bridge_verify_path = try guard.readUtf8File(io, allocator, text_online_cpu_routing_mask_bridge_verify_path_path);
    defer allocator.free(text_online_cpu_routing_mask_bridge_verify_path);
    for (ONLINE_CPU_ROUTING_MASK_BRIDGE_VERIFY_PATH) |marker| try guard.requireMarker(text_online_cpu_routing_mask_bridge_verify_path, marker);
    const text_online_cpu_routing_verify_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_online_cpu_routing_verify_path_path);
    const text_online_cpu_routing_verify_path = try guard.readUtf8File(io, allocator, text_online_cpu_routing_verify_path_path);
    defer allocator.free(text_online_cpu_routing_verify_path);
    for (ONLINE_CPU_ROUTING_VERIFY_PATH) |marker| try guard.requireMarker(text_online_cpu_routing_verify_path, marker);
    const text_perf_buffer_poll_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_perf_buffer_poll_path_path);
    const text_perf_buffer_poll_path = try guard.readUtf8File(io, allocator, text_perf_buffer_poll_path_path);
    defer allocator.free(text_perf_buffer_poll_path);
    for (PERF_BUFFER_POLL_PATH) |marker| try guard.requireMarker(text_perf_buffer_poll_path, marker);
    const text_perf_buffer_poll_verify_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_perf_buffer_poll_verify_path_path);
    const text_perf_buffer_poll_verify_path = try guard.readUtf8File(io, allocator, text_perf_buffer_poll_verify_path_path);
    defer allocator.free(text_perf_buffer_poll_verify_path);
    for (PERF_BUFFER_POLL_VERIFY_PATH) |marker| try guard.requireMarker(text_perf_buffer_poll_verify_path, marker);
    const text_perf_buffer_wait_budget_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_perf_buffer_wait_budget_path_path);
    const text_perf_buffer_wait_budget_path = try guard.readUtf8File(io, allocator, text_perf_buffer_wait_budget_path_path);
    defer allocator.free(text_perf_buffer_wait_budget_path);
    for (PERF_BUFFER_WAIT_BUDGET_PATH) |marker| try guard.requireMarker(text_perf_buffer_wait_budget_path, marker);
    const text_perf_buffer_ready_window_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_perf_buffer_ready_window_path_path);
    const text_perf_buffer_ready_window_path = try guard.readUtf8File(io, allocator, text_perf_buffer_ready_window_path_path);
    defer allocator.free(text_perf_buffer_ready_window_path);
    for (PERF_BUFFER_READY_WINDOW_PATH) |marker| try guard.requireMarker(text_perf_buffer_ready_window_path, marker);
    const text_pin_path_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_pin_path_path_path);
    const text_pin_path_path = try guard.readUtf8File(io, allocator, text_pin_path_path_path);
    defer allocator.free(text_pin_path_path);
    for (PIN_PATH_PATH) |marker| try guard.requireMarker(text_pin_path_path, marker);
    const text_pin_path_verify_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_pin_path_verify_path_path);
    const text_pin_path_verify_path = try guard.readUtf8File(io, allocator, text_pin_path_verify_path_path);
    defer allocator.free(text_pin_path_verify_path);
    for (PIN_PATH_VERIFY_PATH) |marker| try guard.requireMarker(text_pin_path_verify_path, marker);
    const text_ready_buffer_attempt_verify_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_ready_buffer_attempt_verify_path_path);
    const text_ready_buffer_attempt_verify_path = try guard.readUtf8File(io, allocator, text_ready_buffer_attempt_verify_path_path);
    defer allocator.free(text_ready_buffer_attempt_verify_path);
    for (READY_BUFFER_ATTEMPT_VERIFY_PATH) |marker| try guard.requireMarker(text_ready_buffer_attempt_verify_path, marker);
    const text_ready_buffer_fd_lookup_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_ready_buffer_fd_lookup_path_path);
    const text_ready_buffer_fd_lookup_path = try guard.readUtf8File(io, allocator, text_ready_buffer_fd_lookup_path_path);
    defer allocator.free(text_ready_buffer_fd_lookup_path);
    for (READY_BUFFER_FD_LOOKUP_PATH) |marker| try guard.requireMarker(text_ready_buffer_fd_lookup_path, marker);
    const text_ready_buffer_fd_verify_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_ready_buffer_fd_verify_path_path);
    const text_ready_buffer_fd_verify_path = try guard.readUtf8File(io, allocator, text_ready_buffer_fd_verify_path_path);
    defer allocator.free(text_ready_buffer_fd_verify_path);
    for (READY_BUFFER_FD_VERIFY_PATH) |marker| try guard.requireMarker(text_ready_buffer_fd_verify_path, marker);
    const text_ready_buffer_window_verify_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_ready_buffer_window_verify_path_path);
    const text_ready_buffer_window_verify_path = try guard.readUtf8File(io, allocator, text_ready_buffer_window_verify_path_path);
    defer allocator.free(text_ready_buffer_window_verify_path);
    for (READY_BUFFER_WINDOW_VERIFY_PATH) |marker| try guard.requireMarker(text_ready_buffer_window_verify_path, marker);
    const text_type_names_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_type_names_path_path);
    const text_type_names_path = try guard.readUtf8File(io, allocator, text_type_names_path_path);
    defer allocator.free(text_type_names_path);
    for (TYPE_NAMES_PATH) |marker| try guard.requireMarker(text_type_names_path, marker);
    const text_type_names_verify_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_libbpf_shard_routes.zig");
    defer allocator.free(text_type_names_verify_path_path);
    const text_type_names_verify_path = try guard.readUtf8File(io, allocator, text_type_names_verify_path_path);
    defer allocator.free(text_type_names_verify_path);
    for (TYPE_NAMES_VERIFY_PATH) |marker| try guard.requireMarker(text_type_names_verify_path, marker);
    const text_required_markers__scripts_zigux_validate-phase8_py_path = try guard.joinPath(allocator, root, "scripts/zigux/validate-phase8/py");
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase8_py_path);
    const text_required_markers__scripts_zigux_validate-phase8_py = try guard.readUtf8File(io, allocator, text_required_markers__scripts_zigux_validate-phase8_py_path);
    defer allocator.free(text_required_markers__scripts_zigux_validate-phase8_py);
    for (REQUIRED_MARKERS__scripts_zigux_validate-phase8_py) |marker| try guard.requireMarker(text_required_markers__scripts_zigux_validate-phase8_py, marker);
    const text_required_markers__documentation_zigux_phase8-libbpf-segment-survey_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-libbpf-segment-survey/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase8-libbpf-segment-survey_md_path);
    const text_required_markers__documentation_zigux_phase8-libbpf-segment-survey_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase8-libbpf-segment-survey_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase8-libbpf-segment-survey_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase8-libbpf-segment-survey_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase8-libbpf-segment-survey_md, marker);
    const text_required_markers__documentation_zigux_phase8-userspace-kernel-bridge-boundary-survey_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase8-userspace-kernel-bridge-boundary-survey_md_path);
    const text_required_markers__documentation_zigux_phase8-userspace-kernel-bridge-boundary-survey_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase8-userspace-kernel-bridge-boundary-survey_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase8-userspace-kernel-bridge-boundary-survey_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase8-userspace-kernel-bridge-boundary-survey_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase8-userspace-kernel-bridge-boundary-survey_md, marker);
    const text_required_markers__documentation_zigux_phase8-file-path-handle-bridge-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-file-path-handle-bridge-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase8-file-path-handle-bridge-slice_md_path);
    const text_required_markers__documentation_zigux_phase8-file-path-handle-bridge-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase8-file-path-handle-bridge-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase8-file-path-handle-bridge-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase8-file-path-handle-bridge-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase8-file-path-handle-bridge-slice_md, marker);
    const text_required_markers__zigux_makefile_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_required_markers__zigux_makefile_path);
    const text_required_markers__zigux_makefile = try guard.readUtf8File(io, allocator, text_required_markers__zigux_makefile_path);
    defer allocator.free(text_required_markers__zigux_makefile);
    for (REQUIRED_MARKERS__zigux_Makefile) |marker| try guard.requireMarker(text_required_markers__zigux_makefile, marker);
    const text_required_markers__zigux_tests_phase8_file_path_handle_bridge_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase8/file/path/handle/bridge/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase8_file_path_handle_bridge_zig_path);
    const text_required_markers__zigux_tests_phase8_file_path_handle_bridge_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase8_file_path_handle_bridge_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase8_file_path_handle_bridge_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase8_file_path_handle_bridge_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase8_file_path_handle_bridge_zig, marker);
    const text_required_markers__zigux_tests_phase8_file_path_handle_boundary_guard_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase8/file/path/handle/boundary/guard/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase8_file_path_handle_boundary_guard_zig_path);
    const text_required_markers__zigux_tests_phase8_file_path_handle_boundary_guard_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase8_file_path_handle_boundary_guard_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase8_file_path_handle_boundary_guard_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase8_file_path_handle_boundary_guard_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase8_file_path_handle_boundary_guard_zig, marker);
    const text_required_markers__zigux_tests_phase8_file_path_handle_bridge_manifest_sync_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase8/file/path/handle/bridge/manifest/sync/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase8_file_path_handle_bridge_manifest_sync_zig_path);
    const text_required_markers__zigux_tests_phase8_file_path_handle_bridge_manifest_sync_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase8_file_path_handle_bridge_manifest_sync_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase8_file_path_handle_bridge_manifest_sync_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase8_file_path_handle_bridge_manifest_sync_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase8_file_path_handle_bridge_manifest_sync_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_manifest_json_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/manifest/json");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_manifest_json_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_manifest_json = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_manifest_json_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_manifest_json);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_manifest_json) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_manifest_json, marker);
    const text_required_markers__zigux_tests_phase8_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase8/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase8_build_zig_path);
    const text_required_markers__zigux_tests_phase8_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase8_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase8_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase8_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase8_build_zig, marker);
    const text_required_markers__zigux_tests_phase8_verify_routing_gap_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase8/verify/routing/gap/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase8_verify_routing_gap_zig_path);
    const text_required_markers__zigux_tests_phase8_verify_routing_gap_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase8_verify_routing_gap_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase8_verify_routing_gap_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase8_verify_routing_gap_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase8_verify_routing_gap_zig, marker);
    const text_required_markers__zigux_tests_phase8_verify_routing_gap_only_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase8/verify/routing/gap/only/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase8_verify_routing_gap_only_build_zig_path);
    const text_required_markers__zigux_tests_phase8_verify_routing_gap_only_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase8_verify_routing_gap_only_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase8_verify_routing_gap_only_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase8_verify_routing_gap_only_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase8_verify_routing_gap_only_build_zig, marker);
    const text_required_markers__zigux_tests_phase8_libbpf_segments_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase8/libbpf/segments/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase8_libbpf_segments_zig_path);
    const text_required_markers__zigux_tests_phase8_libbpf_segments_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase8_libbpf_segments_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase8_libbpf_segments_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase8_libbpf_segments_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase8_libbpf_segments_zig, marker);
    const text_required_markers__zigux_tests_phase8_libbpf_segments_only_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase8/libbpf/segments/only/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase8_libbpf_segments_only_build_zig_path);
    const text_required_markers__zigux_tests_phase8_libbpf_segments_only_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase8_libbpf_segments_only_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase8_libbpf_segments_only_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase8_libbpf_segments_only_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase8_libbpf_segments_only_build_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_verify_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/verify/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_verify_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_verify_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_verify_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_verify_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_verify_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_verify_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_cpu_mask_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/cpu/mask/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_cpu_mask_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_cpu_mask_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_cpu_mask_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_cpu_mask_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_cpu_mask_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_cpu_mask_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_cpu_mask_verify_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/cpu/mask/verify/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_cpu_mask_verify_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_cpu_mask_verify_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_cpu_mask_verify_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_cpu_mask_verify_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_cpu_mask_verify_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_cpu_mask_verify_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_file_path_handle_bridge_verify_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/file/path/handle/bridge/verify/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_file_path_handle_bridge_verify_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_file_path_handle_bridge_verify_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_file_path_handle_bridge_verify_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_file_path_handle_bridge_verify_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_file_path_handle_bridge_verify_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_file_path_handle_bridge_verify_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_logging_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/logging/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_logging_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_logging_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_logging_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_logging_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_logging_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_logging_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_logging_verify_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/logging/verify/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_logging_verify_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_logging_verify_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_logging_verify_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_logging_verify_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_logging_verify_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_logging_verify_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/online/cpu/routing/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_online_cpu_routing_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_mask_bridge_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/online/cpu/routing/mask/bridge/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_mask_bridge_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_mask_bridge_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_mask_bridge_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_mask_bridge_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_online_cpu_routing_mask_bridge_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_mask_bridge_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_mask_bridge_verify_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/online/cpu/routing/mask/bridge/verify/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_mask_bridge_verify_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_mask_bridge_verify_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_mask_bridge_verify_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_mask_bridge_verify_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_online_cpu_routing_mask_bridge_verify_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_mask_bridge_verify_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_verify_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/online/cpu/routing/verify/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_verify_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_verify_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_verify_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_verify_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_online_cpu_routing_verify_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_online_cpu_routing_verify_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_poll_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/perf/buffer/poll/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_poll_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_poll_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_poll_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_poll_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_perf_buffer_poll_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_poll_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_poll_verify_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/perf/buffer/poll/verify/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_poll_verify_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_poll_verify_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_poll_verify_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_poll_verify_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_perf_buffer_poll_verify_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_poll_verify_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_wait_budget_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/perf/buffer/wait/budget/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_wait_budget_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_wait_budget_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_wait_budget_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_wait_budget_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_perf_buffer_wait_budget_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_wait_budget_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_ready_window_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/perf/buffer/ready/window/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_ready_window_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_ready_window_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_ready_window_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_ready_window_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_perf_buffer_ready_window_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_perf_buffer_ready_window_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_pin_path_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/pin/path/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_pin_path_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_pin_path_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_pin_path_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_pin_path_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_pin_path_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_pin_path_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_pin_path_verify_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/pin/path/verify/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_pin_path_verify_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_pin_path_verify_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_pin_path_verify_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_pin_path_verify_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_pin_path_verify_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_pin_path_verify_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_attempt_verify_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/ready/buffer/attempt/verify/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_attempt_verify_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_attempt_verify_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_attempt_verify_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_attempt_verify_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_ready_buffer_attempt_verify_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_attempt_verify_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_fd_lookup_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/ready/buffer/fd/lookup/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_fd_lookup_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_fd_lookup_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_fd_lookup_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_fd_lookup_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_ready_buffer_fd_lookup_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_fd_lookup_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_fd_verify_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/ready/buffer/fd/verify/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_fd_verify_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_fd_verify_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_fd_verify_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_fd_verify_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_ready_buffer_fd_verify_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_fd_verify_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_window_verify_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/ready/buffer/window/verify/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_window_verify_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_window_verify_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_window_verify_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_window_verify_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_ready_buffer_window_verify_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_ready_buffer_window_verify_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_type_names_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/type/names/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_type_names_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_type_names_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_type_names_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_type_names_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_type_names_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_type_names_zig, marker);
    const text_required_markers__tools_lib_bpf_zigux_segments_type_names_verify_zig_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux/segments/type/names/verify/zig");
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_type_names_verify_zig_path);
    const text_required_markers__tools_lib_bpf_zigux_segments_type_names_verify_zig = try guard.readUtf8File(io, allocator, text_required_markers__tools_lib_bpf_zigux_segments_type_names_verify_zig_path);
    defer allocator.free(text_required_markers__tools_lib_bpf_zigux_segments_type_names_verify_zig);
    for (REQUIRED_MARKERS__tools_lib_bpf_zigux_segments_type_names_verify_zig) |marker| try guard.requireMarker(text_required_markers__tools_lib_bpf_zigux_segments_type_names_verify_zig, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
