const std = @import("std");
const pin_path = @import("pin_path");

test "phase 8 pin-path module imports cleanly" {
    _ = pin_path;
}

test "phase 8 pin-path helper keeps bounded bpffs path planning explicit" {
    var buffer: [96]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/stats_map",
        try pin_path.buildMapPinPath(&buffer, null, "stats_map"),
    );
    try std.testing.expectEqualStrings(
        "/custom/root/stats_map",
        try pin_path.buildValidatedMapPinPath(&buffer, "/custom/root", "stats_map"),
    );
    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/metrics_v1",
        try pin_path.buildValidatedSanitizedMapPinPath(&buffer, null, "metrics.v1"),
    );
}

test "phase 8 pin-path helper keeps name and root validation failures explicit" {
    var buffer: [96]u8 = undefined;

    try pin_path.validatePinName("stats_map");
    try std.testing.expectError(error.EmptyName, pin_path.validatePinName(""));
    try std.testing.expectError(error.InvalidName, pin_path.validatePinName("stats/map"));
    try std.testing.expectError(error.InvalidName, pin_path.validatePinName("stats\x00map"));

    try pin_path.validatePinRootPath("/sys/fs/bpf");
    try std.testing.expectError(error.InvalidRootPath, pin_path.validatePinRootPath("relative/root"));
    try std.testing.expectError(error.InvalidRootPath, pin_path.validatePinRootPath("/sys/fs/bpf/"));

    try std.testing.expectError(
        error.InvalidName,
        pin_path.buildValidatedSanitizedMapPinPath(&buffer, null, "metrics/v1"),
    );
    try std.testing.expectError(
        error.InvalidRootPath,
        pin_path.buildValidatedSanitizedMapPinPath(&buffer, "tmp/bpf", "metrics.v1"),
    );
}

test "phase 8 pin-path helper keeps sanitization and bounded buffer failures explicit" {
    var sanitized_buffer: [96]u8 = undefined;
    try std.testing.expectEqualStrings(
        "/tmp/bpf_v1_2/cache_map",
        try pin_path.buildSanitizedMapPinPath(&sanitized_buffer, "/tmp/bpf.v1.2", "cache.map"),
    );

    var short_buffer: [16]u8 = undefined;
    try std.testing.expectError(
        error.NameTooLong,
        pin_path.pathnameConcat(&short_buffer, "/sys/fs/bpf", "very_long_map_name"),
    );
    try std.testing.expectError(
        error.NameTooLong,
        pin_path.buildMapPinPath(&short_buffer, "/custom/root", "very_long_map_name"),
    );
}
