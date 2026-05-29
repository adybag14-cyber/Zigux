const std = @import("std");

const smoke_source = @embedFile("phase1_host_tools_smoke.zig");
const fixture_guard_source = @embedFile("phase1_find_bit_fixture_guard.zig");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectInOrder(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const relative = std.mem.indexOf(u8, haystack[cursor..], needle) orelse return error.TestExpectedEqual;
        cursor += relative + needle.len;
    }
}

test "host-tools smoke keeps the find_bit fixture guard anchored" {
    try expectInOrder(smoke_source, &.{
        "pub const find_bit = @import(\"find_bit\");",
        "const phase1_find_bit_fixture_guard = @import(\"phase1_find_bit_fixture_guard.zig\");",
        "comptime {",
        "_ = phase1_find_bit_fixture_guard;",
    });
}

test "fixture guard remains tied to the Phase 1 helper fixture and find_bit helper" {
    try expectInOrder(fixture_guard_source, &.{
        "const find_bit = @import(\"../../tools/lib/find_bit.zig\");",
        "const fixture_bytes = @embedFile(\"fixtures/phase1_helpers.json\");",
        "tail_andnot_clamped_first: usize,",
        "tail_clump_exhausted_value: u8,",
    });
}

test "host-tools smoke keeps the direct find_bit tail anchors visible" {
    try expectContains(
        smoke_source,
        "test \"phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned\"",
    );
    try expectInOrder(smoke_source, &.{
        "find_bit.findFirstAndNotBit",
        "find_bit.find_next_andnot_bit",
        "find_bit._find_next_andnot_bit",
        "find_bit.findFirstClump8",
        "find_bit.find_first_clump8",
        "find_bit.find_next_clump8",
        "find_bit._find_next_clump8",
    });
}
