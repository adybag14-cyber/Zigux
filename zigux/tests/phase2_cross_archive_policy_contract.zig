const std = @import("std");

const expected_channel = "0.17.0-dev.758+748e7c5e3";
const expected_archive_sha = "0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6";
const expected_route = "make -C zigux phase2-cross";

const expected_routes = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

const ArchiveSha = struct {
    @"x86_64-linux": []const u8,
};

const UpgradePolicy = struct {
    channel_minimum_lockstep: bool,
    archive_target_scope: []const []const u8,
    required_make_routes: []const []const u8,
};

const ToolchainPolicy = struct {
    phase: []const u8,
    channel: []const u8,
    minimum_version: []const u8,
    archive_sha256: ArchiveSha,
    upgrade_policy: UpgradePolicy,
};

const CrossTarget = struct {
    target: []const u8,
    review_status: []const u8,
    validation_mode: []const u8,
    route: []const u8,
};

const CrossFixture = struct {
    phase: []const u8,
    status: []const u8,
    route: []const u8,
    archive_target_scope: []const []const u8,
    cross_targets: []const CrossTarget,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectStringListEqual(expected: []const []const u8, actual: []const []const u8) !void {
    try std.testing.expectEqual(expected.len, actual.len);
    for (expected, actual) |expected_item, actual_item| {
        try std.testing.expectEqualStrings(expected_item, actual_item);
    }
}

fn findTarget(fixture: CrossFixture, target: []const u8) ?CrossTarget {
    for (fixture.cross_targets) |entry| {
        if (std.mem.eql(u8, entry.target, target)) return entry;
    }
    return null;
}

fn expectNoTarget(fixture: CrossFixture, target: []const u8) !void {
    try std.testing.expect(findTarget(fixture, target) == null);
}

test "phase 2 cross archive policy pins the single trusted archive target" {
    const policy_json = try readRepoFile("scripts/zigux/zig-toolchain-policy.json", 16 * 1024);
    defer std.testing.allocator.free(policy_json);

    const parsed = try std.json.parseFromSlice(ToolchainPolicy, std.testing.allocator, policy_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const policy = parsed.value;

    try std.testing.expectEqualStrings("Phase 2", policy.phase);
    try std.testing.expectEqualStrings(expected_channel, policy.channel);
    try std.testing.expectEqualStrings(expected_channel, policy.minimum_version);
    try std.testing.expect(policy.upgrade_policy.channel_minimum_lockstep);
    try expectStringListEqual(&.{"x86_64-linux"}, policy.upgrade_policy.archive_target_scope);
    try std.testing.expectEqualStrings(expected_archive_sha, policy.archive_sha256.@"x86_64-linux");
    try expectStringListEqual(&expected_routes, policy.upgrade_policy.required_make_routes);
}

test "phase 2 cross fixture stays aligned with the archive policy envelope" {
    const fixture_json = try readRepoFile("zigux/tests/fixtures/phase2_cross_targets.json", 16 * 1024);
    defer std.testing.allocator.free(fixture_json);

    const parsed = try std.json.parseFromSlice(CrossFixture, std.testing.allocator, fixture_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const fixture = parsed.value;

    try std.testing.expectEqualStrings("Phase 2", fixture.phase);
    try std.testing.expectEqualStrings("active", fixture.status);
    try std.testing.expectEqualStrings(expected_route, fixture.route);
    try expectStringListEqual(&.{"x86_64-linux"}, fixture.archive_target_scope);
    try std.testing.expectEqual(@as(usize, 2), fixture.cross_targets.len);

    const archive_target = findTarget(fixture, "x86_64-linux") orelse return error.MissingArchiveTarget;
    try std.testing.expectEqualStrings("pinned bootstrap archive", archive_target.review_status);
    try std.testing.expectEqualStrings("archive_required", archive_target.validation_mode);
    try std.testing.expectEqualStrings(expected_route, archive_target.route);

    const route_only_target = findTarget(fixture, "aarch64-linux") orelse return error.MissingRouteOnlyTarget;
    try std.testing.expectEqualStrings("route contract only", route_only_target.review_status);
    try std.testing.expectEqualStrings("route_contract_only", route_only_target.validation_mode);
    try std.testing.expectEqualStrings(expected_route, route_only_target.route);

    try expectNoTarget(fixture, "riscv64-linux");
}

test "phase 2 cross archive scope remains the only archive-required target" {
    const policy_json = try readRepoFile("scripts/zigux/zig-toolchain-policy.json", 16 * 1024);
    defer std.testing.allocator.free(policy_json);
    const fixture_json = try readRepoFile("zigux/tests/fixtures/phase2_cross_targets.json", 16 * 1024);
    defer std.testing.allocator.free(fixture_json);

    const parsed_policy = try std.json.parseFromSlice(ToolchainPolicy, std.testing.allocator, policy_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed_policy.deinit();
    const parsed_fixture = try std.json.parseFromSlice(CrossFixture, std.testing.allocator, fixture_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed_fixture.deinit();

    try expectStringListEqual(parsed_policy.value.upgrade_policy.archive_target_scope, parsed_fixture.value.archive_target_scope);

    var archive_required_count: usize = 0;
    for (parsed_fixture.value.cross_targets) |entry| {
        if (std.mem.eql(u8, entry.validation_mode, "archive_required")) {
            archive_required_count += 1;
            try std.testing.expectEqualStrings("x86_64-linux", entry.target);
        } else {
            try std.testing.expectEqualStrings("route_contract_only", entry.validation_mode);
        }
    }

    try std.testing.expectEqual(@as(usize, 1), archive_required_count);
}
