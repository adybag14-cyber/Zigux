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
    try expectContains(note, "no direct procfs reads");
    try expectContains(note, "no `bpf_obj_get()` reopen flow");
    try expectContains(note, "map-reuse-compatibility remains queued");
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
