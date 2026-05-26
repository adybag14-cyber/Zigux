const std = @import("std");

const bridge = @import("file_path_handle_bridge.zig");

test "phase8 file-path bridge entrypoints stay explicit" {
    try std.testing.expect(@hasDecl(bridge, "default_proc_fdinfo_root"));
    try std.testing.expect(@hasDecl(bridge, "FilePathHandleBridgeError"));
    try std.testing.expect(@hasDecl(bridge, "FdinfoLine"));
    try std.testing.expect(@hasDecl(bridge, "ReusedMapNameDisposition"));
    try std.testing.expect(@hasDecl(bridge, "ReusedMapNameSummary"));
    try std.testing.expect(@hasDecl(bridge, "validateProcFdinfoRoot"));
    try std.testing.expect(@hasDecl(bridge, "buildProcFdinfoPath"));
    try std.testing.expect(@hasDecl(bridge, "buildProcFdinfoPathReturn"));
    try std.testing.expect(@hasDecl(bridge, "parseFdinfoLine"));
    try std.testing.expect(@hasDecl(bridge, "summarizeReusedMapName"));
    try std.testing.expect(@hasDecl(bridge, "resolveReusedMapName"));
    try std.testing.expect(@hasDecl(bridge, "resolveReusedMapNameReturn"));
}

test "phase8 file-path bridge keeps helper-only outputs stable" {
    var path_buffer: [64]u8 = undefined;
    var name_buffer: [64]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/proc/self/fdinfo/41",
        try bridge.buildProcFdinfoPath(&path_buffer, null, 41),
    );
    try std.testing.expectEqualStrings(
        "/proc/4242/fdinfo/7",
        try bridge.buildProcFdinfoPath(&path_buffer, "/proc/4242/fdinfo", 7),
    );
    try std.testing.expectEqualStrings(
        "stats_map",
        try bridge.resolveReusedMapName(&name_buffer, "stats_map\x00"),
    );
    const fdinfo = try bridge.parseFdinfoLine("map_flags:\t0x20\n");
    try std.testing.expectEqualStrings("map_flags", fdinfo.key);
    try std.testing.expectEqualStrings("0x20", fdinfo.value);

    const truncated = try bridge.summarizeReusedMapName("truncated_name");
    try std.testing.expectEqual(bridge.ReusedMapNameDisposition.truncated_fixed_width, truncated.disposition);
    try std.testing.expectEqualStrings("truncated_name", truncated.name);
}

test "phase8 file-path bridge keeps validation and errno outputs stable" {
    var path_buffer: [64]u8 = undefined;
    var name_buffer: [64]u8 = undefined;

    try std.testing.expectError(error.InvalidProcRoot, bridge.buildProcFdinfoPath(&path_buffer, "proc/fdinfo", 1));
    try std.testing.expectError(error.NegativeFd, bridge.buildProcFdinfoPath(&path_buffer, null, -1));
    try std.testing.expectError(error.EmptyFdinfoLine, bridge.parseFdinfoLine(""));
    try std.testing.expectError(error.MissingFdinfoLineSeparator, bridge.parseFdinfoLine("map_flags 0x20"));
    try std.testing.expectError(error.EmptyMapName, bridge.resolveReusedMapName(&name_buffer, ""));

    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        bridge.buildProcFdinfoPathReturn(&path_buffer, "proc/fdinfo", 1),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        bridge.resolveReusedMapNameReturn(&name_buffer, ""),
    );
}
