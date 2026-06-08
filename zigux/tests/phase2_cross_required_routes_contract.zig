const std = @import("std");

const policy_paths = [_][]const u8{
    "scripts/zigux/zig-toolchain-policy.json",
    "../../scripts/zigux/zig-toolchain-policy.json",
};

const fixture_paths = [_][]const u8{
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "fixtures/phase2_cross_targets.json",
};

fn readFirstExisting(allocator: std.mem.Allocator, paths: []const []const u8) ![]u8 {
    for (paths) |path| {
        if (std.Io.Dir.cwd().readFileAlloc(
            std.testing.io,
            path,
            allocator,
            .limited(1024 * 1024),
        )) |content| {
            return content;
        } else |err| switch (err) {
            error.FileNotFound => continue,
            else => return err,
        }
    }
    return error.FileNotFound;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |index| {
        count += 1;
        offset += index + needle.len;
    }
    return count;
}

test "policy required make route roster keeps phase2 cross ordered" {
    const policy = try readFirstExisting(std.testing.allocator, &policy_paths);
    defer std.testing.allocator.free(policy);

    const route_markers = [_][]const u8{
        "\"phase2-toolchain\"",
        "\"phase2-tools\"",
        "\"phase2-kconfig\"",
        "\"phase2-cross\"",
        "\"phase2-genksyms\"",
        "\"phase2-fixdep\"",
        "\"phase2-validate\"",
    };

    try expectContains(policy, "\"required_make_routes\": [");
    for (route_markers) |marker| {
        try expectContains(policy, marker);
        try std.testing.expectEqual(@as(usize, 1), countOccurrences(policy, marker));
    }

    for (route_markers[0 .. route_markers.len - 1], route_markers[1..]) |before, after| {
        try expectOrdered(policy, before, after);
    }
}

test "phase2 cross route remains between kconfig and genksyms lanes" {
    const policy = try readFirstExisting(std.testing.allocator, &policy_paths);
    defer std.testing.allocator.free(policy);

    try expectOrdered(policy, "\"phase2-kconfig\"", "\"phase2-cross\"");
    try expectOrdered(policy, "\"phase2-cross\"", "\"phase2-genksyms\"");
    try expectOrdered(policy, "\"archive_target_scope\": [", "\"required_make_routes\": [");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
}

test "policy archive scope stays tied to the current fixture boundary" {
    const policy = try readFirstExisting(std.testing.allocator, &policy_paths);
    defer std.testing.allocator.free(policy);
    const fixture = try readFirstExisting(std.testing.allocator, &fixture_paths);
    defer std.testing.allocator.free(fixture);

    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
    try expectContains(policy, "\"archive_sha256\": {\n    \"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try expectContains(fixture, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(policy, "\"riscv64-linux\"");
    try expectNotContains(fixture, "\"riscv64-linux\"");
}

test "fixture continues to publish phase2 cross as the live route" {
    const fixture = try readFirstExisting(std.testing.allocator, &fixture_paths);
    defer std.testing.allocator.free(fixture);

    try expectContains(fixture, "\"phase\": \"Phase 2\"");
    try expectContains(fixture, "\"status\": \"active\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try std.testing.expectEqual(@as(usize, 3), countOccurrences(fixture, "\"route\": \"make -C zigux phase2-cross\""));
}
