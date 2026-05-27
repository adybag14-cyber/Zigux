const std = @import("std");
const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const bitmap = @import("bitmap");
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

const fixture_bytes = @embedFile("fixtures/phase1_helpers.json");

const Fixture = struct {
    argv_split: struct {
        argc: usize,
        argv: []const []const u8,
        blank_argc: usize,
    },
    cmdline: struct {
        decimal_k: struct {
            value: u64,
            rest: []const u8,
        },
        signed_k: struct {
            value: u64,
            rest: []const u8,
        },
        saturated_positive_signed: struct {
            value: u64,
            rest: []const u8,
        },
        hex_m: struct {
            value: u64,
            rest: []const u8,
        },
        octal_k: struct {
            value: u64,
            rest: []const u8,
        },
        invalid: struct {
            value: u64,
            rest: []const u8,
        },
        option_debug: bool,
        option_empty_leading: bool,
        option_empty_double_comma: bool,
        option_empty_trailing: bool,
        option_absent: bool,
        first_arg: struct {
            param: []const u8,
            value: []const u8,
            remaining: []const u8,
        },
        second_arg: struct {
            param: []const u8,
            value: []const u8,
            remaining: []const u8,
        },
        quoted_arg: struct {
            param: []const u8,
            value: []const u8,
            remaining: []const u8,
        },
        unterminated_arg: struct {
            param: []const u8,
            value: []const u8,
            remaining: []const u8,
        },
    },
    ctype: struct {
        isalpha_z: bool,
        isdigit_7: bool,
        tolower_A: u8,
        toupper_z: u8,
    },
    hweight: struct {
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
        copy_values: []const u64,
        copy_clear_tail_values: []const u64,
        copy_and_extend_values: []const u64,
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
    },
    string: struct {
        strtobool_y: bool,
        strtobool_on: bool,
        strtobool_zero: bool,
        strtobool_off: bool,
        strtobool_invalid: u8,
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
        match_iterator_serials: []const usize,
        cached_leftmost_return_serials: []const i32,
        cached_root_transition_serials: []const i32,
        next_match_terminal_null: bool,
    },
    slab: struct {
        alloc_count_after_kmalloc: isize,
        zero_after_kmalloc: bool,
        alloc_count_after_kmalloc_free: isize,
    },
    str_error_r: struct {
        enoent: []const u8,
    },
    vsprintf: struct {
        scnprintf_text: []const u8,
        scnprintf_len: usize,
        pad_text: []const u8,
        pad_len: usize,
    },
    zalloc: struct {
        zeroed: bool,
        freed_is_null: bool,
        value_zeroed: bool,
        value_freed_is_null: bool,
    },
};

const ListSortReplayEntry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const RbtreeReplayEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),

    fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
        const lhs_entry: *const RbtreeReplayEntry = @fieldParentPtr("node", lhs);
        const rhs_entry: *const RbtreeReplayEntry = @fieldParentPtr("node", rhs);
        if (lhs_entry.key != rhs_entry.key) {
            return lhs_entry.key < rhs_entry.key;
        }
        return lhs_entry.serial < rhs_entry.serial;
    }

    fn cmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
        const wanted: *const i32 = @ptrCast(@alignCast(key));
        const entry: *const RbtreeReplayEntry = @fieldParentPtr("node", node);
        if (wanted.* < entry.key) return -1;
        if (wanted.* > entry.key) return 1;
        return 0;
    }
};

fn loadFixture() !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, std.testing.allocator, fixture_bytes, .{
        .ignore_unknown_fields = true,
    });
}

test "phase 1 helper ports match committed parity fixture" {
    var parsed = try loadFixture();
    defer parsed.deinit();
    const fixture = parsed.value;

    var split = try argv_split.argv_split(std.testing.allocator, "alpha beta gamma");
    defer argv_split.argv_free(&split);
    try std.testing.expectEqual(fixture.argv_split.argc, split.argc());
    for (fixture.argv_split.argv, 0..) |expected, idx| {
        try std.testing.expectEqualStrings(expected, split.argv[idx]);
    }

    var blank_split = try argv_split.argv_split(std.testing.allocator, "   \t  ");
    defer argv_split.argv_free(&blank_split);
    try std.testing.expectEqual(fixture.argv_split.blank_argc, blank_split.argc());

    const decimal_k = cmdline.memparse("64K rest");
    try std.testing.expectEqual(fixture.cmdline.decimal_k.value, decimal_k.value);
    try std.testing.expectEqualStrings(fixture.cmdline.decimal_k.rest, decimal_k.rest);

    const signed_k = cmdline.memparse("-2K tail");
    try std.testing.expectEqual(fixture.cmdline.signed_k.value, signed_k.value);
    try std.testing.expectEqualStrings(fixture.cmdline.signed_k.rest, signed_k.rest);

    const saturated_positive_signed = cmdline.memparse("+9223372036854775808");
    try std.testing.expectEqual(fixture.cmdline.saturated_positive_signed.value, saturated_positive_signed.value);
    try std.testing.expectEqualStrings(fixture.cmdline.saturated_positive_signed.rest, saturated_positive_signed.rest);

    const hex_m = cmdline.memparse("0x20M");
    try std.testing.expectEqual(fixture.cmdline.hex_m.value, hex_m.value);
    try std.testing.expectEqualStrings(fixture.cmdline.hex_m.rest, hex_m.rest);

    const octal_k = cmdline.memparse("010K");
    try std.testing.expectEqual(fixture.cmdline.octal_k.value, octal_k.value);
    try std.testing.expectEqualStrings(fixture.cmdline.octal_k.rest, octal_k.rest);

    const invalid = cmdline.memparse("xyz");
    try std.testing.expectEqual(fixture.cmdline.invalid.value, invalid.value);
    try std.testing.expectEqualStrings(fixture.cmdline.invalid.rest, invalid.rest);

    try std.testing.expectEqual(fixture.cmdline.option_debug, cmdline.parseOptionStr("quiet,debug,nohlt", "debug"));
    try std.testing.expectEqual(fixture.cmdline.option_empty_leading, cmdline.parseOptionStr(",quiet", ""));
    try std.testing.expectEqual(fixture.cmdline.option_empty_double_comma, cmdline.parseOptionStr("rootwait,,quiet", ""));
    try std.testing.expectEqual(fixture.cmdline.option_empty_trailing, cmdline.parseOptionStr("quiet,", ""));
    try std.testing.expectEqual(fixture.cmdline.option_absent, cmdline.parseOptionStr("quiet,debug,nohlt", "panic"));

    const first_arg = cmdline.nextArg("console=ttyS0,115200 root=\"/dev/sda1 quiet\" panic=-1") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings(fixture.cmdline.first_arg.param, first_arg.param);
    try std.testing.expectEqualStrings(fixture.cmdline.first_arg.value, first_arg.value.?);
    try std.testing.expectEqualStrings(fixture.cmdline.first_arg.remaining, first_arg.remaining);

    const second_arg = cmdline.nextArg(first_arg.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings(fixture.cmdline.second_arg.param, second_arg.param);
    try std.testing.expectEqualStrings(fixture.cmdline.second_arg.value, second_arg.value.?);
    try std.testing.expectEqualStrings(fixture.cmdline.second_arg.remaining, second_arg.remaining);

    const quoted_arg = cmdline.nextArg("\"mode=fast path\" tail") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings(fixture.cmdline.quoted_arg.param, quoted_arg.param);
    try std.testing.expectEqualStrings(fixture.cmdline.quoted_arg.value, quoted_arg.value.?);
    try std.testing.expectEqualStrings(fixture.cmdline.quoted_arg.remaining, quoted_arg.remaining);

    const unterminated_arg = cmdline.nextArg("mode=\"fast boot") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings(fixture.cmdline.unterminated_arg.param, unterminated_arg.param);
    try std.testing.expectEqualStrings(fixture.cmdline.unterminated_arg.value, unterminated_arg.value.?);
    try std.testing.expectEqualStrings(fixture.cmdline.unterminated_arg.remaining, unterminated_arg.remaining);

    try std.testing.expectEqual(fixture.ctype.isalpha_z, ctype.isalpha('z'));
    try std.testing.expectEqual(fixture.ctype.isdigit_7, ctype.isdigit('7'));
    try std.testing.expectEqual(fixture.ctype.tolower_A, ctype.fastTolower('A'));
    try std.testing.expectEqual(fixture.ctype.toupper_z, ctype.toupper('z'));

    try std.testing.expectEqual(fixture.hweight.w32, hweight.swHweight32(0xf0f0_f0f0));
    try std.testing.expectEqual(fixture.hweight.w64, hweight.swHweight64(0xf0f0_f0f0_f0f0_f0f0));
    try std.testing.expectEqual(fixture.hweight.wlong, hweight.hweightLong(0xff));

    var head: list_sort.ListHead = .{};
    head.init();
    var entries = [_]ListSortReplayEntry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
    };
    const cmp = struct {
        fn less(_: ?*anyopaque, lhs: *const list_sort.ListHead, rhs: *const list_sort.ListHead) i32 {
            const lhs_entry: *const ListSortReplayEntry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const ListSortReplayEntry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.less;
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }
    list_sort.listSort(null, &head, cmp);

    var sorted_keys: [5]i32 = undefined;
    var sorted_ordinals: [5]usize = undefined;
    var count: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const ListSortReplayEntry = @fieldParentPtr("node", current.?);
        sorted_keys[count] = entry.key;
        sorted_ordinals[count] = entry.ordinal;
        count += 1;
    }
    try std.testing.expectEqualSlices(i32, fixture.list_sort.tri_sorted_keys, sorted_keys[0..count]);
    try std.testing.expectEqualSlices(usize, fixture.list_sort.tri_sorted_ordinals, sorted_ordinals[0..count]);

    var bool_head: list_sort.ListHead = .{};
    bool_head.init();
    var bool_entries = [_]ListSortReplayEntry{
        .{ .key = 2, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 3, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 3, .ordinal = 4 },
    };
    const bool_cmp = struct {
        fn less(_: ?*anyopaque, lhs: *const list_sort.ListHead, rhs: *const list_sort.ListHead) i32 {
            const lhs_entry: *const ListSortReplayEntry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const ListSortReplayEntry = @fieldParentPtr("node", rhs);
            return @intFromBool(lhs_entry.key > rhs_entry.key);
        }
    }.less;
    for (&bool_entries) |*entry| {
        list_sort.listAddTail(&entry.node, &bool_head);
    }
    list_sort.listSort(null, &bool_head, bool_cmp);

    var bool_sorted_keys: [5]i32 = undefined;
    var bool_sorted_ordinals: [5]usize = undefined;
    var bool_count: usize = 0;
    var bool_current = bool_head.next;
    while (bool_current != &bool_head) : (bool_current = bool_current.?.next) {
        const entry: *const ListSortReplayEntry = @fieldParentPtr("node", bool_current.?);
        bool_sorted_keys[bool_count] = entry.key;
        bool_sorted_ordinals[bool_count] = entry.ordinal;
        bool_count += 1;
    }
    try std.testing.expectEqualSlices(i32, fixture.list_sort.bool_sorted_keys, bool_sorted_keys[0..bool_count]);
    try std.testing.expectEqualSlices(usize, fixture.list_sort.bool_sorted_ordinals, bool_sorted_ordinals[0..bool_count]);

    const nbits = fixture.find_bit.bits_per_long * 2 + 8;
    const bitmap_a = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 5) | (@as(find_bit.Word, 1) << 9),
        (@as(find_bit.Word, 1) << 2) | (@as(find_bit.Word, 1) << 7),
        0,
    };
    const bitmap_b = [_]find_bit.Word{
        (~@as(find_bit.Word, 0)) ^ (@as(find_bit.Word, 1) << 3),
        (~@as(find_bit.Word, 0)) ^ (@as(find_bit.Word, 1) << 4),
        0,
    };
    const bitmap_and = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 9),
        (@as(find_bit.Word, 1) << 2),
        0,
    };
    try std.testing.expectEqual(fixture.find_bit.first, find_bit.findFirstBit(&bitmap_a, nbits));
    try std.testing.expectEqual(fixture.find_bit.next_after_6, find_bit.findNextBit(&bitmap_a, nbits, 6));
    try std.testing.expectEqual(fixture.find_bit.next_after_word, find_bit.findNextBit(&bitmap_a, nbits, fixture.find_bit.bits_per_long));
    try std.testing.expectEqual(fixture.find_bit.first_zero, find_bit.findFirstZeroBit(&bitmap_b, nbits));
    try std.testing.expectEqual(fixture.find_bit.next_zero, find_bit.findNextZeroBit(&bitmap_b, nbits, fixture.find_bit.bits_per_long));
    try std.testing.expectEqual(fixture.find_bit.first_and, find_bit.findFirstAndBit(&bitmap_a, &bitmap_and, nbits));
    try std.testing.expectEqual(fixture.find_bit.next_and, find_bit.findNextAndBit(&bitmap_a, &bitmap_and, nbits, fixture.find_bit.bits_per_long));
    try std.testing.expectEqual(fixture.find_bit.last, find_bit.findLastBit(&bitmap_a, nbits));

    var bitmap_words = [_]find_bit.Word{ 0, 0, 0 };
    bitmap.setRange(&bitmap_words, 1, 3);
    bitmap.setRange(&bitmap_words, 66, 2);
    try std.testing.expectEqual(@as(usize, fixture.bitmap.weight), bitmap.weight(&bitmap_words, 130));
    try std.testing.expectEqualSlices(u64, fixture.bitmap.range_after_set, &[_]u64{
        @intCast(bitmap_words[0]),
        @intCast(bitmap_words[1]),
        @intCast(bitmap_words[2]),
    });

    var rendered: [32]u8 = undefined;
    const rendered_len = bitmap.scnprintf(&bitmap_words, 130, &rendered);
    try std.testing.expectEqualStrings(fixture.bitmap.scnprintf, rendered[0..rendered_len]);

    var truncated_rendered = [_]u8{0xaa} ** 8;
    const truncated_len = bitmap.scnprintf(&bitmap_words, 130, &truncated_rendered);
    try std.testing.expectEqual(fixture.bitmap.truncated_scnprintf_len, truncated_len);
    try std.testing.expectEqualStrings(fixture.bitmap.truncated_scnprintf, truncated_rendered[0..truncated_len]);

    var terminator_only = [_]u8{0xaa};
    const terminator_only_len = bitmap.scnprintf(&bitmap_words, 130, terminator_only[0..1]);
    try std.testing.expectEqual(fixture.bitmap.terminator_only_scnprintf_len, terminator_only_len);
    try std.testing.expectEqual(fixture.bitmap.terminator_only_nul, terminator_only[0]);

    var zero_length_backing = [_]u8{0xbb};
    const zero_length_len = bitmap.scnprintf(&bitmap_words, 130, zero_length_backing[0..0]);
    try std.testing.expectEqual(fixture.bitmap.zero_length_scnprintf_len, zero_length_len);

    var plain_bitmap: ?[]find_bit.Word = try bitmap.bitmapAlloc(std.testing.allocator, 130);
    defer bitmap.bitmapFree(std.testing.allocator, &plain_bitmap);
    try std.testing.expectEqual(fixture.bitmap.alloc_words, plain_bitmap.?.len);

    var zero_bitmap: ?[]find_bit.Word = try bitmap.bitmapZalloc(std.testing.allocator, 130);
    defer bitmap.bitmapFree(std.testing.allocator, &zero_bitmap);
    try std.testing.expectEqual(fixture.bitmap.zalloc_words, zero_bitmap.?.len);
    try std.testing.expectEqual(fixture.bitmap.zalloc_values.len, zero_bitmap.?.len);
    for (zero_bitmap.?, fixture.bitmap.zalloc_values) |actual, expected| {
        try std.testing.expectEqual(expected, @as(u64, @intCast(actual)));
    }

    const copy_nbits = fixture.find_bit.bits_per_long + 5;
    const copy_src = [_]find_bit.Word{ ~@as(find_bit.Word, 0), ~@as(find_bit.Word, 0), 0 };

    var copy_dst = [_]find_bit.Word{ 0, 0 };
    bitmap.copy(&copy_dst, copy_src[0..2], copy_nbits);
    try std.testing.expectEqualSlices(u64, fixture.bitmap.copy_values, &[_]u64{
        @intCast(copy_dst[0]),
        @intCast(copy_dst[1]),
    });

    var copy_clear_tail_dst = [_]find_bit.Word{ 0, 0 };
    bitmap.copyClearTail(&copy_clear_tail_dst, copy_src[0..2], copy_nbits);
    try std.testing.expectEqualSlices(u64, fixture.bitmap.copy_clear_tail_values, &[_]u64{
        @intCast(copy_clear_tail_dst[0]),
        @intCast(copy_clear_tail_dst[1]),
    });

    var copy_and_extend_dst = [_]find_bit.Word{ 0, 0, 0 };
    bitmap.copyAndExtend(&copy_and_extend_dst, copy_src[0..2], copy_nbits, fixture.find_bit.bits_per_long * 3);
    try std.testing.expectEqualSlices(u64, fixture.bitmap.copy_and_extend_values, &[_]u64{
        @intCast(copy_and_extend_dst[0]),
        @intCast(copy_and_extend_dst[1]),
        @intCast(copy_and_extend_dst[2]),
    });

    const logic_lhs = [_]find_bit.Word{ 0b1110, 0 };
    const logic_rhs = [_]find_bit.Word{ 0b1010, 0 };
    var logic_dst = [_]find_bit.Word{ 0, 0 };

    try std.testing.expectEqual(fixture.bitmap.and_result, bitmap.andBits(&logic_dst, &logic_lhs, &logic_rhs, 8));
    try std.testing.expectEqualSlices(u64, fixture.bitmap.and_values, &[_]u64{
        @intCast(logic_dst[0]),
        @intCast(logic_dst[1]),
    });

    try std.testing.expectEqual(fixture.bitmap.andnot_result, bitmap.andNotBits(&logic_dst, &logic_lhs, &logic_rhs, 8));
    try std.testing.expectEqualSlices(u64, fixture.bitmap.andnot_values, &[_]u64{
        @intCast(logic_dst[0]),
        @intCast(logic_dst[1]),
    });

    bitmap.orBits(&logic_dst, &logic_lhs, &logic_rhs, 8);
    try std.testing.expectEqualSlices(u64, fixture.bitmap.or_values, &[_]u64{
        @intCast(logic_dst[0]),
        @intCast(logic_dst[1]),
    });

    bitmap.xorBits(&logic_dst, &logic_lhs, &logic_rhs, 8);
    try std.testing.expectEqualSlices(u64, fixture.bitmap.xor_values, &[_]u64{
        @intCast(logic_dst[0]),
        @intCast(logic_dst[1]),
    });

    try std.testing.expectEqual(fixture.bitmap.equal, bitmap.equal(&logic_lhs, &[_]find_bit.Word{ 0b1110, 0 }, 8));
    try std.testing.expectEqual(fixture.bitmap.intersects, bitmap.intersects(&logic_lhs, &logic_rhs, 8));
    try std.testing.expectEqual(fixture.bitmap.subset, bitmap.subset(&logic_rhs, &logic_lhs, 8));

    var partial_xor_dst = [_]find_bit.Word{0};
    bitmap.xorBits(&partial_xor_dst, &[_]find_bit.Word{0b1_1111}, &[_]find_bit.Word{0b1_0001}, fixture.bitmap.partial_xor_nbits);
    try std.testing.expectEqualSlices(u64, fixture.bitmap.partial_xor_masked_values, &[_]u64{
        @intCast(partial_xor_dst[0] & bitmap.lastWordMask(fixture.bitmap.partial_xor_nbits)),
    });

    bitmap.clearRange(&bitmap_words, 1, 3);
    bitmap.clearRange(&bitmap_words, 66, 2);
    try std.testing.expectEqualSlices(u64, fixture.bitmap.range_after_clear, &[_]u64{
        @intCast(bitmap_words[0]),
        @intCast(bitmap_words[1]),
        @intCast(bitmap_words[2]),
    });
    bitmap.fill(&bitmap_words, 130);
    try std.testing.expectEqual(fixture.bitmap.full_after_fill, bitmap.full(&bitmap_words, 130));
    bitmap.zero(&bitmap_words, 130);
    try std.testing.expectEqual(fixture.bitmap.empty_after_zero, bitmap.empty(&bitmap_words, 130));

    try std.testing.expectEqual(fixture.string.strtobool_y, try string.strtobool("y"));
    try std.testing.expectEqual(fixture.string.strtobool_on, try string.strtobool("on"));
    try std.testing.expectEqual(fixture.string.strtobool_zero, try string.strtobool("0"));
    try std.testing.expectEqual(fixture.string.strtobool_off, try string.strtobool("off"));
    try std.testing.expectError(error.Invalid, string.strtobool("maybe"));
    try std.testing.expectEqual(fixture.string.strtobool_invalid, @as(u8, @intCast(@intFromError(error.Invalid))));

    var copied = [_]u8{ 0, 0, 0, 0 };
    try std.testing.expectEqual(fixture.string.strlcpy_len, string.strlcpy(copied[0..], "hello"));
    try std.testing.expectEqualStrings(fixture.string.strlcpy_buffer, copied[0 .. copied.len - 1]);
    try std.testing.expectEqualStrings(fixture.string.skip_spaces, string.skipSpaces(" \t hello"));

    var trim_buf = [_]u8{ ' ', 'h', 'i', ' ', 0 };
    try std.testing.expectEqualStrings(fixture.string.trim_spaces, string.trimSpaces(trim_buf[0..]));

    var remove_buf = [_]u8{ 'a', ' ', 'b', ' ', 'c', 0 };
    try std.testing.expectEqualStrings(fixture.string.remove_spaces, string.removeSpaces(remove_buf[0..]));

    var replace_buf = [_]u8{ 'a', '-', 'b', 0 };
    try std.testing.expectEqual(fixture.string.replace_char_end, string.replaceChar(replace_buf[0..], '-', '_'));
    try std.testing.expectEqualStrings(fixture.string.replace_char, replace_buf[0 .. replace_buf.len - 1]);

    var replace_cstr_buf = [_]u8{ 'a', '-', 0, '-', 'z' };
    try std.testing.expectEqual(fixture.string.replace_char_cstr_end, string.replaceChar(replace_cstr_buf[0..], '-', '_'));
    try std.testing.expectEqualSlices(u8, fixture.string.replace_char_cstr_bytes, replace_cstr_buf[0..]);

    try std.testing.expectEqual(@as(?usize, fixture.string.memchr_inv_index), string.memchrInv(&[_]u8{ 'x', 'x', 'x', 'x', 'y' }, 'x'));
    try std.testing.expectEqual(fixture.string.memchr_inv_none, string.memchrInv(&[_]u8{ 'x', 'x', 'x' }, 'x') == null);

    slab.kmalloc_nr_allocated = 0;
    const allocated = slab.kmallocBytes(4, slab.GFP_KERNEL | slab.__GFP_ZERO) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(fixture.slab.alloc_count_after_kmalloc, slab.kmalloc_nr_allocated);
    if (fixture.slab.zero_after_kmalloc) {
        for (allocated) |byte| {
            try std.testing.expectEqual(@as(u8, 0), byte);
        }
    }
    slab.kfree(allocated);
    try std.testing.expectEqual(fixture.slab.alloc_count_after_kmalloc_free, slab.kmalloc_nr_allocated);

    var err_buf: [64]u8 = undefined;
    try std.testing.expectEqualStrings(fixture.str_error_r.enoent, str_error_r.strErrorR(2, &err_buf));

    var render_buf: [16]u8 = undefined;
    const render_len = vsprintf.scnprintf(&render_buf, "{s}:{d}", .{ "zigux", 7 });
    try std.testing.expectEqual(fixture.vsprintf.scnprintf_len, render_len);
    try std.testing.expectEqualStrings(fixture.vsprintf.scnprintf_text, render_buf[0..render_len]);
    var pad_buf: [12]u8 = undefined;
    const pad_len = vsprintf.scnprintfPad(&pad_buf, 8, "id={d}", .{7});
    try std.testing.expectEqual(fixture.vsprintf.pad_len, pad_len);
    try std.testing.expectEqualStrings(fixture.vsprintf.pad_text, pad_buf[0..8]);

    const allocator = std.testing.allocator;
    var zeroed: ?[]u8 = try zalloc.zallocBytes(allocator, 6);
    defer zalloc.zfreeBytes(allocator, &zeroed);
    try std.testing.expectEqual(fixture.zalloc.zeroed, zeroed != null);
    for (zeroed.?) |byte| {
        try std.testing.expectEqual(@as(u8, 0), byte);
    }
    var freed_view = zeroed;
    zalloc.zfreeBytes(allocator, &freed_view);
    try std.testing.expectEqual(fixture.zalloc.freed_is_null, freed_view == null);

    const ZeroValue = struct {
        count: u32,
        enabled: bool,
    };
    var zero_value: ?*ZeroValue = try zalloc.zallocValue(allocator, ZeroValue);
    defer zalloc.zfreeValue(allocator, ZeroValue, &zero_value);
    try std.testing.expectEqual(fixture.zalloc.value_zeroed, zero_value.?.count == 0 and zero_value.?.enabled == false);
    var freed_value = zero_value;
    zalloc.zfreeValue(allocator, ZeroValue, &freed_value);
    try std.testing.expectEqual(fixture.zalloc.value_freed_is_null, freed_value == null);

    var root = rbtree.Root.init();
    try std.testing.expectEqual(fixture.rbtree.empty_root, root.node == null);
    var tree_entries = [_]RbtreeReplayEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 25, .serial = 4 },
        .{ .key = 15, .serial = 5 },
        .{ .key = 10, .serial = 6 },
    };
    for (&tree_entries) |*entry| {
        rbtree.add(&entry.node, &root, RbtreeReplayEntry.less);
    }

    var ordered: [5]i32 = undefined;
    var ordered_count: usize = 0;
    var node = rbtree.first(&root);
    while (node) |current_node| : (node = rbtree.next(current_node)) {
        const entry: *const RbtreeReplayEntry = @fieldParentPtr("node", current_node);
        if (entry.serial == 0 or entry.serial == 1 or entry.serial == 3 or entry.serial == 4 or entry.serial == 5) {
            ordered[ordered_count] = entry.key;
            ordered_count += 1;
        }
    }
    try std.testing.expectEqualSlices(i32, fixture.rbtree.insert_order, ordered[0..ordered_count]);

    var reverse: [5]i32 = undefined;
    var reverse_count: usize = 0;
    node = rbtree.last(&root);
    while (node) |current_node| : (node = rbtree.prev(current_node)) {
        const entry: *const RbtreeReplayEntry = @fieldParentPtr("node", current_node);
        if (entry.serial == 0 or entry.serial == 1 or entry.serial == 3 or entry.serial == 4 or entry.serial == 5) {
            reverse[reverse_count] = entry.key;
            reverse_count += 1;
        }
    }
    try std.testing.expectEqualSlices(i32, fixture.rbtree.reverse_order, reverse[0..reverse_count]);

    var replace_entries = [_]RbtreeReplayEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 15, .serial = 3 },
        .{ .key = 25, .serial = 4 },
    };
    var replacement = RbtreeReplayEntry{ .key = 10, .serial = 5 };
    var replace_root = rbtree.Root.init();
    for (&replace_entries) |*entry| {
        rbtree.add(&entry.node, &replace_root, RbtreeReplayEntry.less);
    }
    rbtree.erase(&replace_entries[1].node, &replace_root);
    rbtree.replaceNode(&replace_entries[0].node, &replacement.node, &replace_root);

    var replace_order: [4]i32 = undefined;
    var replace_count: usize = 0;
    node = rbtree.first(&replace_root);
    while (node) |current_node| : (node = rbtree.next(current_node)) {
        const entry: *const RbtreeReplayEntry = @fieldParentPtr("node", current_node);
        replace_order[replace_count] = entry.key;
        replace_count += 1;
    }
    try std.testing.expectEqualSlices(i32, fixture.rbtree.replace_order, replace_order[0..replace_count]);

    rbtree.eraseInit(&replacement.node, &replace_root);
    try std.testing.expectEqual(fixture.rbtree.erase_init_node_empty, rbtree.emptyNode(&replacement.node));

    var erase_init_order: [3]i32 = undefined;
    var erase_init_count: usize = 0;
    node = rbtree.first(&replace_root);
    while (node) |current_node| : (node = rbtree.next(current_node)) {
        const entry: *const RbtreeReplayEntry = @fieldParentPtr("node", current_node);
        erase_init_order[erase_init_count] = entry.key;
        erase_init_count += 1;
    }
    try std.testing.expectEqualSlices(i32, fixture.rbtree.erase_init_order, erase_init_order[0..erase_init_count]);

    var detached = rbtree.Node.init();
    rbtree.clearNode(&detached);
    try std.testing.expectEqual(fixture.rbtree.cleared_node_empty, rbtree.emptyNode(&detached));

    var postorder_entries = [_]RbtreeReplayEntry{
        .{ .key = 2, .serial = 0 },
        .{ .key = 1, .serial = 1 },
        .{ .key = 3, .serial = 2 },
    };
    var postorder_root = rbtree.Root.init();
    for (&postorder_entries) |*entry| {
        rbtree.add(&entry.node, &postorder_root, RbtreeReplayEntry.less);
    }
    var postorder_count: usize = 0;
    var postorder_node = rbtree.firstPostorder(&postorder_root);
    while (postorder_node) |current_node| : (postorder_node = rbtree.nextPostorder(current_node)) {
        _ = current_node;
        postorder_count += 1;
    }
    try std.testing.expectEqual(fixture.rbtree.postorder_count, postorder_count);

    const duplicate_key = @as(i32, 10);
    const found = rbtree.find(&duplicate_key, &root, RbtreeReplayEntry.cmp) orelse return error.TestUnexpectedResult;
    const found_entry: *const RbtreeReplayEntry = @fieldParentPtr("node", found);
    try std.testing.expectEqual(fixture.rbtree.find_found_key, found_entry.key);

    const missing_key = @as(i32, 17);
    try std.testing.expectEqual(fixture.rbtree.find_missing, rbtree.find(&missing_key, &root, RbtreeReplayEntry.cmp) == null);

    const first_duplicate = rbtree.findFirst(&duplicate_key, &root, RbtreeReplayEntry.cmp) orelse return error.TestUnexpectedResult;
    const first_duplicate_entry: *const RbtreeReplayEntry = @fieldParentPtr("node", first_duplicate);
    try std.testing.expectEqual(fixture.rbtree.find_first_serial, first_duplicate_entry.serial);

    var duplicate_serials: [3]usize = undefined;
    var duplicate_count: usize = 0;
    var iter = rbtree.matchIterator(&duplicate_key, &root, RbtreeReplayEntry.cmp);
    while (iter.next()) |current_node| {
        const entry: *const RbtreeReplayEntry = @fieldParentPtr("node", current_node);
        duplicate_serials[duplicate_count] = entry.serial;
        duplicate_count += 1;
    }
    try std.testing.expectEqualSlices(usize, fixture.rbtree.match_iterator_serials, duplicate_serials[0..duplicate_count]);

    duplicate_serials = undefined;
    duplicate_count = 0;
    var current_match: ?*rbtree.Node = first_duplicate;
    var terminal_match: *rbtree.Node = first_duplicate;
    while (current_match) |match_node| {
        const entry: *const RbtreeReplayEntry = @fieldParentPtr("node", match_node);
        duplicate_serials[duplicate_count] = entry.serial;
        duplicate_count += 1;
        terminal_match = match_node;
        current_match = rbtree.nextMatch(&duplicate_key, match_node, RbtreeReplayEntry.cmp);
    }
    try std.testing.expectEqualSlices(usize, fixture.rbtree.next_match_serials, duplicate_serials[0..duplicate_count]);
    try std.testing.expectEqual(fixture.rbtree.next_match_terminal_null, rbtree.nextMatch(&duplicate_key, terminal_match, RbtreeReplayEntry.cmp) == null);

    var cached_entries = [_]RbtreeReplayEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 12, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 5, .serial = 3 },
    };
    var cached_root = rbtree.RootCached.init();
    var return_serials: [4]i32 = undefined;
    return_serials[0] = serialOrSentinel(rbtree.addCached(&cached_entries[0].node, &cached_root, RbtreeReplayEntry.less));
    return_serials[1] = serialOrSentinel(rbtree.addCached(&cached_entries[1].node, &cached_root, RbtreeReplayEntry.less));
    return_serials[2] = serialOrSentinel(rbtree.addCached(&cached_entries[2].node, &cached_root, RbtreeReplayEntry.less));
    return_serials[3] = serialOrSentinel(rbtree.addCached(&cached_entries[3].node, &cached_root, RbtreeReplayEntry.less));
    try std.testing.expectEqualSlices(i32, fixture.rbtree.cached_leftmost_return_serials, &return_serials);

    var cached_transition_entries = [_]RbtreeReplayEntry{
        .{ .key = 10, .serial = 1 },
        .{ .key = 5, .serial = 0 },
        .{ .key = 20, .serial = 3 },
        .{ .key = 15, .serial = 5 },
    };
    var cached_replacement = RbtreeReplayEntry{ .key = 10, .serial = 4 };
    var cached_new_leftmost = RbtreeReplayEntry{ .key = 3, .serial = 2 };
    var cached_transition_root = rbtree.RootCached.init();
    for (&cached_transition_entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &cached_transition_root, RbtreeReplayEntry.less);
    }
    var cached_transition_serials: [4]i32 = undefined;
    cached_transition_serials[0] = serialOrSentinel(rbtree.firstCached(&cached_transition_root));
    _ = rbtree.eraseCached(&cached_transition_entries[2].node, &cached_transition_root);
    cached_transition_serials[1] = serialOrSentinel(rbtree.firstCached(&cached_transition_root));
    rbtree.replaceNodeCached(&cached_transition_entries[1].node, &cached_replacement.node, &cached_transition_root);
    cached_transition_serials[2] = serialOrSentinel(rbtree.firstCached(&cached_transition_root));
    _ = rbtree.addCached(&cached_new_leftmost.node, &cached_transition_root, RbtreeReplayEntry.less);
    cached_transition_serials[3] = serialOrSentinel(rbtree.firstCached(&cached_transition_root));
    try std.testing.expectEqualSlices(i32, fixture.rbtree.cached_root_transition_serials, &cached_transition_serials);
}

fn serialOrSentinel(node: ?*rbtree.Node) i32 {
    const current = node orelse return -1;
    const entry: *const RbtreeReplayEntry = @fieldParentPtr("node", current);
    return @as(i32, @intCast(entry.serial));
}
