const std = @import("std");
const testing = std.testing;

const helper_fixture = @embedFile("fixtures/phase1_helpers.json");

const closure_alias_tail_marker =
    "`PHASE1_FIND_BIT_LINUX_ALIAS_TAIL_REVIEW=helper-local Linux-style find_next_or_bit tail and past-end alias proof plus find_*clump8 tail-byte and exhausted-caller-byte alias proof stay explicit through the direct find_bit tests, so this closure packet parks them as helper-local alias evidence until a dedicated shared fixture key lands`";

const stale_alias_tail_ownership = [_][]const u8{
    "PHASE1_FIND_BIT_LINUX_ALIAS_TAIL_REVIEW=missing_current_master",
    "PHASE1_FIND_BIT_LINUX_ALIAS_TAIL_REVIEW=validator-owned",
    "shared fixture owns Linux-style alias tail proof",
    "dedicated shared Linux alias fixture key",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(512 * 1024));
}

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

fn expectOnce(haystack: []const u8, needle: []const u8) !void {
    try testing.expectEqual(@as(usize, 1), countNeedle(haystack, needle));
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try testing.expectEqual(@as(usize, 0), countNeedle(haystack, needle));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "closure note parks find_bit Linux alias tail proof as helper-local" {
    const closure_note = try readRepoFile(testing.allocator, "Documentation/zigux/phase1-closure.md");
    defer testing.allocator.free(closure_note);

    try expectOnce(closure_note, closure_alias_tail_marker);
    try expectContains(closure_alias_tail_marker, "find_next_or_bit tail and past-end alias proof");
    try expectContains(closure_alias_tail_marker, "find_*clump8 tail-byte and exhausted-caller-byte alias proof");
    try expectContains(closure_alias_tail_marker, "direct find_bit tests");
    try expectContains(closure_alias_tail_marker, "until a dedicated shared fixture key lands");

    for (stale_alias_tail_ownership) |marker| {
        try expectAbsent(closure_note, marker);
    }
}

test "lane note keeps the alias-tail packet inside the find_bit direct owner" {
    const lane_note = try readRepoFile(testing.allocator, "Documentation/zigux/phase1-host-helper-lane-sequencing.md");
    defer testing.allocator.free(lane_note);

    try expectContains(lane_note, "`PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local");
    try expectContains(lane_note, "Linux-style, and underscore andnot coverage");
    try expectContains(lane_note, "tail-word skip anchors plus the committed tail-clamped and tail-inclusive-boundary find_bit replay fields");
    try expectContains(lane_note, "`PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift");
    try expectContains(lane_note, "Linux-style alias coverage including the shipped andnot scan entry points");
    try expectContains(lane_note, "committed tail-clamped or tail-inclusive-boundary replay drift");
    try expectContains(lane_note, "do not reopen older saved validator cues or neighboring helper families");
}

test "find_bit helper exposes the Linux alias tail and clump8 direct anchors" {
    const find_bit_helper = try readRepoFile(testing.allocator, "tools/lib/find_bit.zig");
    defer testing.allocator.free(find_bit_helper);

    try expectContains(find_bit_helper, "pub fn find_next_or_bit");
    try expectContains(find_bit_helper, "pub fn _find_next_or_bit");
    try expectContains(find_bit_helper, "pub fn find_next_clump8");
    try expectContains(find_bit_helper, "pub fn _find_next_clump8");
    try expectContains(find_bit_helper, "test \"clump8 scans mask tail bits beyond nbits\"");
    try expectContains(find_bit_helper, "test \"clump8 scans leave the caller byte untouched when no set bit remains\"");
    try expectContains(find_bit_helper, "test \"clump8 zero-bit and past-end windows leave the caller byte untouched\"");
    try expectContains(find_bit_helper, "test \"clump8 past-end scans return without reading bitmap words\"");
    try expectContains(find_bit_helper, "test \"Linux-style aliases mirror the primary find helpers, including andnot\"");
}

test "shared fixture carries replay tails without claiming Linux alias-tail ownership" {
    try expectContains(helper_fixture, "\"tail_andnot_clamped_first\"");
    try expectContains(helper_fixture, "\"tail_andnot_clamped_next\"");
    try expectContains(helper_fixture, "\"tail_andnot_clamped_exhausted\"");
    try expectContains(helper_fixture, "\"tail_clump_first\"");
    try expectContains(helper_fixture, "\"tail_clump_first_value\"");
    try expectContains(helper_fixture, "\"tail_clump_next\"");
    try expectContains(helper_fixture, "\"tail_clump_next_value\"");
    try expectContains(helper_fixture, "\"tail_clump_exhausted\"");
    try expectContains(helper_fixture, "\"tail_clump_exhausted_value\"");
    try expectAbsent(helper_fixture, "\"linux_alias_tail_values\"");
    try expectAbsent(helper_fixture, "\"find_bit_linux_alias_tail_anchor\"");
}
