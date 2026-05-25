const std = @import("std");
const file_path_handle_bridge = @import("file_path_handle_bridge");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readWorkspaceFile(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(limit),
    );
}

test "phase 8 file-path-handle bridge docs keep the bounded fdinfo helper explicit" {
    const note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(note);

    try expectContains(note, "\"/proc/%d/fdinfo/%d\"");
    try expectContains(note, "map_type");
    try expectContains(note, "key_size");
    try expectContains(note, "value_size");
    try expectContains(note, "max_entries");
    try expectContains(note, "map_flags");
    try expectContains(note, "map_extra");
    try expectContains(note, "no direct procfs reads");
    try expectContains(note, "no `bpf_obj_get()` reopen flow");
    try expectContains(note, "helper-only `mapReuseObservationFromFdinfo()` handoff");
    try expectContains(note, "planning-only `resolveReusePinnedMapAttempt()` gating");
    try expectContains(note, "planning-only `planTokenPreparation()` gating");
    try expectContains(note, "no live bpffs opens");
    try expectContains(note, "no descriptor replacement, transfer, or close ownership semantics");
}

test "phase 8 file-path-handle bridge helper stays wired into its focused Phase 8 build shard" {
    const focused_build_file = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
        16 * 1024,
    );
    defer std.testing.allocator.free(focused_build_file);

    try expectContains(focused_build_file, "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    try expectContains(focused_build_file, "phase8_file_path_handle_bridge.zig");
    try expectContains(focused_build_file, "phase8-file-path-handle-bridge-tests");
}

test "phase 8 file-path-handle bridge helper stays wired into the shared Phase 8 build shard" {
    const shared_build_file = try readWorkspaceFile(
        std.testing.allocator,
        "zigux/tests/phase8_build.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(shared_build_file);

    try expectContains(shared_build_file, "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    try expectContains(shared_build_file, "phase8_file_path_handle_bridge.zig");
    try expectContains(shared_build_file, "phase8-file-path-handle-bridge-tests");
}

test "phase 8 file-path-handle bridge helper stays wired into the Linux-style replay routes" {
    const makefile = try readWorkspaceFile(std.testing.allocator, "zigux/Makefile", 64 * 1024);
    defer std.testing.allocator.free(makefile);

    try expectContains(makefile, "phase8-file-path-handle-bridge-test:");
    try expectContains(makefile, "zigux/tests/phase8_file_path_handle_bridge_only_build.zig");
    try expectContains(makefile, "phase8-test:");
    try expectContains(makefile, "zigux/tests/phase8_build.zig");
    try expectContains(makefile, "phase8:");
    try expectContains(makefile, "phase8-file-path-handle-bridge-test");
}

test "phase 8 file-path-handle bridge proof keeps helper-local routing evidence smaller than deferred setup-side routing" {
    const boundary_note = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(boundary_note);

    try expectContains(boundary_note, "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig`");
    try expectContains(boundary_note, "advanceOnlineCpuCursor()");
    try expectContains(boundary_note, "summarizeNextOnlineCpuRoute()");
    try expectContains(boundary_note, "summarizeOnlineCpuRouting()");
    try expectContains(boundary_note, "It also does not claim the deferred `perf-buffer-online-cpu-routing` packet");
    try expectContains(boundary_note, "`libbpf_num_possible_cpus()`");
    try expectContains(boundary_note, "online CPU filtering");
    try expectContains(boundary_note, "per-CPU perf-event-array map updates");
    try expectContains(boundary_note, "per-CPU `perf_event_open()` setup");
    try expectContains(boundary_note, "`mmap()` setup");
    try expectContains(boundary_note, "`PERF_EVENT_IOC_ENABLE` enablement");
    try expectContains(boundary_note, "epoll-backed perf FD registration");
    try expectContains(boundary_note, "poll waits");

    const routing_helper = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/online_cpu_routing.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(routing_helper);

    try expectContains(routing_helper, "pub fn advanceOnlineCpuCursor(");
    try expectContains(routing_helper, "pub fn summarizeNextOnlineCpuRoute(");
    try expectContains(routing_helper, "pub fn summarizeOnlineCpuRouting(");
    try expectContains(
        routing_helper,
        "test \"summarizeOnlineCpuRouting reports the first routed online CPU whose fd slot is empty\" {",
    );
}

test "phase 8 file-path-handle bridge proof keeps the manifest-backed helper and deferred bridge split explicit" {
    const manifest = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/manifest.json",
        48 * 1024,
    );
    defer std.testing.allocator.free(manifest);

    try expectContains(
        manifest,
        "\"slug\": \"fdinfo-map-info-helpers\", \"status\": \"starter_landed\"",
    );
    try expectContains(
        manifest,
        "\"why_now\": \"The shared file-path bridge destination already carries the bounded procfs path construction and fdinfo text parsing helpers, so this landed slice should stay explicitly smaller than direct file reads, descriptor ownership, or pinned-object reopen flow.\"",
    );
    try expectContains(
        manifest,
        "\"slug\": \"map-reuse-compatibility\", \"status\": \"starter_landed\"",
    );
    try expectContains(
        manifest,
        "\"why_now\": \"The shared bridge surface now already carries the reused-map-name chooser and compatibility comparison as landed helper-only behavior, and it should stay reviewable without widening into FD duplication, close-on-replacement, or pinned-map reopen side effects.\"",
    );
    try expectContains(
        manifest,
        "\"slug\": \"file-path-and-handle-bridge\", \"status\": \"deferred_high_risk\", \"kind\": \"resource_boundary\"",
    );
    try expectContains(
        manifest,
        "bpf_object_prepare_token() and bpf_object__reuse_map() handle-bridging paths",
    );
    try expectContains(
        manifest,
        "This remaining file-path and handle bridge still crosses real procfs reads, bpffs opens, token creation, bpf_obj_get() reopen flow, and fd ownership semantics, so the helper-first packet should keep it deferred.",
    );
    try expectContains(manifest, "direct procfs reads and descriptor ownership flow");
    try expectContains(manifest, "token creation, bpffs reopen flow, and other fd-handle bridge side effects");
}

test "phase 8 file-path-handle bridge helper source keeps planning-only bridge boundaries explicit" {
    const helper_source = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(helper_source);

    try expectContains(helper_source, "pub fn resolveReusePinnedMapAttempt(");
    try expectContains(helper_source, "pub fn planTokenPreparation(");
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "bpf_obj_get(") == null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "F_DUPFD_CLOEXEC") == null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "/sys/fs/bpf") == null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "std.posix.open") == null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "openat(") == null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "openFile") == null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "readFile") == null);
}

test "phase 8 file-path-handle bridge proof keeps the current libbpf survey role-only bridge split explicit" {
    const libbpf_survey = try readWorkspaceFile(
        std.testing.allocator,
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        48 * 1024,
    );
    defer std.testing.allocator.free(libbpf_survey);

    try expectContains(
        libbpf_survey,
        "Current authenticated helper readback in this runtime now serves only the narrow bridge-side reminder packet directly: the helper set above stays the exact authenticated helper anchor, while the same contents path now returns `tools/lib/bpf/zigux_segments/manifest.json`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, and `Documentation/zigux/phase8-file-path-handle-bridge-slice.md` on current `master`. The broader bridge helper and focused build-route companions, including `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` and `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, remain public-tree-backed reminder vocabulary until the same authenticated contents path serves them directly again. Keep those bridge-facing paths explicit without folding them back into the exact helper set or promoting the deferred resource boundary into helper-first proof.",
    );
    try expectContains(
        libbpf_survey,
        "Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/logging_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`, `tools/lib/bpf/zigux_segments/pin_path_verify.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, and `tools/lib/bpf/zigux_segments/type_names_verify.zig` explicit.",
    );
    try expectContains(libbpf_survey, "`zigux/tests/phase8_verify_routing_gap.zig`");
    try expectContains(libbpf_survey, "`zigux/tests/phase8_verify_routing_gap_only_build.zig`");
    try expectContains(
        libbpf_survey,
        "This survey should therefore keep the helper-first packet and the shared wrapper-route vocabulary explicit together without promoting the still-deferred setup-side routing, reopen-flow, token-materialization, object-model, or bridge-heavy work into direct authenticated helper proof.",
    );
}

test "phase 8 file-path-handle bridge helper keeps proc fdinfo path formatting explicit" {
    var buffer: [64]u8 = undefined;
    try std.testing.expectEqualStrings(
        "/proc/777/fdinfo/9",
        try file_path_handle_bridge.buildProcFdinfoPath(&buffer, 777, 9),
    );
}

test "phase 8 file-path-handle bridge helper keeps fdinfo map info parsing compact" {
    const parsed = try file_path_handle_bridge.parseFdinfoMapInfo(
        \\map_type: 5
        \\key_size: 8
        \\value_size: 16
        \\max_entries: 1024
        \\map_flags: 0x20
        \\map_extra: 0X2A
    );
    const summary = file_path_handle_bridge.summarizeFdinfoMapInfo(parsed);

    try std.testing.expectEqual(@as(?u32, 5), parsed.map_type);
    try std.testing.expectEqual(@as(?u32, 0x20), parsed.map_flags);
    try std.testing.expectEqual(@as(?u64, 42), parsed.map_extra);
    try std.testing.expectEqual(@as(usize, 6), summary.parsed_field_count);
    try std.testing.expect(summary.has_complete_legacy_fields);
    try std.testing.expect(summary.has_map_extra);
}

test "phase 8 file-path-handle bridge helper keeps malformed fdinfo values explicit" {
    var info = file_path_handle_bridge.FdinfoMapInfo{};
    try std.testing.expectError(
        error.InvalidInteger,
        file_path_handle_bridge.applyFdinfoMapInfoLine(&info, "map_flags:\t-1"),
    );
    try std.testing.expectError(
        error.MissingSeparator,
        file_path_handle_bridge.parseFdinfoLine("map_type"),
    );
}
