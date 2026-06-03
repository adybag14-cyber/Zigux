const std = @import("std");
const testing = std.testing;

const manifest_text = @embedFile("fixtures/phase2_tool_manifest.json");

const required_fixdep_support = [_][]const u8{
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/fixdep.zig",
    "zigux/tests/fixtures/fixdep/cases.json",
};

const required_fixture_families = [_][]const u8{
    "zigux/tests/fixtures/fixdep/sample.",
    "zigux/tests/fixtures/fixdep/sample2.",
    "zigux/tests/fixtures/fixdep/sample_comment_continuation",
    "zigux/tests/fixtures/fixdep/sample_comment_only",
    "zigux/tests/fixtures/fixdep/sample_concatenated",
    "zigux/tests/fixtures/fixdep/sample_dependency_continuation",
    "zigux/tests/fixtures/fixdep/sample_double_backslash_comment",
    "zigux/tests/fixtures/fixdep/sample_escaped_colon",
    "zigux/tests/fixtures/fixdep/sample_escaped_space",
    "zigux/tests/fixtures/fixdep/sample_missing_dep",
    "zigux/tests/fixtures/fixdep/sample_multi_target",
    "zigux/tests/fixtures/fixdep/sample_output_write",
};

const required_edge_fixture_names = [_][]const u8{
    "zigux/tests/fixtures/fixdep/dep:colon.so",
    "zigux/tests/fixtures/fixdep/dep\\ name.rmeta",
    "zigux/tests/fixtures/fixdep/escaped\\ space-config.h",
    "zigux/tests/fixtures/fixdep/shared#config.h",
    "zigux/tests/fixtures/fixdep/shared:config.h",
};

fn parseManifest(allocator: std.mem.Allocator) !std.json.Parsed(std.json.Value) {
    return std.json.parseFromSlice(std.json.Value, allocator, manifest_text, .{});
}

fn objectField(object: std.json.ObjectMap, key: []const u8) !std.json.Value {
    return object.get(key) orelse error.MissingField;
}

fn stringField(object: std.json.ObjectMap, key: []const u8) ![]const u8 {
    const value = try objectField(object, key);
    if (value != .string) return error.ExpectedString;
    return value.string;
}

fn arrayField(object: std.json.ObjectMap, key: []const u8) !std.json.Array {
    const value = try objectField(object, key);
    if (value != .array) return error.ExpectedArray;
    return value.array;
}

fn presentSurfaces(root: std.json.Value) !std.json.ObjectMap {
    if (root != .object) return error.ExpectedObject;
    const value = try objectField(root.object, "present_surfaces");
    if (value != .object) return error.ExpectedObject;
    return value.object;
}

fn fixdepSupport(root: std.json.Value) !std.json.Array {
    return arrayField(try presentSurfaces(root), "fixdep_support");
}

fn containsExact(values: std.json.Array, expected: []const u8) bool {
    for (values.items) |value| {
        if (value == .string and std.mem.eql(u8, value.string, expected)) return true;
    }
    return false;
}

fn containsPrefix(values: std.json.Array, expected_prefix: []const u8) bool {
    for (values.items) |value| {
        if (value == .string and std.mem.startsWith(u8, value.string, expected_prefix)) return true;
    }
    return false;
}

test "fixdep closure support keeps public checker and Zig replay anchors" {
    var parsed = try parseManifest(testing.allocator);
    defer parsed.deinit();

    const support = try fixdepSupport(parsed.value);
    try testing.expect(support.items.len >= 60);
    for (required_fixdep_support) |path| {
        try testing.expect(containsExact(support, path));
    }
}

test "fixdep closure support keeps fixture families and escaped-name cases visible" {
    var parsed = try parseManifest(testing.allocator);
    defer parsed.deinit();

    const support = try fixdepSupport(parsed.value);
    for (required_fixture_families) |prefix| {
        try testing.expect(containsPrefix(support, prefix));
    }
    for (required_edge_fixture_names) |path| {
        try testing.expect(containsExact(support, path));
    }
}

test "phase2 closure manifest stays active and gap-free for fixdep closure review" {
    var parsed = try parseManifest(testing.allocator);
    defer parsed.deinit();

    const root = parsed.value;
    if (root != .object) return error.ExpectedObject;
    try testing.expectEqualStrings("Phase 2", try stringField(root.object, "phase"));
    try testing.expectEqualStrings("active", try stringField(root.object, "status"));

    const gaps = try arrayField(root.object, "repo_reality_gaps");
    try testing.expectEqual(@as(usize, 0), gaps.items.len);

    const support = try fixdepSupport(root);
    try testing.expect(containsExact(support, "scripts/zigux/check-phase2-fixdep-gate.py"));
    try testing.expect(containsExact(support, "scripts/zigux/check-fixdep-diff.py"));
}
