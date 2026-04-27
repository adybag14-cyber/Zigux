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

test "phase 8 pin-path segment resolves stored versus requested pin paths" {
    const requested = try pin_path.resolveMapPinRequest("/sys/fs/bpf/cache_map", null, false);
    switch (requested) {
        .proceed => |resolution| {
            try std.testing.expectEqualStrings("/sys/fs/bpf/cache_map", resolution.path);
            try std.testing.expectEqual(.requested, resolution.source);
        },
        .already_pinned => unreachable,
    }

    const stored = try pin_path.resolveMapPinRequest(null, "/sys/fs/bpf/cache_map", false);
    switch (stored) {
        .proceed => |resolution| {
            try std.testing.expectEqualStrings("/sys/fs/bpf/cache_map", resolution.path);
            try std.testing.expectEqual(.stored, resolution.source);
        },
        .already_pinned => unreachable,
    }

    const pinned = try pin_path.resolveMapPinRequest(
        "/sys/fs/bpf/cache_map",
        "/sys/fs/bpf/cache_map",
        true,
    );
    switch (pinned) {
        .proceed => unreachable,
        .already_pinned => |path| try std.testing.expectEqualStrings("/sys/fs/bpf/cache_map", path),
    }

    try std.testing.expectError(error.PathMismatch, pin_path.resolveMapPinRequest(
        "/sys/fs/bpf/other_map",
        "/sys/fs/bpf/cache_map",
        false,
    ));
    try std.testing.expectError(error.MissingPath, pin_path.resolveMapPinRequest(null, null, false));
    try std.testing.expectError(error.AlreadyPinned, pin_path.resolveMapPinRequest(
        "/sys/fs/bpf/cache_map",
        null,
        true,
    ));
}

test "phase 8 pin-path segment resolves stored versus requested unpin paths" {
    const stored = try pin_path.resolveMapUnpinRequest(null, "/sys/fs/bpf/cache_map");
    try std.testing.expectEqualStrings("/sys/fs/bpf/cache_map", stored.path);
    try std.testing.expectEqual(.stored, stored.source);

    const requested = try pin_path.resolveMapUnpinRequest("/sys/fs/bpf/cache_map", null);
    try std.testing.expectEqualStrings("/sys/fs/bpf/cache_map", requested.path);
    try std.testing.expectEqual(.requested, requested.source);

    try std.testing.expectError(error.PathMismatch, pin_path.resolveMapUnpinRequest(
        "/sys/fs/bpf/other_map",
        "/sys/fs/bpf/cache_map",
    ));
    try std.testing.expectError(error.MissingPath, pin_path.resolveMapUnpinRequest(null, null));
}
