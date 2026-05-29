const std = @import("std");

const Policy = struct {
    phase: []const u8,
    channel: []const u8,
    minimum_version: []const u8,
    archive_sha256: ArchiveDigests,
    upgrade_policy: UpgradePolicy,
};

const ArchiveDigests = struct {
    @"x86_64-linux": []const u8,
};

const UpgradePolicy = struct {
    channel_minimum_lockstep: bool,
    archive_target_scope: []const []const u8,
    required_make_routes: []const []const u8,
};

fn expectStringSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |item| {
        if (std.mem.eql(u8, item, needle)) {
            return;
        }
    }
    try std.testing.expect(false);
}

fn expectLowerHexDigest(value: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 64), value.len);
    for (value) |byte| {
        try std.testing.expect(std.ascii.isDigit(byte) or (byte >= 'a' and byte <= 'f'));
    }
}

test "phase2 toolchain policy keeps the pinned archive route locked to the current dev build" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const policy_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/zig-toolchain-policy.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(policy_json);

    const parsed = try std.json.parseFromSlice(Policy, std.testing.allocator, policy_json, .{});
    defer parsed.deinit();

    const policy = parsed.value;
    try std.testing.expectEqualStrings("Phase 2", policy.phase);
    try std.testing.expectEqualStrings("0.17.0-dev.87+9b177a7d2", policy.channel);
    try std.testing.expectEqualStrings(policy.channel, policy.minimum_version);
    try std.testing.expect(policy.upgrade_policy.channel_minimum_lockstep);

    try std.testing.expectEqual(@as(usize, 1), policy.upgrade_policy.archive_target_scope.len);
    try std.testing.expectEqualStrings("x86_64-linux", policy.upgrade_policy.archive_target_scope[0]);
    try expectLowerHexDigest(policy.archive_sha256.@"x86_64-linux");
    try std.testing.expectEqualStrings(
        "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
        policy.archive_sha256.@"x86_64-linux",
    );

    const required_routes = policy.upgrade_policy.required_make_routes;
    try std.testing.expectEqual(@as(usize, 7), required_routes.len);
    try expectStringSliceContains(required_routes, "phase2-toolchain");
    try expectStringSliceContains(required_routes, "phase2-tools");
    try expectStringSliceContains(required_routes, "phase2-kconfig");
    try expectStringSliceContains(required_routes, "phase2-cross");
    try expectStringSliceContains(required_routes, "phase2-genksyms");
    try expectStringSliceContains(required_routes, "phase2-fixdep");
    try expectStringSliceContains(required_routes, "phase2-validate");
}
