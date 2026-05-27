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
    try expectContains(note, "terminated-prefix");
    try expectContains(note, "truncated-fixed-width");
    try expectContains(note, "incomplete-fdinfo reuse planning");
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

test "phase 8 file-path handle bridge proof keeps the manifest-backed helper and deferred bridge split explicit" {
    const manifest = try readWorkspaceFile(
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/manifest.json",
        48 * 1024,
    );
    defer std.testing.allocator.free(manifest);

    try expectContains(
        manifest,
        "\"slug\": \"fdinfo-map-info-helpers\",\n      \"status\": \"starter_landed\"",
    );
    try expectContains(
        manifest,
        "\"slug\": \"map-reuse-compatibility\",\n      \"status\": \"starter_landed\"",
    );
    try expectContains(
        manifest,
        "\"slug\": \"fdinfo-path-and-reuse-name-footholds\",\n      \"status\": \"starter_landed\"",
    );
    try expectContains(
        manifest,
        "The shared file-path bridge destination already carries the bounded procfs path construction and fdinfo text parsing helpers, so this landed slice should stay explicitly smaller than direct file reads, descriptor ownership, or pinned-object reopen flow.",
    );
    try expectContains(
        manifest,
        "The shared bridge surface now already carries the reused-map-name chooser and compatibility comparison as landed helper-only behavior, and it should stay reviewable without widening into FD duplication, close-on-replacement, or pinned-map reopen side effects.",
    );
    try expectContains(
        manifest,
        "This materializes the shared bridge destination with side-effect-free pathname shaping and bounded reused-map name retention while keeping procfs reads, fdinfo parsing, and reuse comparison logic deferred.",
    );
    try expectContains(
        manifest,
        "\"slug\": \"file-path-and-handle-bridge\",\n      \"status\": \"deferred_high_risk\",\n      \"kind\": \"resource_boundary\"",
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

    try expectContains(helper_source, "pub fn mapReuseObservationFromFdinfo(");
    try expectContains(helper_source, "pub fn summarizeMapReuseCompatibility(");
    try expectContains(helper_source, "pub fn isMapReuseCompatible(");
    try expectContains(helper_source, "pub fn resolveReusePinnedMapAttempt(");
    try expectContains(helper_source, "pub fn planTokenPreparation(");
    try expectContains(helper_source, ".disposition = .incomplete_fdinfo_map_info");
    try expectContains(helper_source, ".disposition = .ready_for_reopen_attempt");
    try expectContains(helper_source, ".should_attempt_reopen = true");
    try expectContains(helper_source, ".disposition = .ready_for_token_open_attempt");
    try expectContains(helper_source, ".should_attempt_token_open = true");
    try expectContains(helper_source, "terminated_prefix");
    try expectContains(helper_source, "truncated_fixed_width");
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "bpf_obj_get(") == null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "F_DUPFD_CLOEXEC") == null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "std.posix.open") == null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "openat(") == null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "openFile") == null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "readFile") == null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "fcntl(") == null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "std.posix.dup") == null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "dup2(") == null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "dup3(") == null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "std.posix.close") == null);
    try std.testing.expect(std.mem.indexOf(u8, helper_source, "close(") == null);
}

test "phase 8 file-path-handle bridge helper keeps errno-shaped wrapper boundaries explicit" {
    var path_buffer: [64]u8 = undefined;
    try std.testing.expectEqual(
        @as(i32, "/proc/self/fdinfo/21".len),
        file_path_handle_bridge.buildProcFdinfoPathReturn(&path_buffer, null, 21),
    );
    try std.testing.expectEqualStrings(
        "/proc/self/fdinfo/21",
        path_buffer[0.."/proc/self/fdinfo/21".len],
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        file_path_handle_bridge.buildCurrentProcessFdinfoPathReturn(&path_buffer, -1, 21),
    );

    var name_buffer: [16]u8 = undefined;
    try std.testing.expectEqual(
        @as(i32, "stats_map".len),
        file_path_handle_bridge.resolveReusedMapNameReturn(&name_buffer, "stats_map\x00"),
    );
    try std.testing.expectEqualStrings("stats_map", name_buffer[0.."stats_map".len]);

    var tiny_name_buffer: [4]u8 = undefined;
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NAMETOOLONG)),
        file_path_handle_bridge.resolveReusedMapNameReturn(&tiny_name_buffer, "stats_map\x00"),
    );
}

test "phase 8 file-path-handle bridge helper keeps proc fdinfo path formatting explicit" {
    var buffer: [64]u8 = undefined;
    try std.testing.expectEqualStrings(
        "/proc/777/fdinfo/9",
        try file_path_handle_bridge.buildCurrentProcessFdinfoPath(&buffer, 777, 9),
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
