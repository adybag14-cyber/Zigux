const std = @import("std");

const smoke_source = @embedFile("phase1_host_tools_smoke.zig");

fn contains(needle: []const u8) bool {
    return std.mem.indexOf(u8, smoke_source, needle) != null;
}

fn count(needle: []const u8) usize {
    var found: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOf(u8, smoke_source[index..], needle)) |relative| {
        found += 1;
        index += relative + needle.len;
    }
    return found;
}

fn before(lhs: []const u8, rhs: []const u8) !void {
    const lhs_index = std.mem.indexOf(u8, smoke_source, lhs) orelse return error.MissingLeftMarker;
    const rhs_index = std.mem.indexOf(u8, smoke_source, rhs) orelse return error.MissingRightMarker;
    try std.testing.expect(lhs_index < rhs_index);
}

test "phase1 host-tools smoke keeps the behavior-test roster closed" {
    try std.testing.expectEqual(@as(usize, 4), count("test \"phase1 host-tools smoke "));
    try std.testing.expect(contains("test \"phase1 host-tools smoke imports the live helper modules\""));
    try std.testing.expect(contains("test \"phase1 host-tools smoke exercises live helper behavior\""));
    try std.testing.expect(contains("test \"phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned\""));
    try std.testing.expect(contains("test \"phase1 host-tools smoke keeps bitmap alias zero-size and empty-format edges aligned\""));
}

test "phase1 host-tools smoke still exercises the main helper families" {
    const required_behavior_markers = [_][]const u8{
        "argv_split.argv_split(std.testing.allocator, \"  zigux   host\\ttools  \")",
        "cmdline.memparse(\"64K tail\")",
        "cmdline.memparse(\"-2K tail\")",
        "cmdline.nextArg(\"console=ttyS0,115200 root=\\\"/dev/sda1 quiet\\\" panic=-1\")",
        "ctype.isxdigit('f')",
        "hweight.swHweight64(0xf0f0_f0f0_f0f0_f0f0)",
        "slab.kmallocBytes(8, slab.GFP_KERNEL | slab.__GFP_ZERO)",
        "str_error_r.strErrorR(4096, &unknown_error_buffer)",
        "vsprintf.scnprintfPad(&padded_render, 10, \"id={d}\", .{7})",
        "zalloc.zallocValue(allocator, ZeroValue)",
        "list_sort.listSort(null, &list_head, list_cmp)",
        "list_sort.listSort(null, &bool_head, bool_cmp)",
        "bitmap.setRange(&map, word_bits - 1, 3)",
        "bitmap.scnprintf(&map, nbits, &rendered)",
        "string.strscpyPad(&padded, \"hi\")",
        "string.strlcat(appended[0..], \"all\")",
        "string.match_string(&lookup, &lookup_cstr)",
        "string.strnchrNul(&counted, counted.len, 'z')",
        "rbtree.matchIterator(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp)",
        "rbtree.eraseInitCached(&cached_replacement.node, &cached_root)",
    };

    inline for (required_behavior_markers) |marker| {
        try std.testing.expect(contains(marker));
    }
}

test "phase1 host-tools smoke keeps tail and alias edge coverage after broad behavior coverage" {
    try before(
        "test \"phase1 host-tools smoke exercises live helper behavior\"",
        "test \"phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned\"",
    );
    try before(
        "test \"phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned\"",
        "test \"phase1 host-tools smoke keeps bitmap alias zero-size and empty-format edges aligned\"",
    );

    const tail_and_alias_markers = [_][]const u8{
        "find_bit.findFirstAndNotBit(&tail_lhs, &tail_rhs, nbits)",
        "find_bit.find_next_andnot_bit(&tail_lhs, &tail_rhs, nbits, find_bit.bits_per_long + 2)",
        "find_bit._find_next_andnot_bit(&tail_lhs, &tail_rhs, nbits, find_bit.bits_per_long + 4)",
        "find_bit.findFirstClump8(&clump, &clump_map, nbits)",
        "find_bit.find_first_clump8(&clump, &clump_map, nbits)",
        "find_bit.find_next_clump8(&clump, &clump_map, nbits, find_bit.bits_per_long)",
        "find_bit._find_next_clump8(&clump, &clump_map, nbits, nbits)",
        "bitmap.copy(direct_copy[0..0], src[0..0], 0)",
        "bitmap.bitmap_copy(alias_copy[0..0], src[0..0], 0)",
        "bitmap.copyClearTail(direct_clear[0..0], src[0..0], 0)",
        "bitmap.bitmap_copy_clear_tail(alias_clear[0..0], src[0..0], 0)",
        "bitmap.copyAndExtend(direct_extend[0..0], src[0..0], 0, 0)",
        "bitmap.bitmap_copy_and_extend(alias_extend[0..0], src[0..0], 0, 0)",
        "bitmap.bitmap_scnprintf(&empty_map, 8, &alias_buffer)",
    };

    inline for (tail_and_alias_markers) |marker| {
        try std.testing.expect(contains(marker));
    }
}
