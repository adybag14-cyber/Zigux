const std = @import("std");
const pin_path = @import("pin_path");

test "phase 8 pin-path segment imports cleanly" {
    _ = pin_path;
}

test "phase 8 pin-path segment keeps map-path joining bounded and explicit" {
    var buffer: [96]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/stats_map",
        try pin_path.buildMapPinPath(&buffer, null, "stats_map"),
    );
    try std.testing.expectEqualStrings(
        "/var/run/bpf/stats_map",
        try pin_path.buildMapPinPath(&buffer, "/var/run/bpf", "stats_map"),
    );
}

test "phase 8 pin-path segment sanitizes dots the same way bpffs pin names do" {
    var buffer: [96]u8 = undefined;

    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/metrics_v1",
        try pin_path.buildSanitizedMapPinPath(&buffer, null, "metrics.v1"),
    );
    try std.testing.expectEqualStrings(
        "/tmp/bpf_v1_2/cache_map",
        try pin_path.buildSanitizedMapPinPath(&buffer, "/tmp/bpf.v1.2", "cache.map"),
    );
}

test "phase 8 pin-path segment keeps validation and path-shape checks bounded" {
    var buffer: [96]u8 = undefined;

    try pin_path.validatePinName("cache.map");
    try pin_path.validatePinRootPath("/sys/fs/bpf");

    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/cache_map",
        try pin_path.buildValidatedSanitizedMapPinPath(&buffer, null, "cache.map"),
    );
    try std.testing.expectError(error.InvalidName, pin_path.validatePinName("cache/map"));
    try std.testing.expectError(error.InvalidRootPath, pin_path.validatePinRootPath("tmp/bpf"));
}

test "phase 8 pin-path segment keeps overflow failures explicit" {
    var buffer: [16]u8 = undefined;

    try std.testing.expectError(
        error.NameTooLong,
        pin_path.buildMapPinPath(&buffer, "/custom/root", "very_long_map_name"),
    );
}
