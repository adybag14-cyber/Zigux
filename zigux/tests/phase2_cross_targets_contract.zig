const std = @import("std");

const fixture_json = @embedFile("fixtures/phase2_cross_targets.json");

const expected_route = "make -C zigux phase2-cross";

const CrossTarget = struct {
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
    cross_targets: []const CrossTarget,
};

test "phase2 cross targets fixture keeps the direct route contract" {
    var parsed = try std.json.parseFromSlice(
        CrossTargetsFixture,
        std.testing.allocator,
        fixture_json,
        .{ .ignore_unknown_fields = false },
    );
    defer parsed.deinit();

    const fixture = parsed.value;
    try std.testing.expectEqualStrings("Phase 2", fixture.phase);
    try std.testing.expectEqualStrings("active", fixture.status);
    try std.testing.expectEqualStrings(expected_route, fixture.route);

    try std.testing.expectEqual(@as(usize, 1), fixture.archive_target_scope.len);
    try std.testing.expectEqualStrings("x86_64-linux", fixture.archive_target_scope[0]);

    try std.testing.expectEqual(@as(usize, 2), fixture.cross_targets.len);
    try expectCrossTarget(
        fixture.cross_targets[0],
        "x86_64-linux",
        "pinned bootstrap archive",
        "archive_required",
    );
    try expectCrossTarget(
        fixture.cross_targets[1],
        "aarch64-linux",
        "route contract only",
        "route_contract_only",
    );
}

fn expectCrossTarget(
    entry: CrossTarget,
    expected_target: []const u8,
    expected_review_status: []const u8,
    expected_validation_mode: []const u8,
) !void {
    try std.testing.expectEqualStrings(expected_target, entry.target);
    try std.testing.expectEqualStrings(expected_review_status, entry.review_status);
    try std.testing.expectEqualStrings(expected_validation_mode, entry.validation_mode);
    try std.testing.expectEqualStrings(expected_route, entry.route);
}
