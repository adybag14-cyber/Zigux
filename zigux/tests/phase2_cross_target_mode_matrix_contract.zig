const std = @import("std");

const fixture_paths = .{
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "fixtures/phase2_cross_targets.json",
};

const route = "make -C zigux phase2-cross";

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

const TargetMode = enum {
    archive_required,
    route_contract_only,

    fn parse(value: []const u8) ?TargetMode {
        if (std.mem.eql(u8, value, "archive_required")) return .archive_required;
        if (std.mem.eql(u8, value, "route_contract_only")) return .route_contract_only;
        return null;
    }

    fn expectedReviewStatus(mode: TargetMode) []const u8 {
        return switch (mode) {
            .archive_required => "pinned bootstrap archive",
            .route_contract_only => "route contract only",
        };
    }

    fn isArchiveBacked(mode: TargetMode) bool {
        return mode == .archive_required;
    }
};

fn readFixture() ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    if (std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        fixture_paths[0],
        std.testing.allocator,
        .limited(16 * 1024),
    )) |fixture_json| {
        return fixture_json;
    } else |err| switch (err) {
        error.FileNotFound => {},
        else => return err,
    }

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        fixture_paths[1],
        std.testing.allocator,
        .limited(16 * 1024),
    );
}

fn parseFixture() !std.json.Parsed(CrossTargetsFixture) {
    const fixture_json = try readFixture();
    defer std.testing.allocator.free(fixture_json);

    return std.json.parseFromSlice(CrossTargetsFixture, std.testing.allocator, fixture_json, .{
        .ignore_unknown_fields = true,
        .allocate = .alloc_always,
    });
}

fn expectTarget(entry: CrossTarget, name: []const u8, mode: TargetMode) !void {
    try std.testing.expectEqualStrings(name, entry.target);
    try std.testing.expectEqualStrings(route, entry.route);
    try std.testing.expectEqualStrings(@tagName(mode), entry.validation_mode);
    try std.testing.expectEqualStrings(mode.expectedReviewStatus(), entry.review_status);
}

fn scopeContains(scope: []const []const u8, target: []const u8) bool {
    for (scope) |entry| {
        if (std.mem.eql(u8, entry, target)) return true;
    }
    return false;
}

test "phase 2 cross target modes stay tied to the current two target matrix" {
    const parsed = try parseFixture();
    defer parsed.deinit();
    const fixture = parsed.value;

    try std.testing.expectEqualStrings("Phase 2", fixture.phase);
    try std.testing.expectEqualStrings("active", fixture.status);
    try std.testing.expectEqualStrings(route, fixture.route);
    try std.testing.expectEqual(@as(usize, 2), fixture.cross_targets.len);

    try expectTarget(fixture.cross_targets[0], "x86_64-linux", .archive_required);
    try expectTarget(fixture.cross_targets[1], "aarch64-linux", .route_contract_only);
}

test "archive target scope is exactly the archive required target set" {
    const parsed = try parseFixture();
    defer parsed.deinit();
    const fixture = parsed.value;

    var archive_required_count: usize = 0;
    for (fixture.cross_targets) |entry| {
        const mode = TargetMode.parse(entry.validation_mode) orelse return error.UnknownTargetMode;
        if (mode.isArchiveBacked()) {
            archive_required_count += 1;
            try std.testing.expect(scopeContains(fixture.archive_target_scope, entry.target));
        } else {
            try std.testing.expect(!scopeContains(fixture.archive_target_scope, entry.target));
        }
    }

    try std.testing.expectEqual(archive_required_count, fixture.archive_target_scope.len);
    try std.testing.expectEqual(@as(usize, 1), archive_required_count);
    try std.testing.expectEqualStrings("x86_64-linux", fixture.archive_target_scope[0]);
}

test "validation mode decoder fails closed on unknown matrix modes" {
    try std.testing.expectEqual(TargetMode.archive_required, TargetMode.parse("archive_required").?);
    try std.testing.expectEqual(TargetMode.route_contract_only, TargetMode.parse("route_contract_only").?);
    try std.testing.expectEqual(@as(?TargetMode, null), TargetMode.parse("archive_optional"));
    try std.testing.expectEqual(@as(?TargetMode, null), TargetMode.parse("route_only"));
    try std.testing.expectEqual(@as(?TargetMode, null), TargetMode.parse(""));
}

test "each target keeps a linux triple and an explicit review state" {
    const parsed = try parseFixture();
    defer parsed.deinit();
    const fixture = parsed.value;

    for (fixture.cross_targets) |entry| {
        const mode = TargetMode.parse(entry.validation_mode) orelse return error.UnknownTargetMode;
        try std.testing.expect(std.mem.endsWith(u8, entry.target, "-linux"));
        try std.testing.expect(entry.review_status.len > 0);
        try std.testing.expectEqualStrings(mode.expectedReviewStatus(), entry.review_status);
    }
}
