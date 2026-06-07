const std = @import("std");

const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";
const route = "make -C zigux phase2-cross";

const ExpectedTarget = struct {
    target: []const u8,
    review_status: []const u8,
    validation_mode: []const u8,
};

const expected_targets = [_]ExpectedTarget{
    .{
        .target = "x86_64-linux",
        .review_status = "pinned bootstrap archive",
        .validation_mode = "archive_required",
    },
    .{
        .target = "aarch64-linux",
        .review_status = "route contract only",
        .validation_mode = "route_contract_only",
    },
};

fn readFixture(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(128 * 1024),
    );
}

fn fieldString(object: std.json.ObjectMap, name: []const u8) ![]const u8 {
    const value = object.get(name) orelse return error.MissingField;
    if (value != .string) return error.InvalidFieldType;
    return value.string;
}

fn fieldArray(object: std.json.ObjectMap, name: []const u8) !std.json.Array {
    const value = object.get(name) orelse return error.MissingField;
    if (value != .array) return error.InvalidFieldType;
    return value.array;
}

fn expectTargetEntry(entry: std.json.Value, expected: ExpectedTarget) !void {
    try std.testing.expect(entry == .object);
    const object = entry.object;
    try std.testing.expectEqualStrings(expected.target, try fieldString(object, "target"));
    try std.testing.expectEqualStrings(expected.review_status, try fieldString(object, "review_status"));
    try std.testing.expectEqualStrings(expected.validation_mode, try fieldString(object, "validation_mode"));
    try std.testing.expectEqualStrings(route, try fieldString(object, "route"));
}

fn expectFixtureReviewStatusContract(source: []const u8) !void {
    var parsed = try std.json.parseFromSlice(std.json.Value, std.testing.allocator, source, .{});
    defer parsed.deinit();

    try std.testing.expect(parsed.value == .object);
    const root = parsed.value.object;
    try std.testing.expectEqualStrings("Phase 2", try fieldString(root, "phase"));
    try std.testing.expectEqualStrings("active", try fieldString(root, "status"));
    try std.testing.expectEqualStrings(route, try fieldString(root, "route"));

    const archive_scope = try fieldArray(root, "archive_target_scope");
    try std.testing.expectEqual(@as(usize, 1), archive_scope.items.len);
    try std.testing.expect(archive_scope.items[0] == .string);
    try std.testing.expectEqualStrings("x86_64-linux", archive_scope.items[0].string);

    const targets = try fieldArray(root, "cross_targets");
    try std.testing.expectEqual(expected_targets.len, targets.items.len);
    for (expected_targets, targets.items) |expected, entry| {
        try expectTargetEntry(entry, expected);
    }
}

test "phase2 cross fixture pins review status vocabulary" {
    const source = try readFixture(std.testing.allocator, fixture_path);
    defer std.testing.allocator.free(source);

    try expectFixtureReviewStatusContract(source);
}

test "review status values stay coupled to validation modes" {
    const source =
        \\{
        \\  "phase": "Phase 2",
        \\  "status": "active",
        \\  "route": "make -C zigux phase2-cross",
        \\  "archive_target_scope": ["x86_64-linux"],
        \\  "cross_targets": [
        \\    {
        \\      "target": "x86_64-linux",
        \\      "review_status": "route contract only",
        \\      "validation_mode": "archive_required",
        \\      "route": "make -C zigux phase2-cross"
        \\    },
        \\    {
        \\      "target": "aarch64-linux",
        \\      "review_status": "pinned bootstrap archive",
        \\      "validation_mode": "route_contract_only",
        \\      "route": "make -C zigux phase2-cross"
        \\    }
        \\  ]
        \\}
    ;

    try std.testing.expectError(error.TestExpectedEqual, expectFixtureReviewStatusContract(source));
}

test "review status contract rejects a stale third target" {
    const source =
        \\{
        \\  "phase": "Phase 2",
        \\  "status": "active",
        \\  "route": "make -C zigux phase2-cross",
        \\  "archive_target_scope": ["x86_64-linux"],
        \\  "cross_targets": [
        \\    {
        \\      "target": "x86_64-linux",
        \\      "review_status": "pinned bootstrap archive",
        \\      "validation_mode": "archive_required",
        \\      "route": "make -C zigux phase2-cross"
        \\    },
        \\    {
        \\      "target": "aarch64-linux",
        \\      "review_status": "route contract only",
        \\      "validation_mode": "route_contract_only",
        \\      "route": "make -C zigux phase2-cross"
        \\    },
        \\    {
        \\      "target": "riscv64-linux",
        \\      "review_status": "route contract only",
        \\      "validation_mode": "route_contract_only",
        \\      "route": "make -C zigux phase2-cross"
        \\    }
        \\  ]
        \\}
    ;

    try std.testing.expectError(error.TestExpectedEqual, expectFixtureReviewStatusContract(source));
}

test "review status contract rejects missing review text" {
    const source =
        \\{
        \\  "phase": "Phase 2",
        \\  "status": "active",
        \\  "route": "make -C zigux phase2-cross",
        \\  "archive_target_scope": ["x86_64-linux"],
        \\  "cross_targets": [
        \\    {
        \\      "target": "x86_64-linux",
        \\      "validation_mode": "archive_required",
        \\      "route": "make -C zigux phase2-cross"
        \\    },
        \\    {
        \\      "target": "aarch64-linux",
        \\      "review_status": "route contract only",
        \\      "validation_mode": "route_contract_only",
        \\      "route": "make -C zigux phase2-cross"
        \\    }
        \\  ]
        \\}
    ;

    try std.testing.expectError(error.MissingField, expectFixtureReviewStatusContract(source));
}
