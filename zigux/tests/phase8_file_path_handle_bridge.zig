const std = @import("std");
const file_path_handle_bridge = @import("file_path_handle_bridge");

test "phase 8 file-path-handle bridge segment imports cleanly" {
    _ = file_path_handle_bridge;
}

test "phase 8 file-path-handle bridge builds proc fdinfo paths without widening into io" {
    var buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/proc/4321/fdinfo/9",
        try file_path_handle_bridge.buildFdinfoPath(&buffer, 4321, 9),
    );
    try std.testing.expectError(error.InvalidFd, file_path_handle_bridge.buildFdinfoPath(&buffer, 4321, -3));
}

test "phase 8 file-path-handle bridge keeps the current-process fdinfo helper bounded" {
    var actual: [64]u8 = undefined;
    var expected: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        try std.fmt.bufPrint(&expected, "/proc/{d}/fdinfo/{d}", .{ std.os.linux.getpid(), 12 }),
        try file_path_handle_bridge.buildCurrentProcessFdinfoPath(&actual, 12),
    );
    try std.testing.expectError(error.InvalidFd, file_path_handle_bridge.buildCurrentProcessFdinfoPath(&actual, -2));
}

test "phase 8 file-path-handle bridge parses bounded fdinfo map metadata" {
    const info = try file_path_handle_bridge.parseMapInfoFromFdinfo(
        "map_type:\t3\n" ++
            "key_size:\t4\n" ++
            "value_size:\t8\n" ++
            "max_entries:\t256\n" ++
            "map_flags:\t0x20\n",
    );

    try std.testing.expectEqual(@as(u32, 3), info.map_type);
    try std.testing.expectEqual(@as(u32, 4), info.key_size);
    try std.testing.expectEqual(@as(u32, 8), info.value_size);
    try std.testing.expectEqual(@as(u32, 256), info.max_entries);
    try std.testing.expectEqual(@as(u32, 0x20), info.map_flags);
}

test "phase 8 file-path-handle bridge keeps missing fdinfo fields explicit" {
    try std.testing.expectError(error.MissingMaxEntries, file_path_handle_bridge.parseMapInfoFromFdinfo(
        "map_type:\t3\n" ++
            "key_size:\t4\n" ++
            "value_size:\t8\n" ++
            "map_flags:\t0x20\n",
    ));
}
