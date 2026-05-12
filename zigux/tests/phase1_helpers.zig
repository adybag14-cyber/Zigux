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
        last: usize,
        inclusive_boundary_next: usize,
        inclusive_boundary_zero: usize,
        inclusive_boundary_and: usize,
        past_nbits_next: usize,
        past_nbits_zero: usize,
        past_nbits_and: usize,
        tail_clamped_first: usize,
        tail_clamped_next: usize,
        tail_zero_clamped_first: usize,
        tail_zero_clamped_next: usize,
        tail_and_clamped_first: usize,
        tail_and_clamped_next: usize,
        tail_clamped_last: usize,
        tail_clamped_empty_last: usize,
    },
    bitmap: struct {
        weight: usize,
        scnprintf: []const u8,
        truncated_scnprintf_len: usize,
        truncated_scnprintf: []const u8,
        terminator_only_scnprintf_len: usize,
        terminator_only_nul: u8,
        zero_length_scnprintf_len: usize,
        alloc_words: usize,
        zalloc_words: usize,
        zalloc_values: []const u64,
        and_result: bool,
        and_values: []const u64,
        andnot_result: bool,
        andnot_values: []const u64,
        or_values: []const u64,
        xor_values: []const u64,
        partial_xor_nbits: usize,
        partial_xor_masked_values: []const u64,
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
        replace_char_end: usize,
        replace_char_cstr_end: usize,
        replace_char_cstr_bytes: []const u8,
        memchr_inv_index: usize,
        memchr_inv_none: bool,
    },
    rbtree: struct {
        empty_root: bool,
        insert_order: []const i32,
        reverse_order: []const i32,
        replace_order: []const i32,
        erase_init_order: []const i32,
        postorder_count: usize,
        erase_init_node_empty: bool,
        cleared_node_empty: bool,
        find_found_key: i32,
        find_missing: bool,
        find_first_serial: usize,
        next_match_serials: []const usize,
        next_match_terminal_null: bool,
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
    return std.json.parseFromSlice(Fixture, allocator, @embedFile("fixtures/phase1_helpers.json"), .{
        .ignore_unknown_fields = true,
    });
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
    try std.testing.expectEqual(fixture.find_bit.last, find_bit.findLastBit(&find_map, fixture.find_bit.bits_per_long * 3));

    const inclusive_boundary = fixture.find_bit.bits_per_long - 1;
    const inclusive_set_map = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << @intCast(inclusive_boundary)),
        0,
    };
    const inclusive_zero_map = [_]find_bit.Word{
        ~(@as(find_bit.Word, 1) << @intCast(inclusive_boundary)),
        ~@as(find_bit.Word, 0),
    };
    try std.testing.expectEqual(
        fixture.find_bit.inclusive_boundary_next,
        find_bit.findNextBit(&inclusive_set_map, fixture.find_bit.bits_per_long * 2, inclusive_boundary),
    );
    try std.testing.expectEqual(
        fixture.find_bit.inclusive_boundary_zero,
        find_bit.findNextZeroBit(&inclusive_zero_map, fixture.find_bit.bits_per_long * 2, inclusive_boundary),
    );
    try std.testing.expectEqual(
        fixture.find_bit.inclusive_boundary_and,
        find_bit.findNextAndBit(&inclusive_set_map, &inclusive_set_map, fixture.find_bit.bits_per_long * 2, inclusive_boundary),
    );

    const past_nbits_boundary = fixture.find_bit.past_nbits_next;
    const past_nbits_empty = [_]find_bit.Word{};
    try std.testing.expectEqual(
        fixture.find_bit.past_nbits_next,
        find_bit.findNextBit(&past_nbits_empty, past_nbits_boundary, past_nbits_boundary),
    );
    try std.testing.expectEqual(
        fixture.find_bit.past_nbits_next,
        find_bit.findNextBit(&past_nbits_empty, past_nbits_boundary, past_nbits_boundary + 4),
    );
    try std.testing.expectEqual(
        fixture.find_bit.past_nbits_zero,
        find_bit.findNextZeroBit(
            &past_nbits_empty,
            fixture.find_bit.past_nbits_zero,
            fixture.find_bit.past_nbits_zero,
        ),
    );
    try std.testing.expectEqual(
        fixture.find_bit.past_nbits_zero,
        find_bit.findNextZeroBit(
            &past_nbits_empty,
            fixture.find_bit.past_nbits_zero,
            fixture.find_bit.past_nbits_zero + 4,
        ),
    );
    try std.testing.expectEqual(
        fixture.find_bit.past_nbits_and,
        find_bit.findNextAndBit(
            &past_nbits_empty,
            &past_nbits_empty,
            fixture.find_bit.past_nbits_and,
            fixture.find_bit.past_nbits_and,
        ),
    );
    try std.testing.expectEqual(
        fixture.find_bit.past_nbits_and,
        find_bit.findNextAndBit(
            &past_nbits_empty,
            &past_nbits_empty,
            fixture.find_bit.past_nbits_and,
            fixture.find_bit.past_nbits_and + 4,
        ),
    );

    const find_tail_nbits = fixture.find_bit.bits_per_long + 5;
    const find_tail = [_]find_bit.Word{ 0, @as(find_bit.Word, 1) << 9 };
    const find_tail_full = [_]find_bit.Word{ ~@as(find_bit.Word, 0), find_bit.lastWordMask(find_tail_nbits) };
    try std.testing.expectEqual(fixture.find_bit.tail_clamped_first, find_bit.findFirstBit(&find_tail, find_tail_nbits));
    try std.testing.expectEqual(fixture.find_bit.tail_clamped_next, find_bit.findNextBit(&find_tail, find_tail_nbits, fixture.find_bit.bits_per_long));
    try std.testing.expectEqual(fixture.find_bit.tail_zero_clamped_first, find_bit.findFirstZeroBit(&find_tail_full, find_tail_nbits));
    try std.testing.expectEqual(fixture.find_bit.tail_zero_clamped_next, find_bit.findNextZeroBit(&find_tail_full, find_tail_nbits, fixture.find_bit.bits_per_long));
    try std.testing.expectEqual(fixture.find_bit.tail_and_clamped_first, find_bit.findFirstAndBit(&find_tail, &find_tail, find_tail_nbits));
    try std.testing.expectEqual(fixture.find_bit.tail_and_clamped_next, find_bit.findNextAndBit(&find_tail, &find_tail, find_tail_nbits, fixture.find_bit.bits_per_long));

    var find_tail_window = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9) };
    try std.testing.expectEqual(fixture.find_bit.bits_per_long + 3, find_bit.findFirstBit(&find_tail_window, find_tail_nbits));
    try std.testing.expectEqual(find_tail_nbits, find_bit.findNextBit(&find_tail_window, find_tail_nbits, fixture.find_bit.bits_per_long + 4));
    try std.testing.expectEqual(fixture.find_bit.tail_clamped_last, find_bit.findLastBit(&find_tail_window, find_tail_nbits));
    find_tail_window[1] &= ~(@as(find_bit.Word, 1) << 3);
    try std.testing.expectEqual(find_tail_nbits, find_bit.findFirstBit(&find_tail_window, find_tail_nbits));
    try std.testing.expectEqual(fixture.find_bit.tail_clamped_empty_last, find_bit.findLastBit(&find_tail_window, find_tail_nbits));

    var find_tail_zero_window = find_tail_full;
    find_tail_zero_window[1] &= ~(@as(find_bit.Word, 1) << 2);
    try std.testing.expectEqual(fixture.find_bit.bits_per_long + 2, find_bit.findFirstZeroBit(&find_tail_zero_window, find_tail_nbits));
    try std.testing.expectEqual(fixture.find_bit.bits_per_long + 2, find_bit.findNextZeroBit(&find_tail_zero_window, find_tail_nbits, fixture.find_bit.bits_per_long));

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
    const partial_bitmap_lhs = [_]bitmap.Word{0x1f};
    const partial_bitmap_rhs = [_]bitmap.Word{0x11};
    var partial_bitmap_dst = [_]bitmap.Word{0};
    bitmap.xorBits(&partial_bitmap_dst, &partial_bitmap_lhs, &partial_bitmap_rhs, fixture.bitmap.partial_xor_nbits);
    try expectWordSlice(
        &[_]bitmap.Word{partial_bitmap_dst[0] & bitmap.lastWordMask(fixture.bitmap.partial_xor_nbits)},
        fixture.bitmap.partial_xor_masked_values,
    );
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

    var bitmap_truncated_render = [_]bitmap.Word{0};
    bitmap.setRange(&bitmap_truncated_render, 1, 3);
    bitmap.setRange(&bitmap_truncated_render, 7, 1);
    bitmap.setRange(&bitmap_truncated_render, 10, 3);

    var truncated_buffer = [_]u8{0} ** 8;
    const truncated_len = bitmap.scnprintf(&bitmap_truncated_render, 32, &truncated_buffer);
    try std.testing.expectEqual(fixture.bitmap.truncated_scnprintf_len, truncated_len);
    try std.testing.expectEqualStrings(
        fixture.bitmap.truncated_scnprintf,
        truncated_buffer[0 .. truncated_buffer.len - 1],
    );

    var single_bit_bitmap = [_]bitmap.Word{0};
    bitmap.setRange(&single_bit_bitmap, 9, 1);

    var terminator_only = [_]u8{0xaa};
    const terminator_only_len = bitmap.scnprintf(&single_bit_bitmap, 32, &terminator_only);
    try std.testing.expectEqual(fixture.bitmap.terminator_only_scnprintf_len, terminator_only_len);
    try std.testing.expectEqual(fixture.bitmap.terminator_only_nul, terminator_only[0]);

    var zero_length = [_]u8{};
    const zero_length_len = bitmap.scnprintf(&single_bit_bitmap, 32, &zero_length);
    try std.testing.expectEqual(fixture.bitmap.zero_length_scnprintf_len, zero_length_len);

    const bitmap_allocator = std.testing.allocator;
    var bitmap_allocated = try bitmap.alloc(bitmap_allocator, bitmap.bits_per_long + 5);
    defer bitmap.free(bitmap_allocator, &bitmap_allocated);
    try std.testing.expect(bitmap_allocated != null);
    try std.testing.expectEqual(fixture.bitmap.alloc_words, bitmap_allocated.?.len);

    var bitmap_zero_allocated = try bitmap.zalloc(bitmap_allocator, bitmap.bits_per_long + 5);
    defer bitmap.free(bitmap_allocator, &bitmap_zero_allocated);
    try std.testing.expect(bitmap_zero_allocated != null);
    try std.testing.expectEqual(fixture.bitmap.zalloc_words, bitmap_zero_allocated.?.len);
    try expectWordSlice(bitmap_zero_allocated.?, fixture.bitmap.zalloc_values);

    try std.testing.expectEqual(fixture.string.strtobool_y, try string.strtobool("y"));
    try std.testing.expectEqual(fixture.string.strtobool_on, try string.strtobool("On"));
    try std.testing.expectEqual(fixture.string.strtobool_zero, try string.strtobool("0"));
    try std.testing.expectEqual(fixture.string.strtobool_off, try string.strtobool("of"));
    try std.testing.expectError(error.Invalid, string.strtobool("maybe"));
    const strtobool_invalid = blk: {
        _ = string.strtobool("maybe") catch |err| break :blk @as(i32, @intCast(@intFromError(err)));
        break :blk @as(i32, 0);
    };
    try std.testing.expectEqual(fixture.string.strtobool_invalid, strtobool_invalid);

    var strlcpy_buffer = [_]u8{ 0, 0, 0, 0 };
    try std.testing.expectEqual(fixture.string.strlcpy_len, string.strlcpy(&strlcpy_buffer, "hello"));
    try std.testing.expectEqualStrings(fixture.string.strlcpy_buffer, strlcpy_buffer[0..fixture.string.strlcpy_buffer.len]);
    try std.testing.expectEqualStrings(fixture.string.skip_spaces, string.skipSpaces("   hello"));

    var trim_buffer = [_]u8{ ' ', '\t', 'h', 'i', ' ', '\n', 0 };
    try std.testing.expectEqualStrings(fixture.string.trim_spaces, string.trimSpaces(trim_buffer[0 .. trim_buffer.len - 1]));
    var remove_buffer = [_]u8{ 'a', ' ', 'b', ' ', 'c', 0 };
    try std.testing.expectEqualStrings(fixture.string.remove_spaces, string.removeSpaces(remove_buffer[0 .. remove_buffer.len - 1]));
    var replace_buffer = [_]u8{ 'a', '-', 'b', 0 };
    try std.testing.expectEqual(
        fixture.string.replace_char_end,
        string.replaceChar(replace_buffer[0 .. replace_buffer.len - 1], '-', '_'),
    );
    try std.testing.expectEqualStrings(fixture.string.replace_char, replace_buffer[0..fixture.string.replace_char.len]);
    var replace_cstr_buffer = [_]u8{ 'a', '-', 0, '-', 'z' };
    try std.testing.expectEqual(
        fixture.string.replace_char_cstr_end,
        string.replaceChar(&replace_cstr_buffer, '-', '_'),
    );
    try std.testing.expectEqualSlices(
        u8,
        fixture.string.replace_char_cstr_bytes,
        &replace_cstr_buffer,
    );
    try std.testing.expectEqual(@as(?usize, fixture.string.memchr_inv_index), string.memchrInv("aaaaXaaa", 'a'));
    try std.testing.expectEqual(
        fixture.string.memchr_inv_none,
        string.memchrInv("bbbb", 'b') == null,
    );

    const allocator = std.testing.allocator;
    const split_argv = try argv_split.argvSplit(allocator, " alpha  beta\tgamma\n");
    defer argv_split.argvFree(allocator, split_argv);
    try std.testing.expectEqual(fixture.argv_split.argc, split_argv.len);
    try std.testing.expectEqual(fixture.argv_split.blank_argc, argv_split.countArgc("   \t\n"));
    for (split_argv, fixture.argv_split.argv) |actual, expected| {
        try std.testing.expectEqualStrings(expected, actual);
    }

    const decimal = cmdline.memparse("64K rest");
    try std.testing.expectEqual(fixture.cmdline.decimal_k.value, decimal.value);
    try std.testing.expectEqualStrings(fixture.cmdline.decimal_k.rest, decimal.rest);
    const hexadecimal = cmdline.memparse("0x20M");
    try std.testing.expectEqual(fixture.cmdline.hex_m.value, hexadecimal.value);
    try std.testing.expectEqualStrings(fixture.cmdline.hex_m.rest, hexadecimal.rest);
    const octal = cmdline.memparse("010K");
    try std.testing.expectEqual(fixture.cmdline.octal_k.value, octal.value);
    try std.testing.expectEqualStrings(fixture.cmdline.octal_k.rest, octal.rest);
    const invalid = cmdline.memparse("xyz");
    try std.testing.expectEqual(fixture.cmdline.invalid.value, invalid.value);
    try std.testing.expectEqualStrings(fixture.cmdline.invalid.rest, invalid.rest);

    try std.testing.expectEqual(fixture.ctype.mask_A, ctype.mask('A'));
    try std.testing.expectEqual(fixture.ctype.mask_a, ctype.mask('a'));
    try std.testing.expectEqual(fixture.ctype.mask_space, ctype.mask(' '));
    try std.testing.expectEqual(fixture.ctype.isalnum_A, ctype.isalnum('A'));
    try std.testing.expectEqual(fixture.ctype.isalpha_z, ctype.isalpha('z'));
    try std.testing.expectEqual(fixture.ctype.isdigit_7, ctype.isdigit('7'));
    try std.testing.expectEqual(fixture.ctype.isspace_tab, ctype.isspace('\t'));
    try std.testing.expectEqual(fixture.ctype.isxdigit_f, ctype.isxdigit('f'));
    try std.testing.expectEqual(fixture.ctype.ispunct_bang, ctype.ispunct('!'));
    try std.testing.expectEqual(fixture.ctype.tolower_A, ctype.tolower('A'));
    try std.testing.expectEqual(fixture.ctype.toupper_z, ctype.toupper('z'));
    try std.testing.expectEqual(fixture.ctype.isodigit_7, ctype.isodigit('7'));
    try std.testing.expectEqual(fixture.ctype.isodigit_8, ctype.isodigit('8'));

    try std.testing.expectEqual(fixture.hweight.w8, hweight.swHweight8(0xf0));
    try std.testing.expectEqual(fixture.hweight.w16, hweight.swHweight16(0xf0f0));
    try std.testing.expectEqual(fixture.hweight.w32, hweight.swHweight32(0xf0f0_f0f0));
    try std.testing.expectEqual(fixture.hweight.w64, hweight.swHweight64(0xf0f0_f0f0_f0f0_f0f0));
    try std.testing.expectEqual(fixture.hweight.wlong, hweight.hweightLong(0xf0f0));

    const ListEntry = struct {
        key: i32,
        ordinal: usize,
        node: list_sort.ListHead = .{},
    };

    const tri_cmp = struct {
        fn compare(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const ListEntry = @fieldParentPtr("node", a);
            const rhs: *const ListEntry = @fieldParentPtr("node", b);
            if (lhs.key < rhs.key) return -1;
            if (lhs.key > rhs.key) return 1;
            return 0;
        }
    }.compare;

    const bool_cmp = struct {
        fn compare(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const ListEntry = @fieldParentPtr("node", a);
            const rhs: *const ListEntry = @fieldParentPtr("node", b);
            return @intFromBool(lhs.key > rhs.key);
        }
    }.compare;

    var tri_head: list_sort.ListHead = .{};
    tri_head.init();
    var tri_entries = [_]ListEntry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
    };
    for (&tri_entries) |*entry| list_sort.listAddTail(&entry.node, &tri_head);
    list_sort.listSort(null, &tri_head, tri_cmp);

    var tri_sorted_keys: [5]i32 = undefined;
    var tri_sorted_ordinals: [5]usize = undefined;
    var tri_index: usize = 0;
    var tri_current = tri_head.next;
    while (tri_current != &tri_head) : (tri_current = tri_current.?.next) {
        const entry: *const ListEntry = @fieldParentPtr("node", tri_current.?);
        tri_sorted_keys[tri_index] = entry.key;
        tri_sorted_ordinals[tri_index] = entry.ordinal;
        tri_index += 1;
    }
    try std.testing.expectEqualSlices(i32, fixture.list_sort.tri_sorted_keys, tri_sorted_keys[0..tri_index]);
    try std.testing.expectEqualSlices(usize, fixture.list_sort.tri_sorted_ordinals, tri_sorted_ordinals[0..tri_index]);

    var bool_head: list_sort.ListHead = .{};
    bool_head.init();
    var bool_entries = [_]ListEntry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
    };
    for (&bool_entries) |*entry| list_sort.listAddTail(&entry.node, &bool_head);
    list_sort.listSort(null, &bool_head, bool_cmp);

    var bool_sorted_keys: [5]i32 = undefined;
    var bool_sorted_ordinals: [5]usize = undefined;
    var bool_index: usize = 0;
    var bool_current = bool_head.next;
    while (bool_current != &bool_head) : (bool_current = bool_current.?.next) {
        const entry: *const ListEntry = @fieldParentPtr("node", bool_current.?);
        bool_sorted_keys[bool_index] = entry.key;
        bool_sorted_ordinals[bool_index] = entry.ordinal;
        bool_index += 1;
    }
    try std.testing.expectEqualSlices(i32, fixture.list_sort.bool_sorted_keys, bool_sorted_keys[0..bool_index]);
    try std.testing.expectEqualSlices(usize, fixture.list_sort.bool_sorted_ordinals, bool_sorted_ordinals[0..bool_index]);

    var zalloc_bytes: ?[]u8 = try zalloc.zallocBytes(allocator, 8);
    defer zalloc.zfreeBytes(allocator, &zalloc_bytes);
    var zalloc_zeroed = true;
    for (zalloc_bytes.?) |value| {
        if (value != 0) {
            zalloc_zeroed = false;
            break;
        }
    }
    try std.testing.expectEqual(fixture.zalloc.zeroed, zalloc_zeroed);
    zalloc.zfreeBytes(allocator, &zalloc_bytes);
    try std.testing.expectEqual(fixture.zalloc.freed_is_null, zalloc_bytes == null);

    const ZallocValue = struct {
        a: u32,
        b: bool,
    };
    var zalloc_value: ?*ZallocValue = try zalloc.zallocValue(allocator, ZallocValue);
    defer zalloc.zfreeValue(allocator, ZallocValue, &zalloc_value);
    try std.testing.expectEqual(fixture.zalloc.value_zeroed, zalloc_value.?.a == 0 and !zalloc_value.?.b);
    zalloc.zfreeValue(allocator, ZallocValue, &zalloc_value);
    try std.testing.expectEqual(fixture.zalloc.value_freed_is_null, zalloc_value == null);

    var strerror_buffer: [64]u8 = undefined;
    try std.testing.expectEqualStrings(fixture.str_error_r.enoent, str_error_r.strErrorR(2, &strerror_buffer));
    try std.testing.expectEqualStrings(fixture.str_error_r.unknown, str_error_r.strErrorR(4096, &strerror_buffer));

    slab.kmalloc_nr_allocated = 0;
    try std.testing.expectEqual(fixture.slab.null_without_reclaim, slab.kmallocBytes(8, 0) == null);
    const slab_plain = slab.kmallocBytes(8, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(fixture.slab.alloc_count_after_kmalloc, slab.kmalloc_nr_allocated);
    var slab_plain_zeroed = true;
    for (slab_plain) |value| {
        if (value != 0) {
            slab_plain_zeroed = false;
            break;
        }
    }
    try std.testing.expectEqual(fixture.slab.zero_after_kmalloc, slab_plain_zeroed);
    for (slab_plain) |*value| {
        value.* = 0xaa;
    }
    slab.kfree(slab_plain);
    try std.testing.expectEqual(fixture.slab.alloc_count_after_kmalloc_free, slab.kmalloc_nr_allocated);

    var slab_array: ?[]u8 = slab.kmallocArray(4, 2, slab.GFP_KERNEL) orelse return error.TestUnexpectedResult;
    defer slab.kfree(slab_array);
    var slab_array_zeroed = true;
    for (slab_array.?) |value| {
        if (value != 0) {
            slab_array_zeroed = false;
            break;
        }
    }
    try std.testing.expectEqual(fixture.slab.array_zeroed, slab_array_zeroed);
    try std.testing.expectEqual(fixture.slab.alloc_count_after_kmalloc_array, slab.kmalloc_nr_allocated);
    try std.testing.expectEqual(fixture.slab.slab_is_available, slab.slabIsAvailable());
    slab.kfree(slab_array);
    slab_array = null;
    try std.testing.expectEqual(fixture.slab.alloc_count_after_kmalloc_array_free, slab.kmalloc_nr_allocated);

    var vsprintf_buffer: [16]u8 = undefined;
    const scnprintf_len = vsprintf.scnprintf(&vsprintf_buffer, "{s}:{d}", .{ "zigux", 7 });
    try std.testing.expectEqual(fixture.vsprintf.scnprintf_len, scnprintf_len);
    try std.testing.expectEqualStrings(fixture.vsprintf.scnprintf_text, vsprintf_buffer[0..scnprintf_len]);

    var vsprintf_pad_buffer: [9]u8 = undefined;
    const scnprintf_pad_len = vsprintf.scnprintfPad(&vsprintf_pad_buffer, vsprintf_pad_buffer.len - 1, "id={d}", .{7});
    try std.testing.expectEqual(fixture.vsprintf.pad_len, scnprintf_pad_len);
    try std.testing.expectEqualStrings(fixture.vsprintf.pad_text, vsprintf_pad_buffer[0 .. vsprintf_pad_buffer.len - 1]);

    const Entry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var entries = [_]Entry{
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 25 },
    };
    var replacement = Entry{ .key = 10 };
    var root = rbtree.Root.init();
    try std.testing.expectEqual(fixture.rbtree.empty_root, rbtree.emptyRoot(&root));
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var insert_order: [5]i32 = undefined;
    var insert_index: usize = 0;
    var current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        insert_order[insert_index] = entry.key;
        insert_index += 1;
    }
    try std.testing.expectEqualSlices(i32, fixture.rbtree.insert_order, insert_order[0..insert_index]);

    var reverse_order: [5]i32 = undefined;
    var reverse_index: usize = 0;
    current = rbtree.last(&root);
    while (current) |node| : (current = rbtree.prev(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        reverse_order[reverse_index] = entry.key;
        reverse_index += 1;
    }
    try std.testing.expectEqualSlices(i32, fixture.rbtree.reverse_order, reverse_order[0..reverse_index]);

    rbtree.erase(&entries[1].node, &root);
    rbtree.replaceNode(&entries[0].node, &replacement.node, &root);
    var replace_order: [4]i32 = undefined;
    var replace_index: usize = 0;
    current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        replace_order[replace_index] = entry.key;
        replace_index += 1;
    }
    try std.testing.expectEqualSlices(i32, fixture.rbtree.replace_order, replace_order[0..replace_index]);

    rbtree.eraseInit(&replacement.node, &root);
    var erase_init_order: [3]i32 = undefined;
    var erase_init_index: usize = 0;
    current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        erase_init_order[erase_init_index] = entry.key;
        erase_init_index += 1;
    }
    try std.testing.expectEqualSlices(i32, fixture.rbtree.erase_init_order, erase_init_order[0..erase_init_index]);
    try std.testing.expectEqual(fixture.rbtree.erase_init_node_empty, rbtree.emptyNode(&replacement.node));

    var postorder_entries = [_]Entry{
        .{ .key = 2 },
        .{ .key = 1 },
        .{ .key = 3 },
    };
    const SearchEntry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const searchLess = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const SearchEntry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const SearchEntry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    const searchCmp = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const SearchEntry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var search_entries = [_]SearchEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 20, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var postorder_root = rbtree.Root.init();
    var search_root = rbtree.Root.init();
    for (&postorder_entries) |*entry| {
        rbtree.add(&entry.node, &postorder_root, less);
    }
    for (&search_entries) |*entry| {
        rbtree.add(&entry.node, &search_root, searchLess);
    }
    var postorder_count: usize = 0;
    current = rbtree.firstPostorder(&postorder_root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        postorder_count += 1;
    }
    try std.testing.expectEqual(fixture.rbtree.postorder_count, postorder_count);
    rbtree.clearNode(&replacement.node);
    try std.testing.expectEqual(fixture.rbtree.cleared_node_empty, rbtree.emptyNode(&replacement.node));

    const find_wanted = @as(i32, 15);
    const found = rbtree.find(&find_wanted, &search_root, searchCmp) orelse return error.TestUnexpectedResult;
    const found_entry: *const SearchEntry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(fixture.rbtree.find_found_key, found_entry.key);

    const missing = @as(i32, 17);
    try std.testing.expectEqual(fixture.rbtree.find_missing, rbtree.find(&missing, &search_root, searchCmp) == null);

    const duplicate_wanted = @as(i32, 10);
    const first_match = rbtree.findFirst(&duplicate_wanted, &search_root, searchCmp) orelse return error.TestUnexpectedResult;
    const first_match_entry: *const SearchEntry = @fieldParentPtr("node", first_match);
    try std.testing.expectEqual(fixture.rbtree.find_first_serial, first_match_entry.serial);

    var next_match_serials: [3]usize = undefined;
    var next_match_count: usize = 0;
    var match_cursor = first_match;
    while (true) {
        const entry: *const SearchEntry = @fieldParentPtr("node", match_cursor);
        next_match_serials[next_match_count] = entry.serial;
        next_match_count += 1;
        match_cursor = rbtree.nextMatch(&duplicate_wanted, match_cursor, searchCmp) orelse break;
    }
    try std.testing.expectEqualSlices(usize, fixture.rbtree.next_match_serials, next_match_serials[0..next_match_count]);
    try std.testing.expectEqual(
        fixture.rbtree.next_match_terminal_null,
        rbtree.nextMatch(&duplicate_wanted, match_cursor, searchCmp) == null,
    );
}

test "phase 1 string replaceChar stops at embedded NUL" {
    var replace_buffer = [_]u8{ 'a', '-', 0, '-', 'z' };
    try std.testing.expectEqual(
        @as(usize, 2),
        string.replaceChar(&replace_buffer, '-', '_'),
    );
    try std.testing.expectEqualSlices(
        u8,
        &[_]u8{ 'a', '_', 0, '-', 'z' },
        &replace_buffer,
    );
}

test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace" {
    var trim_cstr_buf = [_]u8{ ' ', 'h', 'i', ' ', '\n', 0, 'x', 'y' };
    try std.testing.expectEqualStrings("hi", string.trimSpaces(&trim_cstr_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'h', 'i', 0, '\n', 0, 'x', 'y' }, &trim_cstr_buf);

    var strim_cstr_buf = [_]u8{ ' ', 'h', 'i', ' ', '\n', 0, 'x', 'y' };
    try std.testing.expectEqualStrings("hi", string.strim(&strim_cstr_buf));
    try std.testing.expectEqualSlices(u8, &[_]u8{ ' ', 'h', 'i', 0, '\n', 0, 'x', 'y' }, &strim_cstr_buf);
}
