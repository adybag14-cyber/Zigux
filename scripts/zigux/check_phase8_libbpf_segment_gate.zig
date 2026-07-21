const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE8_LIBBPF_SEGMENT_GATE=pass";
pub const self_test_pass_marker = "PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };
const Segment = struct { slug: []const u8, status: []const u8 };
const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    segments: []const Segment,
};

const required_files = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
    "Documentation/zigux/phase8-libbpf-segment-survey.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate_phase8.zig",
    "scripts/zigux/check_phase8_libbpf_segment_gate.zig",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase8_libbpf_segments_only_build.zig",
    "zigux/tests/phase8_libbpf_segments.zig",
    "zigux/tests/phase8_file_path_handle_bridge.zig",
    "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
    "zigux/tests/phase8_file_path_handle_boundary_guard.zig",
    "zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig",
    "tools/lib/bpf/zigux_segments/manifest.json",
    "tools/lib/bpf/zigux_segments/verify.zig",
    "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
};

const landed_slugs = [_][]const u8{
    "logging-version-and-errno",
    "pin-path-helpers",
    "cpu-mask-parsing",
    "type-name-helpers",
    "fdinfo-map-info-helpers",
    "map-reuse-compatibility",
    "perf-buffer-poll-bookkeeping",
    "fdinfo-path-and-reuse-name-footholds",
    "ready-buffer-fd-lookup",
    "ready-buffer-window-lookup",
    "perf-buffer-wait-budget",
};

const deferred_slugs = [_][]const u8{
    "file-path-and-handle-bridge",
    "perf-buffer-online-cpu-routing",
    "skeleton-population",
    "object-and-elf-loader",
    "btf-relocation-and-program-load",
};

const markers_0 = [_][]const u8{
    "The directly readable stable-output helper set therefore now keeps the aggregate verifier plus `cpu_mask.zig`, `cpu_mask_verify.zig`, `logging.zig`, `logging_verify.zig`, `pin_path.zig`, `pin_path_verify.zig`, `type_names.zig`, `type_names_verify.zig`, `perf_buffer_poll.zig`, `perf_buffer_wait_budget.zig`, `perf_buffer_poll_verify.zig`, `perf_buffer_ready_window.zig`, `online_cpu_routing.zig`, `online_cpu_routing_verify.zig`, `ready_buffer_attempt_verify.zig`, `ready_buffer_fd_verify.zig`, and `ready_buffer_window_verify.zig` explicit.",
    "Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/logging_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`, `tools/lib/bpf/zigux_segments/pin_path_verify.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, and `tools/lib/bpf/zigux_segments/type_names_verify.zig` explicit.",
    "The directly readable verifier packet now also keeps dedicated stable-output witnesses for cpu-mask parse, string-backed summary, reader-backed summary, auto-count, and fail-closed outputs, logging env/version/error outputs, perf-buffer wait-classification, poll-summary, execution-summary, and impossible-summary fail-closed outputs, pin-path map/program output and validation wrappers, online-CPU route CPU-index and buffer-FD wrappers, ready-buffer attempt wrappers, ready-buffer FD wrappers, ready-buffer window mapped-size and lookup-return wrappers, and type-name lookup plus formatter wrappers explicit beside the aggregate `verify.zig` replay surface.",
    "This survey should therefore keep the helper-first packet and the shared wrapper-route vocabulary explicit together without promoting the still-deferred setup-side routing, reopen-flow, token-materialization, object-model, or bridge-heavy work into direct authenticated helper proof.",
};

const markers_1 = [_][]const u8{
    "The shared file-path bridge destination already carries the bounded procfs path construction and fdinfo text parsing helpers, so this landed slice should stay explicitly smaller than direct file reads, descriptor ownership, or pinned-object reopen flow.",
    "The shared bridge surface now already carries the reused-map-name chooser and compatibility comparison as landed helper-only behavior, and it should stay reviewable without widening into FD duplication, close-on-replacement, or pinned-map reopen side effects.",
};

const markers_2 = [_][]const u8{
    "Current `master` still keeps the mixed-source bridge packet reviewable, and authenticated contents readback now reaches the bridge-side helper and witness files directly again in this runtime.",
    "That narrower split is therefore packet role rather than fetchability: the bridge helper and witness stay on the boundary side of the Phase 8 packet so this survey does not overclaim delivered procfs, bpffs, token, or fd-ownership behavior.",
    "The timing-adjacent poll reminder also stays explicit through `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `zig run scripts/zigux/check_phase8_perf_buffer_poll_gate.zig`, `make -C zigux phase8-perf-buffer-poll-test`, and the shared `phase8` routes; that dedicated packet keeps no standalone timer helper behavior, no standalone clockevent helper behavior, and no broader timeout-sensitive routing behavior explicit while the surrounding setup-side bridge remains deferred.",
};

const markers_3 = [_][]const u8{
    "\"scripts/zigux/check_phase8_libbpf_segment_gate.zig\"",
    "PHASE8_LIBBPF_SEGMENT_GATE=pass",
};

const markers_4 = [_][]const u8{
    "phase8-validate:",
    "phase8-libbpf-segments-test:",
    "zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
    "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
};

const markers_5 = [_][]const u8{
    "../../tools/lib/bpf/zigux_segments/verify.zig",
    "phase8-libbpf-segment-verify-tests",
    "Run focused Phase 8 libbpf segment verify build",
};

const markers_6 = [_][]const u8{
    "test \"phase 8 libbpf-segment compatibility witness keeps the focused verify-routing replay visible\" {",
    "test \"phase 8 libbpf-segment compatibility witness keeps the shared no-timer poll boundary explicit\" {",
    "test \"phase 8 libbpf-segment compatibility witness keeps the mixed-source bridge packet visible\" {",
    "test \"phase 8 libbpf-segment compatibility witness keeps stable-output verifier shards visible\" {",
};

const markers_7 = [_][]const u8{
    "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex",
    "resolveNextOnlineCpuRouteBufferFdAtIndex",
    "resolveNextOnlineCpuRouteBufferFdReturnAtIndex",
    "resolveReadyBufferFdAtAttempt",
    "resolveReadyBufferFdLookupReturnAtAttempt",
    "resolveReadyBufferWindowMappedSizeAtAttempt",
    "resolveReadyBufferWindowMappedSizeReturnAtAttempt",
    "resolveReadyBufferWindowLookupReturnAtAttempt",
    "formatLibbpfBpfLinkType",
};

const markers_8 = [_][]const u8{
    "test \"phase 8 file-path handle bridge proof keeps the manifest-backed helper and deferred bridge split explicit\" {",
    "test \"phase 8 file-path handle bridge helper stays wired into the Linux-style replay routes\" {",
    "planning-only `resolveReusePinnedMapAttempt()` gating",
    "planning-only `planTokenPreparation()` gating",
    "try std.testing.expect(std.mem.indexOf(u8, helper_source, \"bpf_obj_get(\") == null);",
};

const markers_9 = [_][]const u8{
    "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    "phase8_file_path_handle_bridge.zig",
    "phase8-file-path-handle-bridge-tests",
    "Run focused Phase 8 file-path-handle bridge tests",
};

const markers_10 = [_][]const u8{
    "test \"phase 8 file-path-handle boundary guard keeps landed helper slices distinct from the deferred bridge\" {",
    "\"slug\": \"fdinfo-map-info-helpers\"",
    "\"slug\": \"map-reuse-compatibility\"",
    "\"slug\": \"file-path-and-handle-bridge\"",
    "planTokenPreparation",
};

const markers_11 = [_][]const u8{
    "test \"phase 8 file-path handle bridge manifest keeps the landed helper wording explicit\" {",
    "\"lane_key\": \"P8-L13\"",
    "\"id\": \"P8-L13-S07\"",
    "\"slug\": \"file-path-and-handle-bridge\", \"status\": \"deferred_high_risk\", \"kind\": \"resource_boundary\"",
    "planning-only token-readiness gating as a reviewable landed helper slice",
};

const markers_12 = [_][]const u8{
    "pub fn resolveReusePinnedMapAttempt(",
    "pub fn planTokenPreparation(",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase8-libbpf-segment-survey.md", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase8-file-path-handle-bridge-slice.md", .markers = &markers_1 },
    .{ .rel = "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md", .markers = &markers_2 },
    .{ .rel = "scripts/zigux/validate_phase8.zig", .markers = &markers_3 },
    .{ .rel = "zigux/Makefile", .markers = &markers_4 },
    .{ .rel = "zigux/tests/phase8_libbpf_segments_only_build.zig", .markers = &markers_5 },
    .{ .rel = "zigux/tests/phase8_libbpf_segments.zig", .markers = &markers_6 },
    .{ .rel = "tools/lib/bpf/zigux_segments/verify.zig", .markers = &markers_7 },
    .{ .rel = "zigux/tests/phase8_file_path_handle_bridge.zig", .markers = &markers_8 },
    .{ .rel = "zigux/tests/phase8_file_path_handle_bridge_only_build.zig", .markers = &markers_9 },
    .{ .rel = "zigux/tests/phase8_file_path_handle_boundary_guard.zig", .markers = &markers_10 },
    .{ .rel = "zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig", .markers = &markers_11 },
    .{ .rel = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig", .markers = &markers_12 },
};

fn checkManifest(allocator: std.mem.Allocator, source: []const u8) !void {
    const parsed = try std.json.parseFromSlice(Manifest, allocator, source, .{ .ignore_unknown_fields = true });
    defer parsed.deinit();
    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P8-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 8", manifest.phase);
    try std.testing.expect(manifest.surveyed_commit.len != 0);
    try std.testing.expectEqualStrings("tools/lib/bpf/libbpf.c", manifest.anchor);

    var landed_index: usize = 0;
    var deferred_index: usize = 0;
    for (manifest.segments) |segment| {
        if (std.mem.eql(u8, segment.status, "starter_landed")) {
            try std.testing.expect(landed_index < landed_slugs.len);
            try std.testing.expectEqualStrings(landed_slugs[landed_index], segment.slug);
            landed_index += 1;
            continue;
        }
        if (std.mem.eql(u8, segment.status, "deferred_high_risk") or
            std.mem.eql(u8, segment.status, "blocked_on_object_model"))
        {
            try std.testing.expect(deferred_index < deferred_slugs.len);
            try std.testing.expectEqualStrings(deferred_slugs[deferred_index], segment.slug);
            deferred_index += 1;
        }
    }
    try std.testing.expectEqual(landed_slugs.len, landed_index);
    try std.testing.expectEqual(deferred_slugs.len, deferred_index);
}

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (required_files) |rel| {
        const file_path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(file_path);
        const text = try guard.readUtf8File(io, allocator, file_path);
        allocator.free(text);
    }
    for (contracts) |contract| {
        const file_path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(file_path);
        const text = try guard.readUtf8File(io, allocator, file_path);
        defer allocator.free(text);
        for (contract.markers) |marker| {
            guard.requireMarker(text, marker) catch |err| {
                try guard.printLine(io, "PHASE8_LIBBPF_MISSING_MARKER_FILE={s}", .{contract.rel});
                try guard.printLine(io, "PHASE8_LIBBPF_MISSING_MARKER_VALUE={s}", .{marker});
                return err;
            };
        }
    }
    const manifest_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
    defer allocator.free(manifest_path);
    const manifest_source = try guard.readUtf8File(io, allocator, manifest_path);
    defer allocator.free(manifest_source);
    try checkManifest(allocator, manifest_source);
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE8_LIBBPF_SEGMENT_GATE_REQUIRED_FILE_COUNT=20", .{});
    try guard.printLine(io, "PHASE8_LIBBPF_SEGMENT_GATE_REQUIRED_MARKER_COUNT=52", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try std.testing.expectEqual(@as(usize, 20), required_files.len);
    try std.testing.expectEqual(@as(usize, 52), comptime blk: {
        var total: usize = 0;
        for (contracts) |contract| total += contract.markers.len;
        break :blk total;
    });
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST_CASE_COUNT=27", .{});
    try emitCounts(io);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try emitCounts(io);
}

// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const live_pass_marker = "PHASE8_LIBBPF_SEGMENT_GATE=pass";
// pub const self_test_pass_marker = "PHASE8_LIBBPF_SEGMENT_GATE_SELF_TEST=pass";
//
// const MANIFEST_PATH = [_][]const u8{
//     "tools/lib/bpf/zigux_segments/manifest.json",
// };
//
// const SURVEY_PATH = [_][]const u8{
//     "Documentation/zigux/phase8-libbpf-segment-survey.md",
// };
//
// const REVIEW_CHECKLIST_PATH = [_][]const u8{
//     "Documentation/zigux/review-checklist.md",
// };
//
// const BRIDGE_SLICE_PATH = [_][]const u8{
//     "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
// };
//
// const BRIDGE_BOUNDARY_SURVEY_PATH = [_][]const u8{
//     "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
// };
//
// const VALIDATOR_PATH = [_][]const u8{
//     "scripts\\zigux/validate_phase8.zig",
// };
//
// const BUILD_PATH = [_][]const u8{
//     "zigux/tests/phase8_libbpf_segments_only_build.zig",
// };
//
// const LIBBPF_SEGMENTS_TEST_PATH = [_][]const u8{
//     "zigux/tests/phase8_libbpf_segments.zig",
// };
//
// const VERIFY_PATH = [_][]const u8{
//     "tools/lib/bpf/zigux_segments/verify.zig",
// };
//
// const MAKEFILE_PATH = [_][]const u8{
//     "zigux/Makefile",
// };
//
// const BRIDGE_TEST_PATH = [_][]const u8{
//     "zigux/tests/phase8_file_path_handle_bridge.zig",
// };
//
// const BRIDGE_BUILD_PATH = [_][]const u8{
//     "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
// };
//
// const BRIDGE_BOUNDARY_GUARD_PATH = [_][]const u8{
//     "zigux/tests/phase8_file_path_handle_boundary_guard.zig",
// };
//
// const BRIDGE_MANIFEST_SYNC_PATH = [_][]const u8{
//     "zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig",
// };
//
// const BRIDGE_HELPER_PATH = [_][]const u8{
//     "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
// };
//
// const LANDED_SLUGS = [_][]const u8{
//     "logging-version-and-errno",
//     "pin-path-helpers",
//     "cpu-mask-parsing",
//     "type-name-helpers",
//     "fdinfo-map-info-helpers",
//     "map-reuse-compatibility",
//     "perf-buffer-poll-bookkeeping",
//     "fdinfo-path-and-reuse-name-footholds",
//     "ready-buffer-fd-lookup",
//     "ready-buffer-window-lookup",
//     "perf-buffer-wait-budget",
// };
//
// const DEFERRED_SLUGS = [_][]const u8{
//     "file-path-and-handle-bridge",
//     "perf-buffer-online-cpu-routing",
//     "skeleton-population",
//     "object-and-elf-loader",
//     "btf-relocation-and-program-load",
// };
//
// const SURVEY_MARKERS = [_][]const u8{
//     "The directly readable stable-output helper set therefore now keeps the aggregate verifier plus `cpu_mask.zig`, `cpu_mask_verify.zig`, `logging.zig`, `logging_verify.zig`, `pin_path.zig`, `pin_path_verify.zig`, `type_names.zig`, `type_names_verify.zig`, `perf_buffer_poll.zig`, `perf_buffer_wait_budget.zig`, `perf_buffer_poll_verify.zig`, `perf_buffer_ready_window.zig`, `online_cpu_routing.zig`, `online_cpu_routing_verify.zig`, `ready_buffer_attempt_verify.zig`, `ready_buffer_fd_verify.zig`, and `ready_buffer_window_verify.zig` explicit.",
//     "Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/logging_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`, `tools/lib/bpf/zigux_segments/pin_path_verify.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, and `tools/lib/bpf/zigux_segments/type_names_verify.zig` explicit.",
//     "The directly readable verifier packet now also keeps dedicated stable-output witnesses for cpu-mask parse, string-backed summary, reader-backed summary, auto-count, and fail-closed outputs, logging env/version/error outputs, perf-buffer wait-classification, poll-summary, execution-summary, and impossible-summary fail-closed outputs, pin-path map/program output and validation wrappers, online-CPU route CPU-index and buffer-FD wrappers, ready-buffer attempt wrappers, ready-buffer FD wrappers, ready-buffer window mapped-size and lookup-return wrappers, and type-name lookup plus formatter wrappers explicit beside the aggregate `verify.zig` replay surface.",
//     "This survey should therefore keep the helper-first packet and the shared wrapper-route vocabulary explicit together without promoting the still-deferred setup-side routing, reopen-flow, token-materialization, object-model, or bridge-heavy work into direct authenticated helper proof.",
// };
//
// const BRIDGE_SLICE_MARKERS = [_][]const u8{
//     "The shared file-path bridge destination already carries the bounded procfs path construction and fdinfo text parsing helpers, so this landed slice should stay explicitly smaller than direct file reads, descriptor ownership, or pinned-object reopen flow.",
//     "The shared bridge surface now already carries the reused-map-name chooser and compatibility comparison as landed helper-only behavior, and it should stay reviewable without widening into FD duplication, close-on-replacement, or pinned-map reopen side effects.",
// };
//
// const BRIDGE_BOUNDARY_SURVEY_MARKERS = [_][]const u8{
//     "Current `master` still keeps the mixed-source bridge packet reviewable, and authenticated contents readback now reaches the bridge-side helper and witness files directly again in this runtime.",
//     "That narrower split is therefore packet role rather than fetchability: the bridge helper and witness stay on the boundary side of the Phase 8 packet so this survey does not overclaim delivered procfs, bpffs, token, or fd-ownership behavior.",
//     "The timing-adjacent poll reminder also stays explicit through `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `zig run scripts\\zigux/check_phase8_perf_buffer_poll_gate.zig`, `make -C zigux phase8-perf-buffer-poll-test`, and the shared `phase8` routes; that dedicated packet keeps no standalone timer helper behavior, no standalone clockevent helper behavior, and no broader timeout-sensitive routing behavior explicit while the surrounding setup-side bridge remains deferred.",
// };
//
// const VALIDATOR_MARKERS = [_][]const u8{
//     "LIBBPF_SEGMENT_GATE_CHECKER = Path(\"scripts\\zigux/check_phase8_libbpf_segment_gate.zig\")",
//     "LIBBPF_SEGMENT_GATE_CHECKER,",
// };
//
// const MAKEFILE_MARKERS = [_][]const u8{
//     "phase8-validate:",
//     "phase8-libbpf-segments-test:",
//     "zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
//     "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
// };
//
// const BUILD_MARKERS = [_][]const u8{
//     "../../tools/lib/bpf/zigux_segments/verify.zig",
//     "phase8-libbpf-segment-verify-tests",
//     "Run focused Phase 8 libbpf segment verify build",
// };
//
// const LIBBPF_SEGMENTS_TEST_MARKERS = [_][]const u8{
//     "test \"phase 8 libbpf-segment compatibility witness keeps the focused verify-routing replay visible\" {",
//     "test \"phase 8 libbpf-segment compatibility witness keeps the shared no-timer poll boundary explicit\" {",
//     "test \"phase 8 libbpf-segment compatibility witness keeps the mixed-source bridge packet visible\" {",
//     "test \"phase 8 libbpf-segment compatibility witness keeps stable-output verifier shards visible\" {",
// };
//
// const VERIFY_MARKERS = [_][]const u8{
//     "resolveNextOnlineCpuRouteCpuIndexReturnAtIndex",
//     "resolveNextOnlineCpuRouteBufferFdAtIndex",
//     "resolveNextOnlineCpuRouteBufferFdReturnAtIndex",
//     "resolveReadyBufferFdAtAttempt",
//     "resolveReadyBufferFdLookupReturnAtAttempt",
//     "resolveReadyBufferWindowMappedSizeAtAttempt",
//     "resolveReadyBufferWindowMappedSizeReturnAtAttempt",
//     "resolveReadyBufferWindowLookupReturnAtAttempt",
//     "formatLibbpfBpfLinkType",
// };
//
// const BRIDGE_TEST_MARKERS = [_][]const u8{
//     "test \"phase 8 file-path handle bridge proof keeps the manifest-backed helper and deferred bridge split explicit\" {",
//     "test \"phase 8 file-path handle bridge helper stays wired into the Linux-style replay routes\" {",
//     "planning-only `resolveReusePinnedMapAttempt()` gating",
//     "planning-only `planTokenPreparation()` gating",
//     "try std.testing.expect(std.mem.indexOf(u8, helper_source, \"bpf_obj_get(\") == null);",
// };
//
// const BRIDGE_BUILD_MARKERS = [_][]const u8{
//     "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
//     "phase8_file_path_handle_bridge.zig",
//     "phase8-file-path-handle-bridge-tests",
//     "Run focused Phase 8 file-path-handle bridge tests",
// };
//
// const BRIDGE_BOUNDARY_GUARD_MARKERS = [_][]const u8{
//     "test \"phase 8 file-path-handle boundary guard keeps landed helper slices distinct from the deferred bridge\" {",
//     "\"slug\": \"fdinfo-map-info-helpers\"",
//     "\"slug\": \"map-reuse-compatibility\"",
//     "\"slug\": \"file-path-and-handle-bridge\"",
//     "planTokenPreparation",
// };
//
// const BRIDGE_MANIFEST_SYNC_MARKERS = [_][]const u8{
//     "test \"phase 8 file-path handle bridge manifest keeps the landed helper wording explicit\" {",
//     "\"lane_key\": \"P8-L13\"",
//     "\"id\": \"P8-L13-S07\"",
//     "\"slug\": \"file-path-and-handle-bridge\", \"status\": \"deferred_high_risk\", \"kind\": \"resource_boundary\"",
//     "planning-only token-readiness gating as a reviewable landed helper slice",
// };
//
// const BRIDGE_HELPER_MARKERS = [_][]const u8{
//     "pub fn resolveReusePinnedMapAttempt(",
//     "pub fn planTokenPreparation(",
// };
//
// fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
//     const text_manifest_path_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_manifest_path_path);
//     const text_manifest_path = try guard.readUtf8File(io, allocator, text_manifest_path_path);
//     defer allocator.free(text_manifest_path);
//     for (MANIFEST_PATH) |marker| try guard.requireMarker(text_manifest_path, marker);
//     const text_survey_path_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_survey_path_path);
//     const text_survey_path = try guard.readUtf8File(io, allocator, text_survey_path_path);
//     defer allocator.free(text_survey_path);
//     for (SURVEY_PATH) |marker| try guard.requireMarker(text_survey_path, marker);
//     const text_review_checklist_path_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_review_checklist_path_path);
//     const text_review_checklist_path = try guard.readUtf8File(io, allocator, text_review_checklist_path_path);
//     defer allocator.free(text_review_checklist_path);
//     for (REVIEW_CHECKLIST_PATH) |marker| try guard.requireMarker(text_review_checklist_path, marker);
//     const text_bridge_slice_path_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_bridge_slice_path_path);
//     const text_bridge_slice_path = try guard.readUtf8File(io, allocator, text_bridge_slice_path_path);
//     defer allocator.free(text_bridge_slice_path);
//     for (BRIDGE_SLICE_PATH) |marker| try guard.requireMarker(text_bridge_slice_path, marker);
//     const text_bridge_boundary_survey_path_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_bridge_boundary_survey_path_path);
//     const text_bridge_boundary_survey_path = try guard.readUtf8File(io, allocator, text_bridge_boundary_survey_path_path);
//     defer allocator.free(text_bridge_boundary_survey_path);
//     for (BRIDGE_BOUNDARY_SURVEY_PATH) |marker| try guard.requireMarker(text_bridge_boundary_survey_path, marker);
//     const text_validator_path_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_validator_path_path);
//     const text_validator_path = try guard.readUtf8File(io, allocator, text_validator_path_path);
//     defer allocator.free(text_validator_path);
//     for (VALIDATOR_PATH) |marker| try guard.requireMarker(text_validator_path, marker);
//     const text_build_path_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_build_path_path);
//     const text_build_path = try guard.readUtf8File(io, allocator, text_build_path_path);
//     defer allocator.free(text_build_path);
//     for (BUILD_PATH) |marker| try guard.requireMarker(text_build_path, marker);
//     const text_libbpf_segments_test_path_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_libbpf_segments_test_path_path);
//     const text_libbpf_segments_test_path = try guard.readUtf8File(io, allocator, text_libbpf_segments_test_path_path);
//     defer allocator.free(text_libbpf_segments_test_path);
//     for (LIBBPF_SEGMENTS_TEST_PATH) |marker| try guard.requireMarker(text_libbpf_segments_test_path, marker);
//     const text_verify_path_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_verify_path_path);
//     const text_verify_path = try guard.readUtf8File(io, allocator, text_verify_path_path);
//     defer allocator.free(text_verify_path);
//     for (VERIFY_PATH) |marker| try guard.requireMarker(text_verify_path, marker);
//     const text_makefile_path_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_makefile_path_path);
//     const text_makefile_path = try guard.readUtf8File(io, allocator, text_makefile_path_path);
//     defer allocator.free(text_makefile_path);
//     for (MAKEFILE_PATH) |marker| try guard.requireMarker(text_makefile_path, marker);
//     const text_bridge_test_path_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_bridge_test_path_path);
//     const text_bridge_test_path = try guard.readUtf8File(io, allocator, text_bridge_test_path_path);
//     defer allocator.free(text_bridge_test_path);
//     for (BRIDGE_TEST_PATH) |marker| try guard.requireMarker(text_bridge_test_path, marker);
//     const text_bridge_build_path_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_bridge_build_path_path);
//     const text_bridge_build_path = try guard.readUtf8File(io, allocator, text_bridge_build_path_path);
//     defer allocator.free(text_bridge_build_path);
//     for (BRIDGE_BUILD_PATH) |marker| try guard.requireMarker(text_bridge_build_path, marker);
//     const text_bridge_boundary_guard_path_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_bridge_boundary_guard_path_path);
//     const text_bridge_boundary_guard_path = try guard.readUtf8File(io, allocator, text_bridge_boundary_guard_path_path);
//     defer allocator.free(text_bridge_boundary_guard_path);
//     for (BRIDGE_BOUNDARY_GUARD_PATH) |marker| try guard.requireMarker(text_bridge_boundary_guard_path, marker);
//     const text_bridge_manifest_sync_path_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_bridge_manifest_sync_path_path);
//     const text_bridge_manifest_sync_path = try guard.readUtf8File(io, allocator, text_bridge_manifest_sync_path_path);
//     defer allocator.free(text_bridge_manifest_sync_path);
//     for (BRIDGE_MANIFEST_SYNC_PATH) |marker| try guard.requireMarker(text_bridge_manifest_sync_path, marker);
//     const text_bridge_helper_path_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_bridge_helper_path_path);
//     const text_bridge_helper_path = try guard.readUtf8File(io, allocator, text_bridge_helper_path_path);
//     defer allocator.free(text_bridge_helper_path);
//     for (BRIDGE_HELPER_PATH) |marker| try guard.requireMarker(text_bridge_helper_path, marker);
//     const text_landed_slugs_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_landed_slugs_path);
//     const text_landed_slugs = try guard.readUtf8File(io, allocator, text_landed_slugs_path);
//     defer allocator.free(text_landed_slugs);
//     for (LANDED_SLUGS) |marker| try guard.requireMarker(text_landed_slugs, marker);
//     const text_deferred_slugs_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_deferred_slugs_path);
//     const text_deferred_slugs = try guard.readUtf8File(io, allocator, text_deferred_slugs_path);
//     defer allocator.free(text_deferred_slugs);
//     for (DEFERRED_SLUGS) |marker| try guard.requireMarker(text_deferred_slugs, marker);
//     const text_survey_markers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_survey_markers_path);
//     const text_survey_markers = try guard.readUtf8File(io, allocator, text_survey_markers_path);
//     defer allocator.free(text_survey_markers);
//     for (SURVEY_MARKERS) |marker| try guard.requireMarker(text_survey_markers, marker);
//     const text_bridge_slice_markers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_bridge_slice_markers_path);
//     const text_bridge_slice_markers = try guard.readUtf8File(io, allocator, text_bridge_slice_markers_path);
//     defer allocator.free(text_bridge_slice_markers);
//     for (BRIDGE_SLICE_MARKERS) |marker| try guard.requireMarker(text_bridge_slice_markers, marker);
//     const text_bridge_boundary_survey_markers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_bridge_boundary_survey_markers_path);
//     const text_bridge_boundary_survey_markers = try guard.readUtf8File(io, allocator, text_bridge_boundary_survey_markers_path);
//     defer allocator.free(text_bridge_boundary_survey_markers);
//     for (BRIDGE_BOUNDARY_SURVEY_MARKERS) |marker| try guard.requireMarker(text_bridge_boundary_survey_markers, marker);
//     const text_validator_markers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_validator_markers_path);
//     const text_validator_markers = try guard.readUtf8File(io, allocator, text_validator_markers_path);
//     defer allocator.free(text_validator_markers);
//     for (VALIDATOR_MARKERS) |marker| try guard.requireMarker(text_validator_markers, marker);
//     const text_makefile_markers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_makefile_markers_path);
//     const text_makefile_markers = try guard.readUtf8File(io, allocator, text_makefile_markers_path);
//     defer allocator.free(text_makefile_markers);
//     for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text_makefile_markers, marker);
//     const text_build_markers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_build_markers_path);
//     const text_build_markers = try guard.readUtf8File(io, allocator, text_build_markers_path);
//     defer allocator.free(text_build_markers);
//     for (BUILD_MARKERS) |marker| try guard.requireMarker(text_build_markers, marker);
//     const text_libbpf_segments_test_markers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_libbpf_segments_test_markers_path);
//     const text_libbpf_segments_test_markers = try guard.readUtf8File(io, allocator, text_libbpf_segments_test_markers_path);
//     defer allocator.free(text_libbpf_segments_test_markers);
//     for (LIBBPF_SEGMENTS_TEST_MARKERS) |marker| try guard.requireMarker(text_libbpf_segments_test_markers, marker);
//     const text_verify_markers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_verify_markers_path);
//     const text_verify_markers = try guard.readUtf8File(io, allocator, text_verify_markers_path);
//     defer allocator.free(text_verify_markers);
//     for (VERIFY_MARKERS) |marker| try guard.requireMarker(text_verify_markers, marker);
//     const text_bridge_test_markers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_bridge_test_markers_path);
//     const text_bridge_test_markers = try guard.readUtf8File(io, allocator, text_bridge_test_markers_path);
//     defer allocator.free(text_bridge_test_markers);
//     for (BRIDGE_TEST_MARKERS) |marker| try guard.requireMarker(text_bridge_test_markers, marker);
//     const text_bridge_build_markers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_bridge_build_markers_path);
//     const text_bridge_build_markers = try guard.readUtf8File(io, allocator, text_bridge_build_markers_path);
//     defer allocator.free(text_bridge_build_markers);
//     for (BRIDGE_BUILD_MARKERS) |marker| try guard.requireMarker(text_bridge_build_markers, marker);
//     const text_bridge_boundary_guard_markers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_bridge_boundary_guard_markers_path);
//     const text_bridge_boundary_guard_markers = try guard.readUtf8File(io, allocator, text_bridge_boundary_guard_markers_path);
//     defer allocator.free(text_bridge_boundary_guard_markers);
//     for (BRIDGE_BOUNDARY_GUARD_MARKERS) |marker| try guard.requireMarker(text_bridge_boundary_guard_markers, marker);
//     const text_bridge_manifest_sync_markers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_bridge_manifest_sync_markers_path);
//     const text_bridge_manifest_sync_markers = try guard.readUtf8File(io, allocator, text_bridge_manifest_sync_markers_path);
//     defer allocator.free(text_bridge_manifest_sync_markers);
//     for (BRIDGE_MANIFEST_SYNC_MARKERS) |marker| try guard.requireMarker(text_bridge_manifest_sync_markers, marker);
//     const text_bridge_helper_markers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/manifest.json");
//     defer allocator.free(text_bridge_helper_markers_path);
//     const text_bridge_helper_markers = try guard.readUtf8File(io, allocator, text_bridge_helper_markers_path);
//     defer allocator.free(text_bridge_helper_markers);
//     for (BRIDGE_HELPER_MARKERS) |marker| try guard.requireMarker(text_bridge_helper_markers, marker);
// }
//
// fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
//     try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
//     try guard.printLine(io, "{s}", .{self_test_pass_marker});
//     return 0;
// }
//
// pub fn main(init: std.process.Init) !void {
//     const allocator = init.gpa;
//     const io = init.io;
//     const args = try init.minimal.args.toSlice(allocator);
//
//     var self_test = false;
//     var explicit_root: ?[]const u8 = null;
//     var index: usize = 1;
//     while (index < args.len) : (index += 1) {
//         const arg = args[index];
//         if (std.mem.eql(u8, arg, "--self-test")) {
//             self_test = true;
//             continue;
//         }
//         if (std.mem.eql(u8, arg, "--root")) {
//             if (index + 1 >= args.len) std.process.exit(2);
//             index += 1;
//             explicit_root = args[index];
//             continue;
//         }
//     }
//
//     const root = explicit_root orelse try guard.repoRootFromScript(allocator);
//     defer if (explicit_root == null) allocator.free(root);
//
//     if (self_test) {
//         std.process.exit(try runSelfTest(io, allocator));
//     }
//
//     checkRepo(io, allocator, root) catch {
//         std.process.exit(1);
//     };
//     try guard.printLine(io, "{s}", .{live_pass_marker});
// }
//
