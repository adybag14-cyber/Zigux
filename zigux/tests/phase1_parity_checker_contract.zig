const std = @import("std");

const manifest_json = @embedFile("fixtures/phase1_helper_manifest.json");
const replay_zig = @embedFile("phase1_helpers.zig");

const expected_gate_paths = [_][]const u8{
    "ARTIFACT_DIFF_REL",
    "FIXTURE_REL",
    "MANIFEST_REL",
    "BLOCKERS_REL",
    "REPLAY_REL",
    "REPLAY_BUILD_REL",
    "HARNESS_REL",
};

const expected_sections = [_][]const u8{
    "find_bit",
    "bitmap",
    "string",
    "rbtree",
    "argv_split",
    "cmdline",
    "ctype",
    "hweight",
    "list_sort",
    "zalloc",
    "str_error_r",
    "slab",
    "vsprintf",
};

const expected_direct_helpers = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
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

fn getField(object: std.json.ObjectMap, key: []const u8) !std.json.Value {
    return object.get(key) orelse error.MissingField;
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

test "phase1 parity checker keeps canonical gate paths visible" {
    const checker_py = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        "scripts/zigux/check-phase1-parity.py",
        std.testing.allocator,
        .limited(1024 * 1024),
    );
    defer std.testing.allocator.free(checker_py);

    for (expected_gate_paths) |path| {
        try expectContains(checker_py, path);
    }

    for (expected_sections) |section| {
        try expectContains(checker_py, section);
    }

    try expectContains(manifest_json, "shared_replay_parked_helpers");
    try expectContains(manifest_json, "direct_anchor_followup_helpers");
    try expectContains(checker_py, "PHASE1_PARITY=pass");
}

test "phase1 parity checker agrees with the closed manifest partition" {
    const checker_py = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        "scripts/zigux/check-phase1-parity.py",
        std.testing.allocator,
        .limited(1024 * 1024),
    );
    defer std.testing.allocator.free(checker_py);

    var parsed = try std.json.parseFromSlice(std.json.Value, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const root = try expectObject(parsed.value);
    const lane_sequencing = try expectObject(try getField(root, "lane_sequencing"));
    const helpers = try expectArray(try getField(root, "helpers"));
    const parked = try expectArray(try getField(lane_sequencing, "shared_replay_parked_helpers"));
    const direct = try expectArray(try getField(lane_sequencing, "direct_anchor_followup_helpers"));

    try std.testing.expectEqualStrings("Phase 1", try expectString(try getField(root, "phase")));
    try std.testing.expectEqualStrings("closed", try expectString(try getField(root, "status")));
    try std.testing.expectEqual(@as(i64, 13), try expectInteger(try getField(root, "helper_count")));
    try std.testing.expectEqual(@as(usize, 13), helpers.items.len);
    try std.testing.expectEqual(@as(usize, 9), parked.items.len);
    try std.testing.expectEqual(@as(usize, expected_direct_helpers.len), direct.items.len);

    var helper_set = try stringSetFromArray(std.testing.allocator, helpers);
    defer helper_set.deinit();
    var parked_set = try stringSetFromArray(std.testing.allocator, parked);
    defer parked_set.deinit();
    var direct_set = try stringSetFromArray(std.testing.allocator, direct);
    defer direct_set.deinit();

    for (expected_direct_helpers) |helper| {
        try std.testing.expect(helper_set.contains(helper));
        try std.testing.expect(direct_set.contains(helper));
        try std.testing.expect(!parked_set.contains(helper));
        try expectContains(manifest_json, helper);
    }
}

test "phase1 parity checker stays anchored to replay boundary markers" {
    const checker_py = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        "scripts/zigux/check-phase1-parity.py",
        std.testing.allocator,
        .limited(1024 * 1024),
    );
    defer std.testing.allocator.free(checker_py);

    const checker_markers = [_][]const u8{
        "inclusive_boundary_next",
        "tail_clamped_empty_last",
        "truncated_scnprintf_len",
        "replace_char_cstr_bytes",
        "match_iterator_serials",
    };

    for (checker_markers) |marker| {
        try expectContains(checker_py, marker);
    }

    const replay_markers = [_][]const u8{
        "fixture.find_bit.inclusive_boundary_next",
        "fixture.find_bit.tail_clamped_empty_last",
        "fixture.bitmap.truncated_scnprintf_len",
        "fixture.string.replace_char_cstr_bytes",
        "fixture.rbtree.match_iterator_serials",
    };

    for (replay_markers) |marker| {
        try expectContains(replay_zig, marker);
    }

    try expectContains(replay_zig, "phase 1 helper ports match committed parity fixture");
}
