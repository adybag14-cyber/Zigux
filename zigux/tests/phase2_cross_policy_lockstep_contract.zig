const std = @import("std");

const ArchiveTarget = struct {
    target: []const u8,
    review_status: []const u8,
    validation_mode: []const u8,
    route: []const u8,
};

const CrossTargetsFixture = struct {
    phase: []const u8,
    status: []const u8,
    route: []const u8,
    archive_target_scope: []const []const u8,
    cross_targets: []const ArchiveTarget,
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
    archive_sha256: std.json.Value,
    upgrade_policy: UpgradePolicy,
};

fn countTargetMode(targets: []const ArchiveTarget, mode: []const u8) usize {
    var count: usize = 0;
    for (targets) |target| {
        if (std.mem.eql(u8, target.validation_mode, mode)) {
            count += 1;
        }
    }
    return count;
}

fn containsString(values: []const []const u8, expected: []const u8) bool {
    for (values) |value| {
        if (std.mem.eql(u8, value, expected)) return true;
    }
    return false;
}

fn expectSameStringSet(left: []const []const u8, right: []const []const u8) !void {
    try std.testing.expectEqual(left.len, right.len);
    for (left) |value| {
        try std.testing.expect(containsString(right, value));
    }
}

fn expectPolicyArchiveSha(policy: ToolchainPolicy, target: []const u8, expected_sha: []const u8) !void {
    const archive_sha_map = policy.archive_sha256.object;
    const actual = archive_sha_map.get(target) orelse return error.MissingArchiveShaTarget;
    try std.testing.expect(actual == .string);
    try std.testing.expectEqualStrings(expected_sha, actual.string);
}

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

test "phase 2 cross target fixture stays in lockstep with toolchain policy" {
    const fixture_parsed = try std.json.parseFromSlice(
        CrossTargetsFixture,
        std.testing.allocator,
        @embedFile("fixtures/phase2_cross_targets.json"),
        .{ .ignore_unknown_fields = true },
    );
    defer fixture_parsed.deinit();

    const policy_json = try readRepoFile("scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(policy_json);

    const policy_parsed = try std.json.parseFromSlice(
        ToolchainPolicy,
        std.testing.allocator,
        policy_json,
        .{ .ignore_unknown_fields = true },
    );
    defer policy_parsed.deinit();

    const fixture = fixture_parsed.value;
    const policy = policy_parsed.value;

    try std.testing.expectEqualStrings("Phase 2", fixture.phase);
    try std.testing.expectEqualStrings("active", fixture.status);
    try std.testing.expectEqualStrings("Phase 2", policy.phase);
    try std.testing.expectEqualStrings(policy.channel, policy.minimum_version);
    try std.testing.expect(policy.upgrade_policy.channel_minimum_lockstep);
    try std.testing.expect(containsString(policy.upgrade_policy.required_make_routes, "phase2-cross"));

    try std.testing.expectEqual(@as(usize, 2), fixture.cross_targets.len);
    try expectSameStringSet(fixture.archive_target_scope, policy.upgrade_policy.archive_target_scope);
    try std.testing.expectEqual(@as(usize, 1), countTargetMode(fixture.cross_targets, "archive_required"));
    try std.testing.expectEqual(@as(usize, 1), countTargetMode(fixture.cross_targets, "route_contract_only"));

    const archive_target = fixture.cross_targets[0];
    const route_only_target = fixture.cross_targets[1];

    try std.testing.expectEqualStrings("x86_64-linux", archive_target.target);
    try std.testing.expectEqualStrings("archive_required", archive_target.validation_mode);
    try std.testing.expectEqualStrings("pinned bootstrap archive", archive_target.review_status);
    try std.testing.expect(containsString(fixture.archive_target_scope, archive_target.target));
    try expectPolicyArchiveSha(
        policy,
        archive_target.target,
        "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
    );

    try std.testing.expectEqualStrings("aarch64-linux", route_only_target.target);
    try std.testing.expectEqualStrings("route_contract_only", route_only_target.validation_mode);
    try std.testing.expectEqualStrings("route contract only", route_only_target.review_status);
    try std.testing.expect(!containsString(fixture.archive_target_scope, route_only_target.target));
    try std.testing.expect(policy.archive_sha256.object.get(route_only_target.target) == null);

    for (fixture.cross_targets) |target| {
        try std.testing.expectEqualStrings(fixture.route, target.route);
        try std.testing.expectEqualStrings("make -C zigux phase2-cross", target.route);
    }
}
