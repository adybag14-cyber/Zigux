const std = @import("std");

const checker_path = "scripts/zigux/check-phase2-cross.py";
const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";

const ContractError = error{
    MissingMarker,
    DuplicateMarker,
    ForbiddenMarkerPresent,
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
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit)) catch |err| switch (err) {
        error.FileNotFound => blk: {
            const fallback = try std.mem.concat(std.testing.allocator, u8, &.{ "../../", path });
            defer std.testing.allocator.free(fallback);
            break :blk try std.Io.Dir.cwd().readFileAlloc(
                io_instance.io(),
                fallback,
                std.testing.allocator,
                .limited(limit),
            );
        },
        else => return err,
    };
}

fn requireContains(text: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, text, marker) == null) return ContractError.MissingMarker;
}

fn requireAbsent(text: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, text, marker) != null) return ContractError.ForbiddenMarkerPresent;
}

fn requireOnce(text: []const u8, marker: []const u8) !void {
    const matches = std.mem.count(u8, text, marker);
    if (matches == 0) return ContractError.MissingMarker;
    if (matches != 1) return ContractError.DuplicateMarker;
}

fn validateCheckerOutputEnvelope(text: []const u8) !void {
    try requireContains(text, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE=fail");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass");
    try requireContains(text, "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT=");
    try requireContains(text, "MISSING_MAKEFILE_LINE");
    try requireContains(text, "DUPLICATE_MAKEFILE_LINE");
    try requireContains(text, "INVALID_FIXTURE_FIELD");
    try requireContains(text, "ARCHIVE_SCOPE_MISMATCH");
    try requireContains(text, "INVALID_CROSS_TARGET_ROUTE");
    try requireContains(text, "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH");
    try requireContains(text, "len(cross_targets)");
    try requireContains(text, "len(load_archive_target_scope(args.root.resolve()))");
    try requireAbsent(text, "PHASE2_CROSS_MATRIX_JOB=");
}

fn validateFixtureCountBoundary(fixture: CrossFixture) !void {
    try std.testing.expectEqualStrings("Phase 2", fixture.phase);
    try std.testing.expectEqualStrings("active", fixture.status);
    try std.testing.expectEqualStrings("make -C zigux phase2-cross", fixture.route);
    try std.testing.expectEqual(@as(usize, 1), fixture.archive_target_scope.len);
    try std.testing.expectEqualStrings("x86_64-linux", fixture.archive_target_scope[0]);
    try std.testing.expectEqual(@as(usize, 2), fixture.cross_targets.len);

    var archive_required_count: usize = 0;
    var route_contract_only_count: usize = 0;
    for (fixture.cross_targets) |target| {
        try std.testing.expectEqualStrings("make -C zigux phase2-cross", target.route);
        if (std.mem.eql(u8, target.validation_mode, "archive_required")) {
            archive_required_count += 1;
            try std.testing.expectEqualStrings("x86_64-linux", target.target);
            try std.testing.expectEqualStrings("pinned bootstrap archive", target.review_status);
        } else if (std.mem.eql(u8, target.validation_mode, "route_contract_only")) {
            route_contract_only_count += 1;
            try std.testing.expectEqualStrings("aarch64-linux", target.target);
            try std.testing.expectEqualStrings("route contract only", target.review_status);
        } else {
            return ContractError.MissingMarker;
        }
    }
    try std.testing.expectEqual(@as(usize, 1), archive_required_count);
    try std.testing.expectEqual(@as(usize, 1), route_contract_only_count);
}

test "phase 2 cross checker preserves reviewer-facing output labels" {
    const checker = try readRepoFile(checker_path, 256 * 1024);
    defer std.testing.allocator.free(checker);

    try validateCheckerOutputEnvelope(checker);
}

test "phase 2 cross fixture count boundary matches checker output contract" {
    const fixture_json = try readRepoFile(fixture_path, 16 * 1024);
    defer std.testing.allocator.free(fixture_json);

    const parsed = try std.json.parseFromSlice(CrossFixture, std.testing.allocator, fixture_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    try validateFixtureCountBoundary(parsed.value);
}

test "contract catches checker output drift" {
    const minimal_checker =
        \\EXPECTED_SELF_TEST_CASE_COUNT = 17
        \\PHASE2_DIRECT_CROSS_ROUTE=pass
        \\PHASE2_DIRECT_CROSS_ROUTE=fail
        \\PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=
        \\PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=
        \\PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass
        \\PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT=
        \\MISSING_MAKEFILE_LINE
        \\DUPLICATE_MAKEFILE_LINE
        \\INVALID_FIXTURE_FIELD
        \\ARCHIVE_SCOPE_MISMATCH
        \\INVALID_CROSS_TARGET_ROUTE
        \\ARCHIVE_REQUIRED_TARGET_SET_MISMATCH
        \\len(cross_targets)
        \\len(load_archive_target_scope(args.root.resolve()))
    ;
    try validateCheckerOutputEnvelope(minimal_checker);

    try std.testing.expectError(ContractError.MissingMarker, validateCheckerOutputEnvelope(
        \\EXPECTED_SELF_TEST_CASE_COUNT = 17
        \\PHASE2_DIRECT_CROSS_ROUTE=pass
        \\PHASE2_DIRECT_CROSS_ROUTE=fail
        \\PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=
        \\PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass
        \\PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT=
        \\MISSING_MAKEFILE_LINE
        \\DUPLICATE_MAKEFILE_LINE
        \\INVALID_FIXTURE_FIELD
        \\ARCHIVE_SCOPE_MISMATCH
        \\INVALID_CROSS_TARGET_ROUTE
        \\ARCHIVE_REQUIRED_TARGET_SET_MISMATCH
        \\len(cross_targets)
        \\len(load_archive_target_scope(args.root.resolve()))
    ));

    try std.testing.expectError(ContractError.ForbiddenMarkerPresent, validateCheckerOutputEnvelope(
        \\EXPECTED_SELF_TEST_CASE_COUNT = 17
        \\PHASE2_DIRECT_CROSS_ROUTE=pass
        \\PHASE2_DIRECT_CROSS_ROUTE=fail
        \\PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=
        \\PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT=
        \\PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass
        \\PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT=
        \\MISSING_MAKEFILE_LINE
        \\DUPLICATE_MAKEFILE_LINE
        \\INVALID_FIXTURE_FIELD
        \\ARCHIVE_SCOPE_MISMATCH
        \\INVALID_CROSS_TARGET_ROUTE
        \\ARCHIVE_REQUIRED_TARGET_SET_MISMATCH
        \\len(cross_targets)
        \\len(load_archive_target_scope(args.root.resolve()))
        \\PHASE2_CROSS_MATRIX_JOB=legacy
    ));
}

test "contract catches duplicate output labels" {
    try std.testing.expectError(ContractError.DuplicateMarker, requireOnce(
        \\PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=
        \\PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT=
    , "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT="));
}
