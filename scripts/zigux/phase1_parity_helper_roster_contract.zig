const std = @import("std");
const source = @embedFile("check-phase1-parity.py");

fn requireContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn requireOrdered(markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const offset = std.mem.indexOf(u8, source[cursor..], marker) orelse {
            std.debug.print("missing ordered marker: {s}\n", .{marker});
            return error.TestExpectedEqual;
        };
        cursor += offset + marker.len;
    }
}

test "phase1 parity checker keeps the fixture section roster in committed order" {
    try requireContains("EXPECTED_SECTIONS = (");
    try requireOrdered(&.{
        "\"find_bit\",",
        "\"bitmap\",",
        "\"string\",",
        "\"rbtree\",",
        "\"argv_split\",",
        "\"cmdline\",",
        "\"ctype\",",
        "\"hweight\",",
        "\"list_sort\",",
        "\"zalloc\",",
        "\"str_error_r\",",
        "\"slab\",",
        "\"vsprintf\",",
    });
    try requireContains("PHASE1_PARITY_SECTION_COUNT={len(EXPECTED_SECTIONS)}");
}

test "phase1 parity checker keeps the 13 helper source roster in path order" {
    try requireContains("EXPECTED_HELPERS = (");
    try requireOrdered(&.{
        "\"tools/lib/argv_split.zig\",",
        "\"tools/lib/bitmap.zig\",",
        "\"tools/lib/cmdline.zig\",",
        "\"tools/lib/ctype.zig\",",
        "\"tools/lib/find_bit.zig\",",
        "\"tools/lib/hweight.zig\",",
        "\"tools/lib/list_sort.zig\",",
        "\"tools/lib/rbtree.zig\",",
        "\"tools/lib/slab.zig\",",
        "\"tools/lib/str_error_r.zig\",",
        "\"tools/lib/string.zig\",",
        "\"tools/lib/vsprintf.zig\",",
        "\"tools/lib/zalloc.zig\",",
    });
    try requireContains("PHASE1_PARITY_HELPER_COUNT={len(EXPECTED_HELPERS)}");
}

test "phase1 parity checker preserves parked shared helpers and direct anchors" {
    try requireContains("EXPECTED_SHARED_REPLAY_PARKED_HELPERS = (");
    try requireOrdered(&.{
        "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = (",
        "\"tools/lib/argv_split.zig\",",
        "\"tools/lib/cmdline.zig\",",
        "\"tools/lib/ctype.zig\",",
        "\"tools/lib/hweight.zig\",",
        "\"tools/lib/list_sort.zig\",",
        "\"tools/lib/slab.zig\",",
        "\"tools/lib/str_error_r.zig\",",
        "\"tools/lib/vsprintf.zig\",",
        "\"tools/lib/zalloc.zig\",",
    });

    try requireContains("EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = (");
    try requireOrdered(&.{
        "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = (",
        "\"tools/lib/bitmap.zig\",",
        "\"tools/lib/find_bit.zig\",",
        "\"tools/lib/rbtree.zig\",",
        "\"tools/lib/string.zig\",",
    });

    try requireContains("EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS = (");
    try requireOrdered(&.{
        "EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS = (",
        "\"tools/lib/bitmap.zig\",",
        "\"tools/lib/find_bit.zig\",",
        "\"tools/lib/rbtree.zig\",",
        "\"tools/lib/string.zig\",",
    });
    try requireContains("PHASE1_PARITY_DIRECT_REVIEW_HELPER_COUNT={len(EXPECTED_DIRECT_REVIEW_ANCHOR_HELPERS)}");
}

test "phase1 parity checker keeps blocker ids tied to the parked replay packet" {
    try requireContains("EXPECTED_REPLAY_BLOCKER_IDS = (");
    try requireOrdered(&.{
        "\"phase1_helpers_zig_slab_zero_after_kmalloc\",",
        "\"phase1_helpers_c_harness_missing_c_sources\",",
    });
    try requireContains("PHASE1_PARITY_BLOCKER_COUNT={len(EXPECTED_REPLAY_BLOCKER_IDS)}");
    try requireContains("PHASE1_PARITY_BLOCKER_IDS=\" + \",\".join(EXPECTED_REPLAY_BLOCKER_IDS)");
}
