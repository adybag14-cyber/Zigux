const std = @import("std");

const fixture_text = @embedFile("fixtures/phase2_cross_targets.json");
const phase2_cross_route = "make -C zigux phase2-cross";

fn fieldString(object: std.json.ObjectMap, key: []const u8) ![]const u8 {
    const value = object.get(key) orelse return error.MissingField;
    return switch (value) {
        .string => |string| string,
        else => error.InvalidFieldType,
    };
}

fn expectField(object: std.json.ObjectMap, key: []const u8, expected: []const u8) !void {
    try std.testing.expectEqualStrings(expected, try fieldString(object, key));
}

fn expectStringArray(value: std.json.Value, expected: []const []const u8) !void {
    const array = switch (value) {
        .array => |array| array,
        else => return error.InvalidFieldType,
    };
    try std.testing.expectEqual(expected.len, array.items.len);
    for (expected, array.items) |expected_item, actual_item| {
        const actual = switch (actual_item) {
            .string => |string| string,
            else => return error.InvalidFieldType,
        };
        try std.testing.expectEqualStrings(expected_item, actual);
    }
}

fn expectCrossTargets(root: std.json.ObjectMap) !void {
    const value = root.get("cross_targets") orelse return error.MissingField;
    const cross_targets = switch (value) {
        .array => |array| array,
        else => return error.InvalidFieldType,
    };

    try std.testing.expectEqual(@as(usize, 2), cross_targets.items.len);

    const x86_target = switch (cross_targets.items[0]) {
        .object => |object| object,
        else => return error.InvalidFieldType,
    };
    try expectField(x86_target, "target", "x86_64-linux");
    try expectField(x86_target, "review_status", "pinned bootstrap archive");
    try expectField(x86_target, "validation_mode", "archive_required");
    try expectField(x86_target, "route", phase2_cross_route);

    const aarch64_target = switch (cross_targets.items[1]) {
        .object => |object| object,
        else => return error.InvalidFieldType,
    };
    try expectField(aarch64_target, "target", "aarch64-linux");
    try expectField(aarch64_target, "review_status", "route contract only");
    try expectField(aarch64_target, "validation_mode", "route_contract_only");
    try expectField(aarch64_target, "route", phase2_cross_route);
}

test "phase2 cross fixture keeps the current two-target matrix contract" {
    var parsed = try std.json.parseFromSlice(std.json.Value, std.testing.allocator, fixture_text, .{});
    defer parsed.deinit();

    const root = switch (parsed.value) {
        .object => |object| object,
        else => return error.InvalidFieldType,
    };

    try expectField(root, "phase", "Phase 2");
    try expectField(root, "status", "active");
    try expectField(root, "route", phase2_cross_route);
    try expectCrossTargets(root);
}

test "phase2 cross archive scope names exactly the archive-required target" {
    var parsed = try std.json.parseFromSlice(std.json.Value, std.testing.allocator, fixture_text, .{});
    defer parsed.deinit();

    const root = switch (parsed.value) {
        .object => |object| object,
        else => return error.InvalidFieldType,
    };

    try expectStringArray(root.get("archive_target_scope") orelse return error.MissingField, &.{"x86_64-linux"});
}

test "phase2 cross route-contract target stays outside archive scope" {
    var parsed = try std.json.parseFromSlice(std.json.Value, std.testing.allocator, fixture_text, .{});
    defer parsed.deinit();

    const root = switch (parsed.value) {
        .object => |object| object,
        else => return error.InvalidFieldType,
    };

    const cross_targets = switch (root.get("cross_targets") orelse return error.MissingField) {
        .array => |array| array,
        else => return error.InvalidFieldType,
    };
    const route_contract_target = switch (cross_targets.items[1]) {
        .object => |object| object,
        else => return error.InvalidFieldType,
    };

    try expectField(route_contract_target, "target", "aarch64-linux");
    try expectField(route_contract_target, "validation_mode", "route_contract_only");
}
