const std = @import("std");
const file_path_handle_bridge = @import("file_path_handle_bridge");

test "phase 8 file-path-handle bridge segment imports cleanly" {
    _ = file_path_handle_bridge;
}

test "phase 8 file-path-handle bridge builds proc fdinfo paths without widening into io" {
    var buffer: [64]u8 = undefined;
    var short_buffer: [8]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/proc/4321/fdinfo/9",
        try file_path_handle_bridge.buildFdinfoPath(&buffer, 4321, 9),
    );
    try std.testing.expectError(error.InvalidPid, file_path_handle_bridge.buildFdinfoPath(&buffer, 0, 9));
    try std.testing.expectError(error.InvalidFd, file_path_handle_bridge.buildFdinfoPath(&buffer, 4321, -3));
    try std.testing.expectError(error.PathTooLong, file_path_handle_bridge.buildFdinfoPath(&short_buffer, 4321, 9));
}

test "phase 8 file-path-handle bridge plans token preparation without claiming live bpffs io" {
    const prevented = file_path_handle_bridge.planTokenPreparation("");
    try std.testing.expectEqual(
        file_path_handle_bridge.TokenPreparationDisposition.prevented,
        prevented.disposition,
    );
    try std.testing.expectEqualStrings("", prevented.bpffs_path);
    try std.testing.expectEqual(@as(?file_path_handle_bridge.TokenPreparationLogLevel, null), prevented.log_level);
    try std.testing.expect(!prevented.requiresBpffsOpen());
    try std.testing.expect(!prevented.requiresTokenCreate());

    const optional = file_path_handle_bridge.planTokenPreparation(null);
    try std.testing.expectEqual(
        file_path_handle_bridge.TokenPreparationDisposition.optional_probe,
        optional.disposition,
    );
    try std.testing.expectEqualStrings(file_path_handle_bridge.default_bpf_fs_path, optional.bpffs_path);
    try std.testing.expectEqual(file_path_handle_bridge.TokenPreparationLogLevel.debug, optional.log_level.?);
    try std.testing.expect(optional.requiresBpffsOpen());
    try std.testing.expect(optional.requiresTokenCreate());

    const mandatory = file_path_handle_bridge.planTokenPreparation("/custom/bpffs");
    try std.testing.expectEqual(
        file_path_handle_bridge.TokenPreparationDisposition.mandatory_probe,
        mandatory.disposition,
    );
    try std.testing.expectEqualStrings("/custom/bpffs", mandatory.bpffs_path);
    try std.testing.expectEqual(file_path_handle_bridge.TokenPreparationLogLevel.warn, mandatory.log_level.?);
    try std.testing.expect(mandatory.requiresBpffsOpen());
    try std.testing.expect(mandatory.requiresTokenCreate());
}

test "phase 8 file-path-handle bridge parses bounded fdinfo map metadata" {
    const info = try file_path_handle_bridge.parseMapInfoFromFdinfo(
        "pos:\t0\n" ++
            "flags:\t02000002\n" ++
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

test "phase 8 file-path-handle bridge accepts reordered fields and surrounding whitespace" {
    const info = try file_path_handle_bridge.parseMapInfoFromFdinfo(
        "map_flags:   512\r\n" ++
            "max_entries:\t128\r\n" ++
            "value_size:\t 8\r\n" ++
            "key_size:\t4\r\n" ++
            "map_type:\t1\r\n",
    );

    try std.testing.expectEqual(@as(u32, 1), info.map_type);
    try std.testing.expectEqual(@as(u32, 4), info.key_size);
    try std.testing.expectEqual(@as(u32, 8), info.value_size);
    try std.testing.expectEqual(@as(u32, 128), info.max_entries);
    try std.testing.expectEqual(@as(u32, 512), info.map_flags);
}

test "phase 8 file-path-handle bridge keeps reused-map name selection bounded and explicit" {
    try std.testing.expectEqualStrings(
        "process_pinned_map",
        file_path_handle_bridge.chooseReusedMapName("process_pinned_map", "process_pinned_"),
    );
    try std.testing.expectEqualStrings(
        "ringbuf_map",
        file_path_handle_bridge.chooseReusedMapName("ringbuf_map_local", "ringbuf_map"),
    );
    try std.testing.expectEqualStrings(
        "different_prefix",
        file_path_handle_bridge.chooseReusedMapName("process_pinned_map", "different_prefix"),
    );
}

test "phase 8 file-path-handle bridge keeps missing duplicate and malformed fdinfo fields explicit" {
    try std.testing.expectError(error.MissingMaxEntries, file_path_handle_bridge.parseMapInfoFromFdinfo(
        "map_type:\t3\n" ++
            "key_size:\t4\n" ++
            "value_size:\t8\n" ++
            "map_flags:\t0x20\n",
    ));
    try std.testing.expectError(error.DuplicateField, file_path_handle_bridge.parseMapInfoFromFdinfo(
        "map_type:\t3\n" ++
            "key_size:\t4\n" ++
            "value_size:\t8\n" ++
            "max_entries:\t256\n" ++
            "map_flags:\t0x20\n" ++
            "map_flags:\t0x40\n",
    ));
    try std.testing.expectError(error.InvalidValue, file_path_handle_bridge.parseMapInfoFromFdinfo(
        "map_type:\t3\n" ++
            "key_size:\t4\n" ++
            "value_size:\t8\n" ++
            "max_entries:\t256\n" ++
            "map_flags:\t-1\n",
    ));
    try std.testing.expectError(error.InvalidValue, file_path_handle_bridge.parseMapInfoFromFdinfo(
        "map_type:\t3\n" ++
            "key_size:\t4\n" ++
            "value_size:\t8\n" ++
            "max_entries:\t256\n" ++
            "map_flags:\t0x100000000\n",
    ));
}
