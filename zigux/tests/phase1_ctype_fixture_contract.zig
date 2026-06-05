const std = @import("std");

const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");

const CtypeFixture = struct {
    mask_A: u8,
    mask_a: u8,
    mask_space: u8,
    isalnum_A: bool,
    isalpha_z: bool,
    isdigit_7: bool,
    isspace_tab: bool,
    isxdigit_f: bool,
    ispunct_bang: bool,
    tolower_A: u8,
    toupper_z: u8,
    isodigit_7: bool,
    isodigit_8: bool,
};

const Fixture = struct {
    ctype: CtypeFixture,
};

fn loadFixture() !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, std.testing.allocator, fixture_bytes, .{
        .ignore_unknown_fields = true,
    });
}

fn expectNeedleAfter(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierNeedle;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterNeedle;
    try std.testing.expect(earlier_index < later_index);
}

test "phase 1 ctype fixture pins masks and predicates" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const ctype = parsed.value.ctype;

    try std.testing.expectEqual(@as(u8, 65), ctype.mask_A);
    try std.testing.expectEqual(@as(u8, 66), ctype.mask_a);
    try std.testing.expectEqual(@as(u8, 160), ctype.mask_space);

    try std.testing.expect(ctype.isalnum_A);
    try std.testing.expect(ctype.isalpha_z);
    try std.testing.expect(ctype.isdigit_7);
    try std.testing.expect(ctype.isspace_tab);
    try std.testing.expect(ctype.isxdigit_f);
    try std.testing.expect(ctype.ispunct_bang);
}

test "phase 1 ctype fixture pins case and octal boundaries" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const ctype = parsed.value.ctype;

    try std.testing.expectEqual(@as(u8, 'a'), ctype.tolower_A);
    try std.testing.expectEqual(@as(u8, 'Z'), ctype.toupper_z);
    try std.testing.expect(ctype.isodigit_7);
    try std.testing.expect(!ctype.isodigit_8);
}

test "phase 1 ctype fixture remains between cmdline and hweight sections" {
    try expectNeedleAfter(fixture_bytes, "\"cmdline\"", "\"ctype\"");
    try expectNeedleAfter(fixture_bytes, "\"ctype\"", "\"hweight\"");
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, fixture_bytes, "\"ctype\""));
}
