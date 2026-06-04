const std = @import("std");

const manifest_bytes = @embedFile("fixtures/phase1_helper_manifest.json");

const expected_helpers = [_][]const u8{
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

const expected_shared_replay_helpers = [_][]const u8{
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

const expected_direct_anchor_helpers = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

fn loadManifest() !std.json.Parsed(std.json.Value) {
    return std.json.parseFromSlice(std.json.Value, std.testing.allocator, manifest_bytes, .{
        .ignore_unknown_fields = true,
    });
}

fn getObject(value: std.json.Value, key: []const u8) !std.json.ObjectMap {
    const child = value.object.get(key) orelse return error.MissingManifestKey;
    if (child != .object) return error.ManifestKeyHasWrongType;
    return child.object;
}

fn getArray(value: std.json.Value, key: []const u8) !std.json.Array {
    const child = value.object.get(key) orelse return error.MissingManifestKey;
    if (child != .array) return error.ManifestKeyHasWrongType;
    return child.array;
}

fn getString(value: std.json.Value, key: []const u8) ![]const u8 {
    const child = value.object.get(key) orelse return error.MissingManifestKey;
    if (child != .string) return error.ManifestKeyHasWrongType;
    return child.string;
}

fn getInteger(value: std.json.Value, key: []const u8) !i64 {
    const child = value.object.get(key) orelse return error.MissingManifestKey;
    if (child != .integer) return error.ManifestKeyHasWrongType;
    return child.integer;
}

fn getOptionalArray(value: std.json.Value, key: []const u8) !?std.json.Array {
    const child = value.object.get(key) orelse return null;
    if (child != .array) return error.ManifestKeyHasWrongType;
    return child.array;
}

fn expectStringList(expected: []const []const u8, actual: std.json.Array) !void {
    try std.testing.expectEqual(expected.len, actual.items.len);
    for (expected, actual.items) |expected_item, actual_item| {
        if (actual_item != .string) return error.ManifestKeyHasWrongType;
        try std.testing.expectEqualStrings(expected_item, actual_item.string);
    }
}

fn containsString(items: std.json.Array, wanted: []const u8) bool {
    for (items.items) |item| {
        if (item == .string and std.mem.eql(u8, item.string, wanted)) return true;
    }
    return false;
}

fn expectAnchorHasReviewContract(anchor: std.json.ObjectMap) !void {
    const helper_test_anchors = anchor.get("helper_test_anchors") orelse return error.MissingManifestKey;
    if (helper_test_anchors != .array) return error.ManifestKeyHasWrongType;
    try std.testing.expect(helper_test_anchors.array.items.len > 0);
    const next_safe_step_note = anchor.get("next_safe_step_note") orelse return error.MissingManifestKey;
    if (next_safe_step_note != .string) return error.ManifestKeyHasWrongType;
}

test "phase1 helper manifest keeps the closed helper roster exact" {
    var parsed = try loadManifest();
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("Phase 1", try getString(manifest, "phase"));
    try std.testing.expectEqualStrings("closed", try getString(manifest, "status"));
    try std.testing.expectEqual(@as(i64, expected_helpers.len), try getInteger(manifest, "helper_count"));
    try expectStringList(&expected_helpers, try getArray(manifest, "helpers"));
}

test "phase1 helper manifest keeps shared replay and direct anchor lanes disjoint" {
    var parsed = try loadManifest();
    defer parsed.deinit();
    const sequencing = std.json.Value{ .object = try getObject(parsed.value, "lane_sequencing") };
    const shared_replay_helpers = try getArray(sequencing, "shared_replay_parked_helpers");
    const direct_anchor_helpers = try getArray(sequencing, "direct_anchor_followup_helpers");

    try expectStringList(&expected_shared_replay_helpers, shared_replay_helpers);
    try expectStringList(&expected_direct_anchor_helpers, direct_anchor_helpers);

    for (shared_replay_helpers.items) |shared_helper| {
        try std.testing.expect(!containsString(direct_anchor_helpers, shared_helper.string));
    }
    for (expected_helpers) |helper| {
        const in_shared = containsString(shared_replay_helpers, helper);
        const in_direct = containsString(direct_anchor_helpers, helper);
        try std.testing.expect(in_shared != in_direct);
    }
    try std.testing.expect(std.mem.indexOf(u8, try getString(sequencing, "rule_summary"), "parked on shared replay") != null);
    try std.testing.expect(std.mem.indexOf(u8, try getString(sequencing, "anti_overlap_rule"), "Do not reopen Phase 1") != null);
}

test "phase1 helper manifest keeps direct helpers reviewable from anchors" {
    var parsed = try loadManifest();
    defer parsed.deinit();
    const anchors = try getObject(parsed.value, "review_anchors");

    for (expected_direct_anchor_helpers) |helper| {
        const anchor = anchors.get(helper) orelse return error.MissingManifestKey;
        if (anchor != .object) return error.ManifestKeyHasWrongType;
        try expectAnchorHasReviewContract(anchor.object);
    }

    const bitmap = std.json.Value{ .object = anchors.get("tools/lib/bitmap.zig").?.object };
    try std.testing.expect(containsString(try getArray(bitmap, "parity_fixture_keys"), "truncated_scnprintf"));
    if (try getOptionalArray(bitmap, "parity_fixture_keys")) |keys| {
        if (containsString(keys, "copy_values")) {
            try std.testing.expect(containsString(keys, "copy_and_extend_values"));
        }
    }
    if (try getOptionalArray(bitmap, "shared_logical_fixture_keys")) |keys| {
        try std.testing.expect(containsString(keys, "andnot_values"));
    }
    if (try getOptionalArray(bitmap, "shared_range_fixture_keys")) |keys| {
        try std.testing.expect(containsString(keys, "empty_after_zero"));
    }

    const find_bit = std.json.Value{ .object = anchors.get("tools/lib/find_bit.zig").?.object };
    if (try getOptionalArray(find_bit, "parity_fixture_keys")) |keys| {
        try std.testing.expect(containsString(keys, "bits_per_long"));
        try std.testing.expect(containsString(keys, "last"));
    }
}
