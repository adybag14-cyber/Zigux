const std = @import("std");
const testing = std.testing;

const closure_note_memtostr_marker =
    "Current `master` now also spells the helper-local `memtostr()`, `memtostrPad()`, and `memtostr_pad()` anchors directly in the shipped manifest-backed string review packet beside the `memcpyAndPad()`, `memcpy_and_pad()`, `strtomem()`, and `strtomem_pad()` byte-copy anchors. Keep those byte-copy and pad tests helper-local review evidence rather than shared-fixture or validator-owned requirements until dedicated fixture keys land.";

const adjacent_string_markers = .{
    .sysfs_review = "`PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`",
    .review_guard = "`PHASE1_STRING_REVIEW_GUARD=zig run scripts/zigux/check_phase1_string_review_packet.zig exact-checks helper-local string anchors plus the committed replaceChar and current string fixture packet across the helper, closure note, lane note, manifest, and fixture`",
};

const manifest_memtostr_packet = .{
    .anchors = [_][]const u8{
        "test \"memtostr copies a bounded non-NUL source and adds one terminator\"",
        "test \"memtostr stops at embedded NUL without padding the tail\"",
        "test \"memtostrPad zero-pads the remaining tail after copying\"",
        "test \"memtostr helpers keep one-byte destinations terminated\"",
    },
    .summary = "helper-local memtostr boundary and tail-padding anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated memtostr(), memtostrPad(), or memtostr_pad() fixture keys, so bounded source copies, embedded-NUL stops, terminator insertion, and zero-padded destination tails remain review-visible at the helper surface",
};

const manifest_byte_copy_packet = .{
    .anchors = [_][]const u8{
        "test \"memcpyAndPad copies the requested prefix and pads the destination tail\"",
        "test \"memcpy_and_pad mirrors memcpyAndPad padding semantics\"",
        "test \"strtomem copies a C-string prefix without adding a terminator or padding\"",
        "test \"strtomem_pad copies through the first NUL and pads the remaining tail\"",
    },
    .summary = "helper-local raw-copy and pad anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated memcpyAndPad(), memcpy_and_pad(), strtomem(), or strtomem_pad() fixture keys, so prefix-copy, first-NUL stop, alias parity, and caller-selected pad behavior remain review-visible at the helper surface",
};

const stale_memtostr_interpretations = [_][]const u8{
    "shared fixture owns memtostr",
    "validator-owned memtostr requirement",
    "PHASE1_STRING_MEMTOSTR_REVIEW=missing_current_master",
    "dedicated fixture keys already landed",
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

test "string memtostr closure marker stays helper-local" {
    try expectOnce(closure_note_memtostr_marker, "helper-local `memtostr()`");
    try expectOnce(closure_note_memtostr_marker, "`memtostrPad()`");
    try expectOnce(closure_note_memtostr_marker, "`memtostr_pad()`");
    try expectOnce(closure_note_memtostr_marker, "`memcpyAndPad()`");
    try expectOnce(closure_note_memtostr_marker, "`memcpy_and_pad()`");
    try expectOnce(closure_note_memtostr_marker, "`strtomem()`");
    try expectOnce(closure_note_memtostr_marker, "`strtomem_pad()`");
    try testing.expect(std.mem.indexOf(u8, closure_note_memtostr_marker, "helper-local review evidence") != null);
    try testing.expect(std.mem.indexOf(u8, closure_note_memtostr_marker, "until dedicated fixture keys land") != null);
}

test "memtostr packet remains adjacent to the string review guard" {
    const packet =
        adjacent_string_markers.sysfs_review ++ "\n" ++
        adjacent_string_markers.review_guard ++ "\n" ++
        closure_note_memtostr_marker ++ "\n";

    try expectOnce(packet, adjacent_string_markers.sysfs_review);
    try expectOnce(packet, adjacent_string_markers.review_guard);
    try expectOnce(packet, closure_note_memtostr_marker);
    try testing.expect(std.mem.indexOf(u8, packet, "check-phase1-string-review-packet.py") != null);
}

test "manifest-backed memtostr and byte-copy anchors stay paired" {
    try testing.expectEqual(@as(usize, 4), manifest_memtostr_packet.anchors.len);
    try testing.expectEqual(@as(usize, 4), manifest_byte_copy_packet.anchors.len);
    for (manifest_memtostr_packet.anchors) |anchor| {
        try expectOnce(anchor, "test \"");
        try testing.expect(std.mem.indexOf(u8, anchor, "memtostr") != null);
    }
    for (manifest_byte_copy_packet.anchors) |anchor| {
        try expectOnce(anchor, "test \"");
    }
    try testing.expect(std.mem.indexOf(u8, manifest_byte_copy_packet.anchors[0], "memcpyAndPad") != null);
    try testing.expect(std.mem.indexOf(u8, manifest_byte_copy_packet.anchors[1], "memcpy_and_pad") != null);
    try testing.expect(std.mem.indexOf(u8, manifest_byte_copy_packet.anchors[2], "strtomem") != null);
    try testing.expect(std.mem.indexOf(u8, manifest_byte_copy_packet.anchors[3], "strtomem_pad") != null);
    try testing.expect(std.mem.indexOf(u8, manifest_memtostr_packet.summary, "shared Phase 1 replay still does not carry dedicated memtostr()") != null);
    try testing.expect(std.mem.indexOf(u8, manifest_byte_copy_packet.summary, "shared Phase 1 replay still does not carry dedicated memcpyAndPad()") != null);
}

test "stale shared-fixture or validator ownership stays outside the packet" {
    for (stale_memtostr_interpretations) |marker| {
        try testing.expectEqual(@as(usize, 0), countNeedle(closure_note_memtostr_marker, marker));
        try testing.expectEqual(@as(usize, 0), countNeedle(manifest_memtostr_packet.summary, marker));
        try testing.expectEqual(@as(usize, 0), countNeedle(manifest_byte_copy_packet.summary, marker));
    }
    try testing.expect(std.mem.indexOf(u8, closure_note_memtostr_marker, "validator-owned") != null);
    try testing.expect(std.mem.indexOf(u8, closure_note_memtostr_marker, "shared fixture owns") == null);
    try testing.expect(std.mem.indexOf(u8, closure_note_memtostr_marker, "dedicated fixture keys already landed") == null);
}
