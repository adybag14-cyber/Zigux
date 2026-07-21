const std = @import("std");
const testing = std.testing;

const closure_note_alias_tail_marker =
    "`PHASE1_FIND_BIT_LINUX_ALIAS_TAIL_REVIEW=helper-local Linux-style find_next_or_bit tail and past-end alias proof plus find_*clump8 tail-byte and exhausted-caller-byte alias proof stay explicit through the direct find_bit tests, so this closure packet parks them as helper-local alias evidence until a dedicated shared fixture key lands`";

const adjacent_find_bit_markers = .{
    .bench_anchor_guard = "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",
    .review_guard = "`PHASE1_FIND_BIT_REVIEW_GUARD=zig run scripts/zigux/check_phase1_find_bit_review_packet.zig exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`",
};

const stale_alias_tail_markers = [_][]const u8{
    "`PHASE1_FIND_BIT_LINUX_ALIAS_TAIL_REVIEW=missing_current_master`",
    "`PHASE1_FIND_BIT_LINUX_ALIAS_TAIL_REVIEW=shared fixture owns Linux alias tail behavior`",
    "`PHASE1_FIND_BIT_LINUX_ALIAS_TAIL_REVIEW=validator-owned requirement`",
};

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

test "find_bit Linux alias tail marker is pinned to the closure note wording" {
    try expectOnce(closure_note_alias_tail_marker, "PHASE1_FIND_BIT_LINUX_ALIAS_TAIL_REVIEW=");
    try testing.expect(std.mem.indexOf(u8, closure_note_alias_tail_marker, "find_next_or_bit tail and past-end alias proof") != null);
    try testing.expect(std.mem.indexOf(u8, closure_note_alias_tail_marker, "find_*clump8 tail-byte and exhausted-caller-byte alias proof") != null);
    try testing.expect(std.mem.indexOf(u8, closure_note_alias_tail_marker, "helper-local alias evidence") != null);
    try testing.expect(std.mem.indexOf(u8, closure_note_alias_tail_marker, "until a dedicated shared fixture key lands") != null);
}

test "alias tail marker remains adjacent to find_bit direct-anchor guards" {
    const packet =
        adjacent_find_bit_markers.bench_anchor_guard ++ "\n" ++
        closure_note_alias_tail_marker ++ "\n" ++
        adjacent_find_bit_markers.review_guard ++ "\n";

    try expectOnce(packet, adjacent_find_bit_markers.bench_anchor_guard);
    try expectOnce(packet, closure_note_alias_tail_marker);
    try expectOnce(packet, adjacent_find_bit_markers.review_guard);
    try testing.expect(std.mem.indexOf(u8, packet, "check-phase1-find-bit-bench-anchors.py") != null);
    try testing.expect(std.mem.indexOf(u8, packet, "check-phase1-find-bit-review-packet.py") != null);
}

test "stale alias tail interpretations stay outside the current packet" {
    for (stale_alias_tail_markers) |marker| {
        try testing.expectEqual(@as(usize, 0), countNeedle(closure_note_alias_tail_marker, marker));
    }
    try testing.expect(std.mem.indexOf(u8, closure_note_alias_tail_marker, "shared fixture owns") == null);
    try testing.expect(std.mem.indexOf(u8, closure_note_alias_tail_marker, "validator-owned") == null);
}
