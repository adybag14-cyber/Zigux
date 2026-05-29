const std = @import("std");

const required_policy_keys = [_][]const u8{
    "phase",
    "channel",
    "minimum_version",
    "archive_sha256",
    "upgrade_policy",
};

const required_upgrade_policy_keys = [_][]const u8{
    "channel_minimum_lockstep",
    "archive_target_scope",
    "required_make_routes",
};

const failure_markers = [_][]const u8{
    "DuplicateTrackingDict",
    "object_pairs_hook=DuplicateTrackingDict",
    "duplicate toolchain policy keys",
    "unexpected toolchain policy keys",
    "duplicate archive_sha256 targets",
    "archive_target_scope references missing archive_sha256 entries",
    "archive_sha256 contains targets outside archive_target_scope",
    "duplicate upgrade_policy keys",
    "unexpected upgrade_policy keys",
    "duplicate required_make_routes entry",
    "minimum_version must match channel when channel_minimum_lockstep is true",
};

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(256 * 1024),
    );
}

test "phase 2 toolchain policy parser keeps fail-closed duplicate and unknown-key guards" {
    const checker_source = try readRepoFile(std.testing.allocator, "scripts/zigux/check-zig-toolchain.py");
    defer std.testing.allocator.free(checker_source);

    for (failure_markers) |marker| {
        try std.testing.expect(contains(checker_source, marker));
    }

    try std.testing.expect(contains(checker_source, "POLICY_KEYS ="));
    for (required_policy_keys) |key| {
        try std.testing.expect(contains(checker_source, key));
    }

    try std.testing.expect(contains(checker_source, "UPGRADE_POLICY_KEYS ="));
    for (required_upgrade_policy_keys) |key| {
        try std.testing.expect(contains(checker_source, key));
    }
}

test "phase 2 pinned policy stays inside the guarded key and route contract" {
    const policy_source = try readRepoFile(std.testing.allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(policy_source);

    for (required_policy_keys) |key| {
        try std.testing.expect(contains(policy_source, key));
    }
    for (required_upgrade_policy_keys) |key| {
        try std.testing.expect(contains(policy_source, key));
    }

    try std.testing.expect(contains(policy_source, "Phase 2"));
    try std.testing.expect(contains(policy_source, "0.17.0-dev.87+9b177a7d2"));
    try std.testing.expect(contains(policy_source, "x86_64-linux"));
    try std.testing.expect(contains(policy_source, "phase2-toolchain"));
    try std.testing.expect(contains(policy_source, "phase2-validate"));
}

test "phase 2 toolchain checker self-test names the policy failure cases" {
    const checker_source = try readRepoFile(std.testing.allocator, "scripts/zigux/check-zig-toolchain.py");
    defer std.testing.allocator.free(checker_source);

    const self_test_markers = [_][]const u8{
        "duplicate toolchain policy keys",
        "unexpected toolchain policy keys",
        "duplicate archive_sha256 targets",
        "duplicate upgrade_policy keys",
        "unexpected upgrade_policy keys",
        "duplicate required_make_routes entry",
        "invalid toolchain policy JSON",
    };

    for (self_test_markers) |marker| {
        try std.testing.expect(contains(checker_source, marker));
    }
}
