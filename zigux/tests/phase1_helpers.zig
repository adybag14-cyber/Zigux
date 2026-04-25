const std = @import("std");
const argv_split = @import("argv_split");
const bitmap = @import("bitmap");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const find_bit = @import("find_bit");
const hweight = @import("hweight");
const list_sort = @import("list_sort");
const rbtree = @import("rbtree");
const slab = @import("slab");
const str_error_r = @import("str_error_r");
const string = @import("string");
const vsprintf = @import("vsprintf");
const zalloc = @import("zalloc");

const CmdlineValueFixture = struct {
    value: u64,
    rest: []const u8,
};

const Fixture = struct {
    find_bit: struct {
        bits_per_long: usize,
        first: usize,
        next_after_6: usize,
        next_after_word: usize,
        first_zero: usize,
        next_zero: usize,
        first_and: usize,
        next_and: usize,
        tail_clamped_first: usize,
        tail_clamped_next: usize,
        tail_zero_clamped_first: usize,
        tail_zero_clamped_next: usize,
        tail_and_clamped_first: usize,
        tail_and_clamped_next: usize,
    },
    bitmap: struct {
        weight: usize,
        scnprintf: []const u8,
        and_result: bool,
        and_values: []const u64,
        andnot_result: bool,
        andnot_values: []const u64,
        or_values: []const u64,
        xor_values: []const u64,
        equal: bool,
        intersects: bool,
        subset: bool,
        range_after_set: []const u64,
        range_after_clear: []const u64,
        full_after_fill: bool,
        empty_after_zero: bool,
    },
    string: struct {
        strtobool_y: bool,
        strtobool_on: bool,
        strtobool_zero: bool,
        strtobool_off: bool,
        strtobool_invalid: i32,
        strlcpy_len: usize,
        strlcpy_buffer: []const u8,
        skip_spaces: []const u8,
        trim_spaces: []const u8,
        remove_spaces: []const u8,
        replace_char: []const u8,
        memchr_inv_index: usize,
        memchr_inv_none: bool,
    },
    rbtree: struct {
        insert_order: []const i32,
        replace_order: []const i32,
        postorder_count: usize,
        cleared_node_empty: bool,
    },
    argv_split: struct {
        argc: usize,
        argv: []const []const u8,
        blank_argc: usize,
    },
    cmdline: struct {
        decimal_k: CmdlineValueFixture,
        hex_m: CmdlineValueFixture,
        octal_k: CmdlineValueFixture,
        invalid: CmdlineValueFixture,
    },
    ctype: struct {
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
    },
    hweight: struct {
        w8: u32,
        w16: u32,
        w32: u32,
        w64: u64,
        wlong: usize,
    },
    list_sort: struct {
        tri_sorted_keys: []const i32,
        tri_sorted_ordinals: []const usize,
        bool_sorted_keys: []const i32,
        bool_sorted_ordinals: []const usize,
    },
    zalloc: struct {
        zeroed: bool,
        freed_is_null: bool,
        value_zeroed: bool,
        value_freed_is_null: bool,
    },
    str_error_r: struct {
        enoent: []const u8,
        unknown: []const u8,
    },
    slab: struct {
        null_without_reclaim: bool,
        alloc_count_after_kmalloc: isize,
        zero_after_kmalloc: bool,
        alloc_count_after_kmalloc_free: isize,
        array_zeroed: bool,
        alloc_count_after_kmalloc_array: isize,
        alloc_count_after_kmalloc_array_free: isize,
        slab_is_available: bool,
    },
    vsprintf: struct {
        scnprintf_text: []const u8,
        scnprintf_len: usize,
        pad_text: []const u8,
        pad_len: usize,
    },
};

fn loadFixture(allocator: std.mem.Allocator) !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, allocator, @embedFile("fixtures/phase1_helpers.json"), .{});
}

fn expectWordSlice(actual: []const bitmap.Word, expected: []const u64) !void {
    try std.testing.expectEqual(expected.len, actual.len);
    for (actual, expected) |value, expected_value| {
        try std.testing.expectEqual(@as(bitmap.Word, @intCast(expected_value)), value);
    }
}

test "phase 1 helper modules import cleanly" {
    _ = argv_split;
    _ = bitmap;
    _ = cmdline;
    _ = ctype;
    _ = find_bit;
    _ = hweight;
    _ = list_sort;
    _ = rbtree;
    _ = slab;
    _ = str_error_r;
    _ = string;
    _ = vsprintf;
    _ = zalloc;
}

test "phase 1 helper ports match committed parity fixture" {
    var parsed = try loadFixture(std.testing.allocator);
    defer parsed.deinit();
    const fixture = parsed.value;

    try std.testing.expectEqual(@as(usize, @bitSizeOf(find_bit.Word)), fixture.find_bit.bits_per_long);

    var find_map = [_]find_bit.Word{ 0, 0, 0 };
    find_map[0] |= @as(find_bit.Word, 1) << 5;
    find_map[1] |= @as(find_bit.Word, 1) << 3;
    find_map[2] |= @as(find_bit.Word, 1) << 7;
    try std.testing.expectEqual(fixture.find_bit.first, find_bit.findFirstBit(&find_map, fixture.find_bit.bits_per_long * 3));
    try std.testing.expectEqual(fixture.find_bit.next_after_6, find_bit.findNextBit(&find_map, fixture.find_bit.bits_per_long * 3, 6));
    try std.testing.expectEqual(fixture.find_bit.next_after_word, find_bit.findNextBit(&find_map, fixture.find_bit.bits_per_long * 3, fixture.find_bit.bits_per_long + 4));
    try std.testing.expectEqual(fixture.find_bit.first_zero, find_bit.findFirstZeroBit(&[_]find_bit.Word{0xf7}, 12));
    try std.testing.expectEqual(fixture.find_bit.next_zero, find_bit.findNextZeroBit(&[_]find_bit.Word{ ~@as(find_bit.Word, 0), ~(@as(find_bit.Word, 1) << 4) }, fixture.find_bit.bits_per_long * 2, fixture.find_bit.bits_per_long));

    const find_lhs = [_]find_bit.Word{ (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 9), @as(find_bit.Word, 1) << 2 };
    const find_rhs = [_]find_bit.Word{ @as(find_bit.Word, 1) << 9, @as(find_bit.Word, 1) << 2 };
    try std.testing.expectEqual(fixture.find_bit.first_and, find_bit.findFirstAndBit(&find_lhs, &find_rhs, fixture.find_bit.bits_per_long * 2));
    try std.testing.expectEqual(fixture.find_bit.next_and, find_bit.findNextAndBit(&find_lhs, &find_rhs, fixture.find_bit.bits_per_long * 2, 10));

    const find_tail_nbits = fixture.find_bit.bits_per_long + 5;
    const find_tail = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 9 };
    const find_tail_full = [_]find_bit.Word{ ~@as(find_bit.Word, 0), find_bit.lastWordMask(find_tail_nbits) };
    try std.testing.expectEqual(fixture.find_bit.tail_clamped_first, find_bit.findFirstBit(&find_tail, find_tail_nbits));
    try std.testing.expectEqual(fixture.find_bit.tail_clamped_next, find_bit.findNextBit(&find_tail, find_tail_nbits, fixture.find_bit.bits_per_long));
    try std.testing.expectEqual(fixture.find_bit.tail_zero_clamped_first, find_bit.findFirstZeroBit(&find_tail_full, find_tail_nbits));
    try std.testing.expectEqual(fixture.find_bit.tail_zero_clamped_next, find_bit.findNextZeroBit(&find_tail_full, find_tail_nbits, fixture.find_bit.bits_per_long));
    try std.testing.expectEqual(fixture.find_bit.tail_and_clamped_first, find_bit.findFirstAndBit(&find_tail, &find_tail, find_tail_nbits));
    try std.testing.expectEqual(fixture.find_bit.tail_and_clamped_next, find_bit.findNextAndBit(&find_tail, &find_tail, find_tail_nbits, fixture.find_bit.bits_per_long));

    const bitmap_lhs = [_]bitmap.Word{ 0x0e, 0 };
    const bitmap_rhs = [_]bitmap.Word{ 0x0a, 0 };
    var bitmap_dst = [_]bitmap.Word{ 0, 0 };
    try std.testing.expectEqual(fixture.bitmap.weight, bitmap.weight(&bitmap_lhs, 8));
    try std.testing.expectEqual(fixture.bitmap.and_result, bitmap.andBits(&bitmap_dst, &bitmap_lhs, &bitmap_rhs, 8));
    try expectWordSlice(&bitmap_dst, fixture.bitmap.and_values);
    try std.testing.expectEqual(fixture.bitmap.andnot_result, bitmap.andNotBits(&bitmap_dst, &bitmap_lhs, &bitmap_rhs, 8));
    try expectWordSlice(&bitmap_dst, fixture.bitmap.andnot_values);
    bitmap.orBits(&bitmap_dst, &bitmap_lhs, &bitmap_rhs, 8);
    try expectWordSlice(&bitmap_dst, fixture.bitmap.or_values);
    bitmap.xorBits(&bitmap_dst, &bitmap_lhs, &bitmap_rhs, 8);
    try expectWordSlice(&bitmap_dst, fixture.bitmap.xor_values);
    try std.testing.expectEqual(fixture.bitmap.equal, bitmap.equal(&bitmap_lhs, &[_]bitmap.Word{ 0x0e, 0 }, 8));
    try std.testing.expectEqual(fixture.bitmap.intersects, bitmap.intersects(&bitmap_lhs, &bitmap_rhs, 8));
    try std.testing.expectEqual(fixture.bitmap.subset, bitmap.subset(&bitmap_rhs, &bitmap_lhs, 8));

    var bitmap_range = [_]bitmap.Word{ 0, 0, 0 };
    bitmap.setRange(&bitmap_range, 1, 3);
    bitmap.setRange(&bitmap_range, bitmap.bits_per_long + 2, 2);
    try expectWordSlice(&bitmap_range, fixture.bitmap.range_after_set);
    bitmap.clearRange(&bitmap_range, 1, 3);
    bitmap.clearRange(&bitmap_range, bitmap.bits_per_long + 2, 2);
    try expectWordSlice(&bitmap_range, fixture.bitmap.range_after_clear);

    bitmap.fill(&bitmap_dst, find_bit.bits_per_long * 2);
    try std.testing.expectEqual(fixture.bitmap.full_after_fill, bitmap.full(&bitmap_dst, find_bit.bits_per_long * 2));
    bitmap.zero(&bitmap_dst, find_bit.bits_per_long * 2);
    try std.testing.expectEqual(fixture.bitmap.empty_after_zero, bitmap.empty(&bitmap_dst, find_bit.bits_per_long * 2));

    var bitmap_render = [_]bitmap.Word{ 0, 0 };
    bitmap.setRange(&bitmap_render, 1, 3);
    bitmap.setRange(&bitmap_render, 7, 1);
    bitmap.setRange(&bitmap_render, 10, 2);
    var bitmap_buffer: [64]u8 = undefined;
    const bitmap_len = bitmap.scnprintf(&bitmap_render, 32, &bitmap_buffer);
    try std.testing.expectEqualStrings(fixture.bitmap.scnprintf, bitmap_buffer[0..bitmap_len]);

    try std.testing.expectEqual(fixture.string.strtobool_y, try string.strtobool("y"));
    try std.testing.expectEqual(fixture.string.strtobool_on, try string.strtobool("On"));
    try std.testing.expectEqual(fixture.string.strtobool_zero, try string.strtobool("0"));
    try std.testing.expectEqual(fixture.string.strtobool_off, try string.strtobool("of"));
    try std.testing.expectError(error.Invalid, string.strtobool("maybe"));

    var strlcpy_buffer = [_]u8{ 0, 0, 0, 0 };
    try std.testing.expectEqual(fixture.string.strlcpy_len, string.strlcpy(&strlcpy_buffer, "hello"));
    try std.testing.expectEqualStrings(fixture.string.strlcpy_buffer, strlcpy_buffer[0..fixture.string.strlcpy_buffer.len]);
    try std.testing.expectEqualStrings(fixture.string.skip_spaces, string.skipSpaces("   hello"));

    var trim_buffer = [_]u8{ ' ', '\t', 'h', 'i', ' ', '\n', 0 };
    try std.testing.expectEqualStrings(fixture.string.trim_spaces, string.trimSpaces(trim_buffer[0 .. trim_buffer.len - 1]));
    var remove_buffer = [_]u8{ 'a', ' ', 'b', ' ', 'c', 0 };
    try std.testing.expectEqualStrings(fixture.string.remove_spaces, string.removeSpaces(remove_buffer[0 .. remove_buffer.len - 1]));
    var replace_buffer = [_]u8{ 'a', '-', 'b', 0 };
    _ = string.replaceChar(replace_buffer[0 .. replace_buffer.len - 1], '-', '_');
    try std.testing.expectEqualStrings(fixture.string.replace_char, replace_buffer[0..fixture.string.replace_char.len]);
    try std.testing.expectEqual(@as(?usize, fixture.string.memchr_inv_index), string.memchrInv("aaaaXaaa", 'a'));
    try std.testing.expectEqual(@as(?usize, null), string.memchrInv("bbbb", 'b'));
    try std.testing.expect(fixture.string.memchr_inv_none);
