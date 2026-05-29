const std = @import("std");

const replay_blockers_json = @embedFile("fixtures/phase1_replay_blockers.json");

const expected_shared_helpers = [_][]const u8{
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
};

const expected_direct_helpers = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

const expected_all_helpers = [_][]const u8{
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
};

fn getField(object: std.json.ObjectMap, key: []const u8) !std.json.Value {
    return object.get(key) orelse error.MissingField;
}

fn expectObject(value: std.json.Value) !std.json.ObjectMap {
    return switch (value) {
        .object => |object| object,
        else => error.ExpectedObject,
    };
}

fn expectArray(value: std.json.Value) !std.json.Array {
    return switch (value) {
        .array => |array| array,
        else => error.ExpectedArray,
    };
}

fn expectString(value: std.json.Value) ![]const u8 {
    return switch (value) {
        .string => |string| string,
        else => error.ExpectedString,
    };
}

fn expectInteger(value: std.json.Value) !i64 {
    return switch (value) {
        .integer => |integer| integer,
        else => error.ExpectedInteger,
    };
}

fn expectBool(value: std.json.Value) !bool {
    return switch (value) {
        .bool => |boolean| boolean,
        else => error.ExpectedBool,
    };
}

fn expectStringValue(value: std.json.Value, expected: []const u8) !void {
    try std.testing.expectEqualStrings(expected, try expectString(value));
}

fn expectStringArray(array: std.json.Array, expected: []const []const u8) !void {
    try std.testing.expectEqual(expected.len, array.items.len);
    for (expected, 0..) |expected_helper, index| {
        try expectStringValue(array.items[index], expected_helper);
    }
}

test "phase1 replay blockers keep lane sequencing partition explicit" {
    var parsed = try std.json.parseFromSlice(std.json.Value, std.testing.allocator, replay_blockers_json, .{});
    defer parsed.deinit();

    const root = try expectObject(parsed.value);
    try expectStringValue(try getField(root, "status"), "parked");

    const lane_sequencing = try expectObject(try getField(root, "lane_sequencing"));
    try expectStringValue(
        try getField(lane_sequencing, "manifest"),
        "zigux/tests/fixtures/phase1_helper_manifest.json",
    );
    try std.testing.expectEqual(
        @as(i64, expected_shared_helpers.len),
        try expectInteger(try getField(lane_sequencing, "shared_replay_parked_helper_count")),
    );
    try std.testing.expectEqual(
        @as(i64, expected_direct_helpers.len),
        try expectInteger(try getField(lane_sequencing, "direct_anchor_followup_helper_count")),
    );

    try expectStringArray(
        try expectArray(try getField(lane_sequencing, "shared_replay_parked_helpers")),
        &expected_shared_helpers,
    );
    try expectStringArray(
        try expectArray(try getField(lane_sequencing, "direct_anchor_followup_helpers")),
        &expected_direct_helpers,
    );

    const anti_overlap_rule = try expectString(try getField(lane_sequencing, "anti_overlap_rule"));
    try std.testing.expect(std.mem.indexOf(u8, anti_overlap_rule, "Do not reopen Phase 1") != null);
    try std.testing.expect(std.mem.indexOf(u8, anti_overlap_rule, "direct-anchor helpers") != null);
}

test "phase1 replay blockers keep the slab fixture mismatch pinned" {
    var parsed = try std.json.parseFromSlice(std.json.Value, std.testing.allocator, replay_blockers_json, .{});
    defer parsed.deinit();

    const root = try expectObject(parsed.value);
    const replay = try expectObject(try getField(root, "replay"));
    try expectStringValue(try getField(replay, "path"), "zigux/tests/phase1_helpers.zig");
    try expectStringValue(try getField(replay, "state"), "blocked");

    const blockers = try expectArray(try getField(replay, "blockers"));
    try std.testing.expectEqual(@as(usize, 1), blockers.items.len);

    const blocker = try expectObject(blockers.items[0]);
    try expectStringValue(try getField(blocker, "id"), "phase1_helpers_zig_slab_zero_after_kmalloc");
    try expectStringValue(try getField(blocker, "kind"), "fixture_mismatch");
    try expectStringValue(try getField(blocker, "path"), "tools/lib/slab.zig");
    try expectStringValue(try getField(blocker, "field"), "slab.zero_after_kmalloc");
    try std.testing.expect(try expectBool(try getField(blocker, "expected")));
    try std.testing.expect(!(try expectBool(try getField(blocker, "actual"))));

    const evidence = try expectString(try getField(blocker, "evidence"));
    try std.testing.expect(std.mem.indexOf(u8, evidence, "phase1_helpers.zig:595") != null);
    try std.testing.expect(std.mem.indexOf(u8, evidence, "produced `false`") != null);
}

test "phase1 replay blockers keep C harness recovery blocked on missing C sources" {
    var parsed = try std.json.parseFromSlice(std.json.Value, std.testing.allocator, replay_blockers_json, .{});
    defer parsed.deinit();

    const root = try expectObject(parsed.value);
    const c_harness = try expectObject(try getField(root, "c_harness"));
    try expectStringValue(
        try getField(c_harness, "path"),
        "zigux/tests/fixtures/phase1_helpers_c_harness.c",
    );
    try expectStringValue(try getField(c_harness, "state"), "blocked");
    try expectStringValue(
        try getField(c_harness, "blocker_id"),
        "phase1_helpers_c_harness_missing_c_sources",
    );
    try std.testing.expectEqual(@as(i64, 13), try expectInteger(try getField(c_harness, "helper_count")));

    const helpers = try expectArray(try getField(c_harness, "helpers"));
    try expectStringArray(helpers, &expected_all_helpers);

    const reason = try expectString(try getField(c_harness, "reason"));
    try std.testing.expect(std.mem.indexOf(u8, reason, "tools/lib/*.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, reason, "current master no longer ships") != null);
}
