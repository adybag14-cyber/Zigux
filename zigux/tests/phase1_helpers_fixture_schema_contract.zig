const std = @import("std");

const fixture_json = @embedFile("fixtures/phase1_helpers.json");

const expected_sections = [_][]const u8{
    "argv_split",
    "bitmap",
    "cmdline",
    "ctype",
    "find_bit",
    "hweight",
    "list_sort",
    "rbtree",
    "slab",
    "str_error_r",
    "string",
    "vsprintf",
    "zalloc",
};

fn expectObject(value: std.json.Value) !std.json.ObjectMap {
    return switch (value) {
        .object => |object| object,
        else => error.ExpectedObject,
    };
}

fn expectInteger(value: std.json.Value) !i64 {
    return switch (value) {
        .integer => |integer| integer,
        else => error.ExpectedInteger,
    };
}

fn expectSection(root: std.json.ObjectMap, name: []const u8) !std.json.ObjectMap {
    const value = root.get(name) orelse return error.MissingSection;
    return expectObject(value);
}

fn expectField(section: std.json.ObjectMap, name: []const u8) !void {
    try std.testing.expect(section.contains(name));
}

fn getField(section: std.json.ObjectMap, name: []const u8) !std.json.Value {
    return section.get(name) orelse return error.MissingField;
}

fn expectNoField(section: std.json.ObjectMap, name: []const u8) !void {
    try std.testing.expect(!section.contains(name));
}

test "phase1 helpers fixture keeps the closed top-level helper schema" {
    var parsed = try std.json.parseFromSlice(std.json.Value, std.testing.allocator, fixture_json, .{});
    defer parsed.deinit();

    const root = try expectObject(parsed.value);
    try std.testing.expectEqual(@as(usize, expected_sections.len), root.count());

    for (expected_sections) |section| {
        _ = try expectSection(root, section);
    }
}

test "phase1 helpers fixture keeps current replay-drift sentinels" {
    var parsed = try std.json.parseFromSlice(std.json.Value, std.testing.allocator, fixture_json, .{});
    defer parsed.deinit();

    const root = try expectObject(parsed.value);
    const find_bit = try expectSection(root, "find_bit");
    const bitmap = try expectSection(root, "bitmap");
    const string = try expectSection(root, "string");
    const rbtree = try expectSection(root, "rbtree");
    const cmdline = try expectSection(root, "cmdline");

    try expectField(find_bit, "tail_inclusive_boundary_next");
    try expectField(find_bit, "tail_inclusive_boundary_zero");
    try expectField(find_bit, "tail_inclusive_boundary_and");
    try expectNoField(find_bit, "inclusive_boundary_next");
    try expectNoField(find_bit, "past_nbits_next");

    try expectField(bitmap, "copy_values");
    try expectField(bitmap, "copy_clear_tail_values");
    try expectField(bitmap, "copy_and_extend_values");
    try expectField(bitmap, "complement_values");

    try expectField(cmdline, "signed_k");
    try expectField(cmdline, "signed_hex_k");
    try expectField(cmdline, "signed_octal_m");
    try expectField(cmdline, "saturated_positive_signed");
    try expectField(cmdline, "first_arg");
    try expectField(cmdline, "unterminated_arg");

    try expectField(rbtree, "cached_leftmost_return_serials");
    try expectField(rbtree, "cached_root_transition_serials");
    try std.testing.expectEqual(@as(i64, 184), try expectInteger(try getField(string, "strtobool_invalid")));
}
