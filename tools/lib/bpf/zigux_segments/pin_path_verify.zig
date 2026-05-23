const std = @import("std");

const pin_path = @import("pin_path.zig");

test "phase8 pin-path helper entrypoints stay explicit" {
    try std.testing.expect(@hasDecl(pin_path, "pathnameConcat"));
    try std.testing.expect(@hasDecl(pin_path, "sanitizePinPath"));
    try std.testing.expect(@hasDecl(pin_path, "validatePinName"));
    try std.testing.expect(@hasDecl(pin_path, "validatePinRootPath"));
    try std.testing.expect(@hasDecl(pin_path, "buildMapPinPath"));
    try std.testing.expect(@hasDecl(pin_path, "buildValidatedMapPinPath"));
    try std.testing.expect(@hasDecl(pin_path, "buildSanitizedMapPinPath"));
    try std.testing.expect(@hasDecl(pin_path, "buildValidatedSanitizedMapPinPath"));
    try std.testing.expect(@hasDecl(pin_path, "buildValidatedSanitizedMapPinPathReturn"));
    try std.testing.expect(@hasDecl(pin_path, "buildProgramPinPath"));
    try std.testing.expect(@hasDecl(pin_path, "buildValidatedProgramPinPath"));
    try std.testing.expect(@hasDecl(pin_path, "buildSanitizedProgramPinPath"));
    try std.testing.expect(@hasDecl(pin_path, "buildValidatedSanitizedProgramPinPath"));
    try std.testing.expect(@hasDecl(pin_path, "buildValidatedSanitizedProgramPinPathReturn"));
}

test "phase8 pin-path helpers keep stable map and program outputs explicit" {
    var buffer: [96]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/stats_map",
        try pin_path.buildMapPinPath(&buffer, null, "stats_map"),
    );
    try std.testing.expectEqualStrings(
        "/tmp/bpf.v1/cache_map",
        try pin_path.buildSanitizedMapPinPath(&buffer, "/tmp/bpf.v1", "cache.map"),
    );
    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/xdp_dispatch_v1",
        try pin_path.buildValidatedSanitizedProgramPinPath(&buffer, null, "xdp_dispatch.v1"),
    );
    try std.testing.expectEqualStrings(
        "/tmp/bpf.v1/xdp_dispatch",
        try pin_path.buildValidatedProgramPinPath(&buffer, "/tmp/bpf.v1", "xdp_dispatch"),
    );
}

test "phase8 pin-path helpers keep slash-preserving and validated-root outputs explicit" {
    var buffer: [96]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/root_map",
        try pin_path.pathnameConcat(&buffer, "/", "root_map"),
    );
    try std.testing.expectEqualStrings(
        "/tmp/bpf/cache_map",
        try pin_path.pathnameConcat(&buffer, "/tmp/bpf/", "cache_map"),
    );
    try std.testing.expectEqualStrings(
        "/tmp/bpf.v1/metrics.v1",
        try pin_path.buildValidatedMapPinPath(&buffer, "/tmp/bpf.v1", "metrics.v1"),
    );
    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/stats.map",
        try pin_path.buildValidatedMapPinPath(&buffer, null, "stats.map"),
    );
}

test "phase8 pin-path helpers keep validated sanitized return wrappers explicit" {
    var buffer: [96]u8 = undefined;

    try std.testing.expectEqual(
        @as(i32, "/sys/fs/bpf/metrics_v1".len),
        pin_path.buildValidatedSanitizedMapPinPathReturn(&buffer, null, "metrics.v1"),
    );
    try std.testing.expectEqualStrings("/sys/fs/bpf/metrics_v1", buffer[0.."/sys/fs/bpf/metrics_v1".len]);
    try std.testing.expectEqual(
        @as(i32, "/sys/fs/bpf/xdp_dispatch_v1".len),
        pin_path.buildValidatedSanitizedProgramPinPathReturn(&buffer, null, "xdp_dispatch.v1"),
    );
    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/xdp_dispatch_v1",
        buffer[0.."/sys/fs/bpf/xdp_dispatch_v1".len],
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        pin_path.buildValidatedSanitizedMapPinPathReturn(&buffer, null, "metrics/v1"),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.INVAL)),
        pin_path.buildValidatedSanitizedProgramPinPathReturn(&buffer, "tmp/bpf", "xdp_dispatch.v1"),
    );
}

test "phase8 pin-path helpers keep validation failures explicit" {
    var buffer: [96]u8 = undefined;

    try std.testing.expectError(error.EmptyName, pin_path.validatePinName(""));
    try std.testing.expectError(error.InvalidName, pin_path.validatePinName("stats/map"));
    try std.testing.expectError(error.InvalidRootPath, pin_path.validatePinRootPath("tmp/bpf"));
    try std.testing.expectError(error.InvalidRootPath, pin_path.validatePinRootPath("/tmp/bpf/"));
    try std.testing.expectError(error.InvalidRootPath, pin_path.validatePinRootPath("/tmp/bpf\x00tmp"));

    try std.testing.expectError(
        error.InvalidName,
        pin_path.buildValidatedMapPinPath(&buffer, null, "stats/map"),
    );
    try std.testing.expectError(
        error.InvalidRootPath,
        pin_path.buildValidatedMapPinPath(&buffer, "/tmp/bpf\x00tmp", "stats.map"),
    );
    try std.testing.expectError(
        error.InvalidRootPath,
        pin_path.buildValidatedSanitizedProgramPinPath(&buffer, "tmp/bpf", "xdp_dispatch.v1"),
    );
}

test "phase8 pin-path helpers keep length failures explicit" {
    var buffer: [16]u8 = undefined;

    try std.testing.expectError(
        error.NameTooLong,
        pin_path.pathnameConcat(&buffer, "/sys/fs/bpf", "very_long_map_name"),
    );
    try std.testing.expectError(
        error.NameTooLong,
        pin_path.buildMapPinPath(&buffer, "/custom/root", "very_long_map_name"),
    );
    try std.testing.expectError(
        error.NameTooLong,
        pin_path.buildProgramPinPath(&buffer, "/custom/root", "very_long_program_name"),
    );

    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NAMETOOLONG)),
        pin_path.buildValidatedSanitizedMapPinPathReturn(&buffer, "/custom/root", "very_long_map_name"),
    );
    try std.testing.expectEqual(
        -@as(i32, @intFromEnum(std.os.linux.E.NAMETOOLONG)),
        pin_path.buildValidatedSanitizedProgramPinPathReturn(
            &buffer,
            "/custom/root",
            "very_long_program_name",
        ),
    );
}
