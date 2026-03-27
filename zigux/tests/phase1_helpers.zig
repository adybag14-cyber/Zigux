const std = @import("std");
const argv_split = @import("argv_split");
const bitmap = @import("bitmap");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const find_bit = @import("find_bit");
const hweight = @import("hweight");
const rbtree = @import("rbtree");
const string = @import("string");

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
    },
    bitmap: struct {
        weight: usize,
        scnprintf: []const u8,
        and_result: bool,
        and_values: []const u64,
        andnot_result: bool,
        andnot_values: []const u64,
        or_values: []const u64,
        equal: bool,
        intersects: bool,
        subset: bool,
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
    _ = rbtree;
    _ = string;
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
    try std.testing.expectEqual(fixture.bitmap.equal, bitmap.equal(&bitmap_lhs, &[_]bitmap.Word{ 0x0e, 0 }, 8));
    try std.testing.expectEqual(fixture.bitmap.intersects, bitmap.intersects(&bitmap_lhs, &bitmap_rhs, 8));
    try std.testing.expectEqual(fixture.bitmap.subset, bitmap.subset(&bitmap_rhs, &bitmap_lhs, 8));

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

    var postorder_entries = [_]Entry{
        .{ .key = 2 },
        .{ .key = 1 },
        .{ .key = 3 },
    };
    var postorder_root = rbtree.Root.init();
    for (&postorder_entries) |*entry| {
        rbtree.add(&entry.node, &postorder_root, less);
    }
    var postorder_count: usize = 0;
    current = rbtree.firstPostorder(&postorder_root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        postorder_count += 1;
    }
    try std.testing.expectEqual(fixture.rbtree.postorder_count, postorder_count);
    rbtree.clearNode(&replacement.node);
    try std.testing.expectEqual(fixture.rbtree.cleared_node_empty, rbtree.emptyNode(&replacement.node));
}
