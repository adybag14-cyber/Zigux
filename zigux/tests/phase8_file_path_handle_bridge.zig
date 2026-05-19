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

test "phase 8 file-path handle bridge docs keep the bounded fdinfo helper explicit" {
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

test "phase 8 file-path handle bridge helper stays wired into its focused Phase 8 build shard" {
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

test "phase 8 file-path handle bridge helper stays wired into the shared Phase 8 build shard" {
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

test "phase 8 file-path handle bridge proof keeps helper-local routing evidence smaller than deferred setup-side routing" {
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
    try expectContains(boundary_note, "per-CPU `perf_event_open()` setup");
    try expectContains(boundary_note, "epoll-backed perf FD registration");

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

test "phase 8 file-path handle bridge proof keeps the manifest-backed helper and deferred bridge split explicit" {
    const manifest = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/manifest.json",
        48 * 1024,
    );
    defer std.testing.allocator.free(manifest);

    try expectContains(
        manifest,
        "\"slug\": \"fdinfo-map-info-helpers\",\n \"status\": \"starter_landed\"",
    );
    try expectContains(
        manifest,
        "\"why_now\": \"This remains a bounded next helper once Zigux chooses to materialize the shared file-path bridge surface; until then the reviewable procfs path construction and fdinfo text parsing should stay explicitly smaller than direct file reads, descriptor ownership, or pinned-object reopen flow.\"",
    );
    try expectContains(
        manifest,
        "\"slug\": \"map-reuse-compatibility\",\n \"status\": \"starter_landed\"",
    );
    try expectContains(
        manifest,
        "\"why_now\": \"This remains a bounded next helper once the shared bridge surface exists; the reused-map-name chooser and compatibility comparison are still reviewable without widening into FD duplication, close-on-replacement, or pinned-map reopen side effects.\"",
    );
    try expectContains(
        manifest,
        "\"slug\": \"file-path-and-handle-bridge\",\n \"status\": \"deferred_high_risk\"",
    );
    try expectContains(
        manifest,
        "This remaining file-path and handle bridge still crosses real procfs reads, bpffs opens, token creation, bpf_obj_get() reopen flow, and fd ownership semantics, so the helper-first packet should keep it deferred.",
    );
    try expectContains(manifest, "direct procfs reads and descriptor ownership flow");
    try expectContains(manifest, "token creation, bpffs reopen flow, and other fd-handle bridge side effects");
}

test "phase 8 file-path handle bridge helper keeps proc fdinfo path formatting explicit" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/proc/777/fdinfo/9",
        try file_path_handle_bridge.buildProcFdinfoPath(&buffer, 777, 9),
    );
}

test "phase 8 file-path handle bridge helper keeps fdinfo map info parsing compact" {
    const parsed = try file_path_handle_bridge.parseFdinfoMapInfo(
        \\map_type: 5
        \\key_size: 8
        \\value_size: 16
        \\max_entries: 1024
        \\map_flags: 0x20
    );

    const summary = file_path_handle_bridge.summarizeFdinfoMapInfo(parsed);

    try std.testing.expectEqual(@as(?u32, 5), parsed.map_type);
    try std.testing.expectEqual(@as(?u32, 0x20), parsed.map_flags);
    try std.testing.expectEqual(@as(usize, 5), summary.parsed_field_count);
    try std.testing.expect(summary.has_complete_legacy_fields);
}

test "phase 8 file-path handle bridge helper keeps malformed fdinfo values explicit" {
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
