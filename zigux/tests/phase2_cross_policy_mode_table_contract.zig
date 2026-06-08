const std = @import("std");

const policy_path = "scripts/zigux/zig-toolchain-policy.json";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

const current_route = "make -C zigux phase2-cross";
const current_archive_target = "x86_64-linux";
const current_route_only_target = "aarch64-linux";
const stale_target = "riscv64-linux";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    if (std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(128 * 1024))) |content| {
        return content;
    } else |root_err| {
        if (root_err != error.FileNotFound) return root_err;
    }

    const parent_path = try std.fmt.allocPrint(allocator, "../{s}", .{path});
    defer allocator.free(parent_path);
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, parent_path, allocator, .limited(128 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    return count;
}

test "policy keeps one archive-backed target scoped to x86" {
    const allocator = std.testing.allocator;
    const policy = try readRepoFile(allocator, policy_path);
    defer allocator.free(policy);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
    try expectContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try expectNotContains(policy, "\"aarch64-linux\":");
    try expectNotContains(policy, stale_target);
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(policy, "\"archive_target_scope\""));
}

test "fixture exposes exactly one archive target and one route-only peer" {
    const allocator = std.testing.allocator;
    const fixture = try readRepoFile(allocator, fixture_path);
    defer allocator.free(fixture);

    try expectContains(fixture, "\"phase\": \"Phase 2\"");
    try expectContains(fixture, "\"status\": \"active\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"review_status\": \"pinned bootstrap archive\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"review_status\": \"route contract only\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(fixture, stale_target);
    try std.testing.expectEqual(@as(usize, 2), countOccurrences(fixture, "\"target\": "));
    try std.testing.expectEqual(@as(usize, 3), countOccurrences(fixture, current_route));
}

test "mode table preserves policy fixture split without target drift" {
    const allocator = std.testing.allocator;
    const policy = try readRepoFile(allocator, policy_path);
    defer allocator.free(policy);
    const fixture = try readRepoFile(allocator, fixture_path);
    defer allocator.free(fixture);

    try expectContains(policy, current_archive_target);
    try expectContains(fixture, current_archive_target);
    try expectContains(fixture, current_route_only_target);
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectNotContains(policy, current_route_only_target);
    try expectNotContains(policy, stale_target);
    try expectNotContains(fixture, stale_target);
}
