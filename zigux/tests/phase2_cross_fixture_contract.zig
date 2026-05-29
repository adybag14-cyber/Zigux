const std = @import("std");
const testing = std.testing;

const fixture = @embedFile("fixtures/phase2_cross_targets.json");

const CrossTarget = struct {
    target: []const u8,
    review_status: []const u8,
    validation_mode: []const u8,
    route: []const u8,
};

const Phase2CrossTargets = struct {
    phase: []const u8,
    status: []const u8,
    route: []const u8,
    archive_target_scope: []const []const u8,
    cross_targets: []const CrossTarget,
};

fn parseFixture() !std.json.Parsed(Phase2CrossTargets) {
    return std.json.parseFromSlice(Phase2CrossTargets, testing.allocator, fixture, .{});
}

fn expectText(actual: []const u8, expected: []const u8) !void {
    try testing.expectEqualStrings(expected, actual);
}

test "phase2 cross fixture keeps the bounded two-target matrix contract" {
    var parsed = try parseFixture();
    defer parsed.deinit();

    const matrix = parsed.value;
    try expectText(matrix.phase, "Phase 2");
    try expectText(matrix.status, "active");
    try expectText(matrix.route, "make -C zigux phase2-cross");

    try testing.expectEqual(@as(usize, 1), matrix.archive_target_scope.len);
    try expectText(matrix.archive_target_scope[0], "x86_64-linux");

    try testing.expectEqual(@as(usize, 2), matrix.cross_targets.len);
    try expectText(matrix.cross_targets[0].target, "x86_64-linux");
    try expectText(matrix.cross_targets[0].review_status, "pinned bootstrap archive");
    try expectText(matrix.cross_targets[0].validation_mode, "archive_required");
    try expectText(matrix.cross_targets[0].route, matrix.route);

    try expectText(matrix.cross_targets[1].target, "aarch64-linux");
    try expectText(matrix.cross_targets[1].review_status, "route contract only");
    try expectText(matrix.cross_targets[1].validation_mode, "route_contract_only");
    try expectText(matrix.cross_targets[1].route, matrix.route);
}

test "phase2 cross fixture keeps archive validation scoped to the pinned host target" {
    var parsed = try parseFixture();
    defer parsed.deinit();

    var archive_required_count: usize = 0;
    for (parsed.value.cross_targets) |target| {
        if (std.mem.eql(u8, target.validation_mode, "archive_required")) {
            archive_required_count += 1;
            try expectText(target.target, "x86_64-linux");
        }
    }

    try testing.expectEqual(@as(usize, 1), archive_required_count);
}
