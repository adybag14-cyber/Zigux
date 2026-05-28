const std = @import("std");

const manifest_json = @embedFile("fixtures/phase1_helper_manifest.json");

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

const expected_direct_helpers = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
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

fn stringSetFromArray(
    allocator: std.mem.Allocator,
    array: std.json.Array,
) !std.StringHashMap(void) {
    var set = std.StringHashMap(void).init(allocator);
    errdefer set.deinit();

    for (array.items) |item| {
        const string = try expectString(item);
        try set.put(string, {});
    }

    return set;
}

test "phase1 manifest keeps the host-tools lane partition stable" {
    var parsed = try std.json.parseFromSlice(std.json.Value, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const root = try expectObject(parsed.value);
    const phase = try expectString(try getField(root, "phase"));
    const status = try expectString(try getField(root, "status"));
    const helper_count = try expectInteger(try getField(root, "helper_count"));
    const helpers = try expectArray(try getField(root, "helpers"));

    const lane_sequencing = try expectObject(try getField(root, "lane_sequencing"));
    const parked = try expectArray(try getField(lane_sequencing, "shared_replay_parked_helpers"));
    const direct = try expectArray(try getField(lane_sequencing, "direct_anchor_followup_helpers"));

    try std.testing.expectEqualStrings("Phase 1", phase);
    try std.testing.expectEqualStrings("closed", status);
    try std.testing.expectEqual(@as(i64, expected_all_helpers.len), helper_count);
    try std.testing.expectEqual(@as(usize, @intCast(helper_count)), helpers.items.len);
    try std.testing.expectEqual(@as(usize, 9), parked.items.len);
    try std.testing.expectEqual(@as(usize, expected_direct_helpers.len), direct.items.len);

    var helper_set = try stringSetFromArray(std.testing.allocator, helpers);
    defer helper_set.deinit();
    var parked_set = try stringSetFromArray(std.testing.allocator, parked);
    defer parked_set.deinit();
    var direct_set = try stringSetFromArray(std.testing.allocator, direct);
    defer direct_set.deinit();

    for (expected_all_helpers) |helper| {
        try std.testing.expect(helper_set.contains(helper));
    }

    for (expected_direct_helpers) |helper| {
        try std.testing.expect(direct_set.contains(helper));
        try std.testing.expect(helper_set.contains(helper));
    }

    var direct_iter = direct_set.iterator();
    while (direct_iter.next()) |entry| {
        try std.testing.expect(!parked_set.contains(entry.key_ptr.*));
    }

    var helper_iter = helper_set.iterator();
    while (helper_iter.next()) |entry| {
        const helper = entry.key_ptr.*;
        try std.testing.expect(direct_set.contains(helper) or parked_set.contains(helper));
    }
}

test "phase1 manifest keeps direct-anchor review packets non-empty" {
    var parsed = try std.json.parseFromSlice(std.json.Value, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const root = try expectObject(parsed.value);
    const review_anchors = try expectObject(try getField(root, "review_anchors"));

    for (expected_direct_helpers) |helper| {
        const helper_review = try expectObject(review_anchors.get(helper) orelse return error.MissingReviewAnchor);
        const helper_test_anchors = try expectArray(try getField(helper_review, "helper_test_anchors"));
        const next_safe_step_note = try expectString(try getField(helper_review, "next_safe_step_note"));

        try std.testing.expect(helper_test_anchors.items.len != 0);
        try std.testing.expect(next_safe_step_note.len != 0);
    }
}
