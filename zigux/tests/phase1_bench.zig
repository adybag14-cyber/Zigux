const std = @import("std");
const bitmap = @import("bitmap");
const find_bit = @import("find_bit");
const hweight = @import("hweight");
const list_sort = @import("list_sort");
const rbtree = @import("rbtree");
const string = @import("string");

const Io = std.Io;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const iterations_bitmap = 20_000;
const iterations_bitmap_window = 20_000;
const iterations_bitmap_copy = 20_000;
const iterations_bitmap_scnprintf = 12_000;
const iterations_find_bit = 20_000;
const iterations_find_bit_same_word = 20_000;
const iterations_find_zero_bit = 20_000;
const iterations_find_and_bit = 20_000;
const iterations_string = 40_000;
const iterations_hweight = 100_000;
const iterations_list_sort = 1_000;
const iterations_rbtree = 4_000;

fn bitmapBench() struct { checksum: u64 } {
    var map = [_]bitmap.Word{0} ** bitmap.bitsToWords(4096);
    bitmap.setRange(&map, 5, 32);
    bitmap.setRange(&map, 256, 64);
    bitmap.setRange(&map, 2048, 17);

    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_bitmap) : (idx += 1) {
        checksum +%= @intCast(bitmap.weight(&map, 4096));
    }

    return .{ .checksum = checksum };
}

fn bitmapWindowBench() struct { checksum: u64 } {
    const nbits = bitmap.bits_per_long + 5;
    var lhs = [_]bitmap.Word{0} ** bitmap.bitsToWords(nbits);
    var rhs = [_]bitmap.Word{0} ** bitmap.bitsToWords(nbits);
    var dst = [_]bitmap.Word{0} ** bitmap.bitsToWords(nbits);

    bitmap.setRange(&lhs, 1, 4);
    bitmap.setRange(&lhs, bitmap.bits_per_long - 2, 6);
    bitmap.setRange(&rhs, 0, 2);
    bitmap.setRange(&rhs, bitmap.bits_per_long, 4);

    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_bitmap_window) : (idx += 1) {
        if ((idx & 1) == 0) {
            lhs[1] |= @as(bitmap.Word, 1) << 2;
            rhs[1] &= ~(@as(bitmap.Word, 1) << 4);
        } else {
            lhs[1] &= ~(@as(bitmap.Word, 1) << 2);
            rhs[1] |= @as(bitmap.Word, 1) << 4;
        }

        bitmap.orBits(&dst, &lhs, &rhs, nbits);
        checksum +%= @intCast(bitmap.weight(&dst, nbits));

        checksum +%= @as(u64, @intFromBool(bitmap.andBits(&dst, &lhs, &rhs, nbits)));
        checksum +%= @intCast(bitmap.weight(&dst, nbits));
        const expected_and_tail: bitmap.Word = if ((idx & 1) == 0) 0b1111 else 0b1011;
        checksum +%= @popCount(dst[1] ^ expected_and_tail);

        checksum +%= @as(u64, @intFromBool(bitmap.andNotBits(&dst, &lhs, &rhs, nbits)));
        checksum +%= @intCast(bitmap.weight(&dst, nbits));
        checksum +%= @popCount(dst[1]);

        bitmap.xorBits(&dst, &lhs, &rhs, nbits);
        checksum +%= @intCast(bitmap.weight(&dst, nbits));
        checksum +%= @as(u64, @intFromBool(bitmap.intersects(&lhs, &rhs, nbits)));
        checksum +%= @as(u64, @intFromBool(bitmap.subset(&rhs, &dst, nbits)));
    }

    return .{ .checksum = checksum };
}

fn bitmapCopyBench() struct { checksum: u64 } {
    const full_nbits = bitmap.bits_per_long * 3;
    const aligned_copy_nbits = bitmap.bits_per_long + 33;
    const partial_tail_nbits = bitmap.bits_per_long + 45;
    const extend_partial_count = bitmap.bits_per_long + 5;
    const extend_full_count = bitmap.bits_per_long * 2;

    var sparse_src = [_]bitmap.Word{0} ** bitmap.bitsToWords(full_nbits);
    var dense_src = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
        0,
    };
    const extend_sparse_src = [_]bitmap.Word{ ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0), ~@as(bitmap.Word, 0) };
    const extend_dense_src = [_]bitmap.Word{ 0x55aa, 0xaa55, ~@as(bitmap.Word, 0) };
    var dst = [_]bitmap.Word{0} ** bitmap.bitsToWords(full_nbits);

    bitmap.setRange(&sparse_src, 0, 109);
    dense_src[2] = 0;

    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_bitmap_copy) : (idx += 1) {
        bitmap.fill(&dst, full_nbits);
        bitmap.copy(&dst, &sparse_src, aligned_copy_nbits);
        checksum +%= @intCast(bitmap.weight(&dst, full_nbits));
        checksum +%= @intCast(find_bit.findFirstZeroBit(&dst, full_nbits));

        bitmap.fill(&dst, full_nbits);
        bitmap.copy(&dst, &dense_src, partial_tail_nbits);
        checksum +%= @intCast(bitmap.weight(&dst, full_nbits));
        checksum +%= @intCast(find_bit.findFirstZeroBit(&dst, full_nbits));

        bitmap.fill(&dst, full_nbits);
        bitmap.copyClearTail(&dst, &dense_src, partial_tail_nbits);
        checksum +%= @intCast(bitmap.weight(&dst, full_nbits));
        checksum +%= @intCast(find_bit.findFirstZeroBit(&dst, full_nbits));
        checksum +%= @popCount(dst[1] ^ bitmap.lastWordMask(partial_tail_nbits));

        bitmap.copyAndExtend(&dst, &extend_sparse_src, extend_partial_count, full_nbits);
        checksum +%= @intCast(bitmap.weight(&dst, full_nbits));
        checksum +%= @intCast(find_bit.findFirstZeroBit(&dst, full_nbits));
        checksum +%= @popCount(dst[1] ^ bitmap.lastWordMask(extend_partial_count));
        checksum +%= @popCount(dst[2]);

        bitmap.fill(&dst, full_nbits);
        bitmap.copyAndExtend(&dst, &extend_dense_src, extend_full_count, full_nbits);
        checksum +%= @intCast(bitmap.weight(&dst, full_nbits));
        checksum +%= @intCast(find_bit.findFirstZeroBit(&dst, full_nbits));
        checksum +%= @popCount(dst[2]);
    }

    return .{ .checksum = checksum };
}

fn bitmapScnprintfBench() struct { checksum: u64 } {
    const nbits = 32;
    var map = [_]bitmap.Word{0} ** bitmap.bitsToWords(nbits);
    var full_buffer: [32]u8 = undefined;
    var trunc_buffer: [6]u8 = undefined;
    var empty_buffer = [_]u8{0xcc} ** 4;

    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_bitmap_scnprintf) : (idx += 1) {
        bitmap.zero(&map, nbits);

        empty_buffer = [_]u8{0xcc} ** 4;
        const empty_len = bitmap.scnprintf(&map, nbits, &empty_buffer);
        checksum +%= empty_len;
        for (empty_buffer) |byte| {
            checksum +%= byte;
        }

        bitmap.setRange(&map, idx & 1, 3);
        bitmap.setRange(&map, 7, 1);
        if ((idx & 2) == 0) {
            bitmap.setRange(&map, 10, 2);
        } else {
            bitmap.setRange(&map, 12, 4);
        }

        const full_len = bitmap.scnprintf(&map, nbits, &full_buffer);
        checksum +%= full_len;
        checksum +%= full_buffer[0];
        checksum +%= full_buffer[full_len - 1];
        checksum +%= full_buffer[full_len];

        const trunc_len = bitmap.scnprintf(&map, nbits, &trunc_buffer);
        checksum +%= trunc_len;
        checksum +%= trunc_buffer[0];
        checksum +%= trunc_buffer[trunc_len];
    }

    return .{ .checksum = checksum };
}

fn findBitBench() struct { next_checksum: u64, family_checksum: u64, tail_window_checksum: u64, same_word_checksum: u64 } {
    var map = [_]find_bit.Word{0} ** find_bit.bitsToWords(4096);
    map[0] |= (@as(find_bit.Word, 1) << 3);
    map[7] |= (@as(find_bit.Word, 1) << 9);
    map[15] |= (@as(find_bit.Word, 1) << 17);
    map[31] |= (@as(find_bit.Word, 1) << 1);

    const tail_nbits = find_bit.bits_per_long + 5;
    const full = ~@as(find_bit.Word, 0);
    var zero_map = [_]find_bit.Word{ full, full };
    zero_map[0] &= ~(@as(find_bit.Word, 1) << 6);
    zero_map[1] &= ~(@as(find_bit.Word, 1) << 4);

    const and_lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 9),
        (@as(find_bit.Word, 1) << 2),
    };
    const and_rhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 9),
        (@as(find_bit.Word, 1) << 2),
    };

    const same_word_nbits = find_bit.bits_per_long + 6;
    const same_word_set = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 6),
        @as(find_bit.Word, 1) << 4,
    };
    var same_word_zero = [_]find_bit.Word{ full, full };
    same_word_zero[0] &= ~(@as(find_bit.Word, 1) << 1);
    same_word_zero[0] &= ~(@as(find_bit.Word, 1) << 6);
    same_word_zero[1] &= ~(@as(find_bit.Word, 1) << 4);
    const same_word_and_lhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 6),
        @as(find_bit.Word, 1) << 4,
    };
    const same_word_and_rhs = [_]find_bit.Word{
        (@as(find_bit.Word, 1) << 6) | (@as(find_bit.Word, 1) << 9),
        @as(find_bit.Word, 1) << 4,
    };
    const same_word_set_starts = [_]usize{ 1, 2, 7, find_bit.bits_per_long + 5 };
    const same_word_and_starts = [_]usize{ 2, 6, 7, find_bit.bits_per_long + 5 };

    var tail_set = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 10) };
    var tail_zero = [_]find_bit.Word{ full, find_bit.lastWordMask(tail_nbits) };
    const tail_and_lhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9),
    };
    const tail_and_rhs = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 12),
    };

    var next_checksum: u64 = 0;
    var family_checksum: u64 = 0;
    var tail_window_checksum: u64 = 0;
    var same_word_checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_find_bit) : (idx += 1) {
        const start = idx % 1024;
        next_checksum +%= @intCast(find_bit.findNextBit(&map, 4096, start));

        family_checksum +%= @intCast(find_bit.findFirstBit(&map, 4096));
        family_checksum +%= @intCast(find_bit.findNextBit(&map, 4096, start));
        family_checksum +%= @intCast(find_bit.findFirstZeroBit(&zero_map, find_bit.bits_per_long * zero_map.len));
        family_checksum +%= @intCast(find_bit.findNextZeroBit(&zero_map, find_bit.bits_per_long * zero_map.len, (idx % 9) + 1));
        family_checksum +%= @intCast(find_bit.findFirstAndBit(&and_lhs, &and_rhs, find_bit.bits_per_long * and_lhs.len));
        family_checksum +%= @intCast(find_bit.findNextAndBit(&tail_and_lhs, &tail_and_rhs, tail_nbits, find_bit.bits_per_long + (idx % 5)));

        if ((idx & 1) == 0) {
            tail_set[1] |= @as(find_bit.Word, 1) << 3;
            tail_zero[1] &= ~(@as(find_bit.Word, 1) << 2);
        } else {
            tail_set[1] &= ~(@as(find_bit.Word, 1) << 3);
            tail_zero[1] |= @as(find_bit.Word, 1) << 2;
        }

        tail_window_checksum +%= @intCast(find_bit.findFirstBit(&tail_set, tail_nbits));
        tail_window_checksum +%= @intCast(find_bit.findNextBit(&tail_set, tail_nbits, find_bit.bits_per_long + (idx % 5)));
        tail_window_checksum +%= @intCast(find_bit.findFirstZeroBit(&tail_zero, tail_nbits));
        tail_window_checksum +%= @intCast(find_bit.findNextZeroBit(&tail_zero, tail_nbits, find_bit.bits_per_long + (idx % 5)));
        tail_window_checksum +%= @intCast(find_bit.findFirstAndBit(&tail_and_lhs, &tail_and_rhs, tail_nbits));
        tail_window_checksum +%= @intCast(find_bit.findNextAndBit(&tail_and_lhs, &tail_and_rhs, tail_nbits, find_bit.bits_per_long + (idx % 5)));

        if (idx < iterations_find_bit_same_word) {
            same_word_checksum +%= @intCast(find_bit.findNextBit(&same_word_set, same_word_nbits, same_word_set_starts[idx % same_word_set_starts.len]));
            same_word_checksum +%= @intCast(find_bit.findNextZeroBit(&same_word_zero, same_word_nbits, same_word_set_starts[idx % same_word_set_starts.len]));
            same_word_checksum +%= @intCast(find_bit.findNextAndBit(&same_word_and_lhs, &same_word_and_rhs, same_word_nbits, same_word_and_starts[idx % same_word_and_starts.len]));
        }
    }

    return .{
        .next_checksum = next_checksum,
        .family_checksum = family_checksum,
        .tail_window_checksum = tail_window_checksum,
        .same_word_checksum = same_word_checksum,
    };
}

fn findZeroBitBench() struct { checksum: u64 } {
    const nbits = find_bit.bits_per_long * 4 + 11;
    var map = [_]find_bit.Word{~@as(find_bit.Word, 0)} ** find_bit.bitsToWords(nbits);
    map[0] &= ~(@as(find_bit.Word, 1) << 2);
    map[1] &= ~(@as(find_bit.Word, 1) << 7);
    map[2] &= ~(@as(find_bit.Word, 1) << 5);
    map[4] &= ~(@as(find_bit.Word, 1) << 3);
    map[4] &= ~(@as(find_bit.Word, 1) << 9);

    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_find_zero_bit) : (idx += 1) {
        checksum +%= @intCast(find_bit.findNextZeroBit(&map, nbits, idx % (find_bit.bits_per_long * 2)));
    }

    return .{ .checksum = checksum };
}

fn findAndBitBench() struct { checksum: u64 } {
    const nbits = find_bit.bits_per_long * 4 + 9;
    var lhs = [_]find_bit.Word{0} ** find_bit.bitsToWords(nbits);
    var rhs = [_]find_bit.Word{0} ** find_bit.bitsToWords(nbits);

    lhs[0] |= (@as(find_bit.Word, 1) << 4) | (@as(find_bit.Word, 1) << 11);
    rhs[0] |= (@as(find_bit.Word, 1) << 11);
    lhs[1] |= (@as(find_bit.Word, 1) << 6);
    rhs[1] |= (@as(find_bit.Word, 1) << 6);
    lhs[2] |= (@as(find_bit.Word, 1) << 10);
    rhs[2] |= (@as(find_bit.Word, 1) << 10);
    lhs[4] |= (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 6);
    rhs[4] |= (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 8);

    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_find_and_bit) : (idx += 1) {
        checksum +%= @intCast(find_bit.findNextAndBit(&lhs, &rhs, nbits, idx % (find_bit.bits_per_long * 2 + 5)));
    }

    return .{ .checksum = checksum };
}

fn stringBench() !struct {
    checksum: u64,
    bool_trim_checksum: u64,
    memchr_checksum: u64,
    compare_checksum: u64,
    memparse_checksum: u64,
} {
    var aligned = [_]u8{'a'} ** 24;
    aligned[17] = 'X';

    var misaligned_storage = [_]u8{'a'} ** 25;
    misaligned_storage[18] = 'X';

    var prefix_storage = [_]u8{'a'} ** 25;
    prefix_storage[3] = 'X';

    var trailing_storage = [_]u8{'a'} ** 26;
    trailing_storage[25] = 'X';

    const embedded_source = [_]u8{ 'z', 'i', 'g', 0, 'x' };
    const embedded_prefix = [_]u8{ 'z', 'i', 'g', 0, 'u', 'x' };
    const embedded_suffix = [_]u8{ 'i', 'g', 0, 'u', 'x' };
    const embedded_eq = [_]u8{ 'z', 'i', 'g', 0, 'u', 'x' };

    var checksum: u64 = 0;
    var bool_trim_checksum: u64 = 0;
    var memchr_checksum: u64 = 0;
    var compare_checksum: u64 = 0;
    var memparse_checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_string) : (idx += 1) {
        const enabled = try string.strtobool(if ((idx & 1) == 0) "on" else "0");
        var trim_buf = [_]u8{ ' ', '\t', 'h', 'i', ' ', '\n' };
        const trimmed = string.trimSpaces(&trim_buf);
        const aligned_idx = string.memchrInv(&aligned, 'a').?;
        const misaligned_idx = string.memchrInv(misaligned_storage[1..], 'a').?;
        const prefix_idx = string.memchrInv(prefix_storage[1..], 'a').?;
        const trailing_idx = string.memchrInv(trailing_storage[1..], 'a').?;

        checksum +%= @as(u64, @intFromBool(enabled));
        checksum +%= @intCast(trimmed.len);
        checksum +%= aligned_idx;
        checksum +%= misaligned_idx;
        checksum +%= prefix_idx;
        checksum +%= trailing_idx;

        const skipped = string.skipSpaces("   hello");
        var remove_buf = [_]u8{ 'a', ' ', 'b', 0, ' ', 'x' };
        const removed = string.removeSpaces(&remove_buf);
        var replace_buf = [_]u8{ 'a', '-', 'b', 0, '-' };
        const replace_end = @intFromPtr(string.strreplace(replace_buf[0 .. replace_buf.len - 1], '-', '_')) - @intFromPtr(replace_buf[0..].ptr);

        bool_trim_checksum +%= @as(u64, @intFromBool(enabled));
        bool_trim_checksum +%= @intCast(trimmed.len + skipped.len + removed.len + replace_end);

        memchr_checksum +%= aligned_idx;
        memchr_checksum +%= misaligned_idx;
        memchr_checksum +%= prefix_idx;
        memchr_checksum +%= trailing_idx;

        compare_checksum +%= @as(u64, @intFromBool(string.streq("zigux", "zigux")));
        compare_checksum +%= @as(u64, @intFromBool(string.streq(&embedded_source, &embedded_eq)));
        compare_checksum +%= @as(u64, @intFromBool(string.strstarts("zigux", "zig")));
        compare_checksum +%= @intCast(string.str_has_prefix("zigux", "zig"));
        compare_checksum +%= @as(u64, @intFromBool(string.strends("zigux", "gux")));
        compare_checksum +%= @as(u64, @intFromBool(string.strstarts(&embedded_source, &embedded_prefix)));
        compare_checksum +%= @as(u64, @intFromBool(string.strends(&embedded_source, &embedded_suffix)));

        const parsed = switch (idx % 3) {
            0 => string.memparse("64KiB rest"),
            1 => string.memparse("0x20M"),
            else => string.memparse("xyz"),
        };
        memparse_checksum +%= parsed.value >> 10;
        memparse_checksum +%= parsed.rest.len;
    }

    return .{
        .checksum = checksum,
        .bool_trim_checksum = bool_trim_checksum,
        .memchr_checksum = memchr_checksum,
        .compare_checksum = compare_checksum,
        .memparse_checksum = memparse_checksum,
    };
}

fn hweightBench() struct { checksum: u64 } {
    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_hweight) : (idx += 1) {
        const value: u32 = @truncate(0xf0f0_a5a5 ^ @as(u32, @intCast(idx)));
        checksum +%= hweight.swHweight32(value);
    }

    return .{ .checksum = checksum };
}

fn listSortBench() struct { checksum: u64 } {
    const cmp = struct {
        fn compare(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const Entry = @fieldParentPtr("node", a);
            const rhs: *const Entry = @fieldParentPtr("node", b);
            if (lhs.key < rhs.key) return -1;
            if (lhs.key > rhs.key) return 1;
            return 0;
        }
    }.compare;

    var checksum: u64 = 0;
    var iter: usize = 0;
    while (iter < iterations_list_sort) : (iter += 1) {
        var head: list_sort.ListHead = .{};
        head.init();
        var entries: [128]Entry = undefined;
        for (&entries, 0..) |*entry, idx| {
            entry.* = .{
                .key = @intCast((127 - idx) % 11),
                .ordinal = idx,
            };
            list_sort.listAddTail(&entry.node, &head);
        }
        list_sort.listSort(null, &head, cmp);

        var current = head.next;
        while (current != &head) : (current = current.?.next) {
            const entry: *const Entry = @fieldParentPtr("node", current.?);
            checksum +%= @intCast(entry.key + @as(i32, @intCast(entry.ordinal & 1)));
        }
    }

    return .{ .checksum = checksum };
}

fn rbtreeBench() struct {
    checksum: u64,
    duplicate_checksum: u64,
    cached_checksum: u64,
    find_add_checksum: u64,
    postorder_safe_checksum: u64,
} {
    const RbEntry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };
    const RbDuplicateEntry = struct {
        key: i32,
        serial: usize,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const RbEntry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const RbEntry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;
    const duplicateLess = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const RbDuplicateEntry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const RbDuplicateEntry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;
    const cmpKey = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const RbDuplicateEntry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;
    const cmpNode = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const RbDuplicateEntry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const RbDuplicateEntry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    var checksum: u64 = 0;
    var duplicate_checksum: u64 = 0;
    var cached_checksum: u64 = 0;
    var find_add_checksum: u64 = 0;
    var postorder_safe_checksum: u64 = 0;
    var iter: usize = 0;
    while (iter < iterations_rbtree) : (iter += 1) {
        var entries = [_]RbEntry{
            .{ .key = 10 },
            .{ .key = 20 },
            .{ .key = 5 },
            .{ .key = 15 },
            .{ .key = 25 },
        };
        var replacement = RbEntry{ .key = 10 };
        var root = rbtree.Root.init();

        for (&entries) |*entry| {
            rbtree.add(&entry.node, &root, less);
        }

        var current = rbtree.first(&root);
        while (current) |node| : (current = rbtree.next(node)) {
            const entry: *const RbEntry = @fieldParentPtr("node", node);
            checksum +%= @intCast(entry.key + 31);
        }

        rbtree.erase(&entries[1].node, &root);
        rbtree.replaceNode(&entries[0].node, &replacement.node, &root);
        rbtree.eraseInit(&replacement.node, &root);
        checksum +%= @as(u64, @intFromBool(rbtree.emptyNode(&replacement.node)));

        current = rbtree.firstPostorder(&root);
        while (current) |node| : (current = rbtree.nextPostorder(node)) {
            const entry: *const RbEntry = @fieldParentPtr("node", node);
            checksum +%= @intCast(entry.key + 17);
        }

        var safe_entries = [_]RbEntry{
            .{ .key = 2 },
            .{ .key = 1 },
            .{ .key = 4 },
            .{ .key = 3 },
        };
        var safe_root = rbtree.Root.init();
        for (&safe_entries) |*entry| {
            rbtree.add(&entry.node, &safe_root, less);
        }
        var safe_iterator = rbtree.iteratePostorderSafe(&safe_root);
        while (safe_iterator.next()) |node| {
            const entry: *const RbEntry = @fieldParentPtr("node", node);
            postorder_safe_checksum +%= @intCast(entry.key + 89);
            rbtree.clearNode(node);
            postorder_safe_checksum +%= @intFromBool(rbtree.emptyNode(node));
        }
        postorder_safe_checksum +%= @intFromBool(safe_iterator.next() == null);

        var duplicate_entries = [_]RbDuplicateEntry{
            .{ .key = 10, .serial = 0 },
            .{ .key = 5, .serial = 1 },
            .{ .key = 10, .serial = 2 },
            .{ .key = 20, .serial = 3 },
            .{ .key = 10, .serial = 4 },
            .{ .key = 15, .serial = 5 },
        };
        var duplicate_root = rbtree.Root.init();
        for (&duplicate_entries) |*entry| {
            rbtree.add(&entry.node, &duplicate_root, duplicateLess);
        }

        const wanted = @as(i32, 10);
        var forward_matches = rbtree.iterateMatches(&wanted, &duplicate_root, cmpKey);
        while (forward_matches.next()) |node| {
            const entry: *const RbDuplicateEntry = @fieldParentPtr("node", node);
            duplicate_checksum +%= entry.serial + 41;
        }
        var reverse_matches = rbtree.iterateMatchesReverse(&wanted, &duplicate_root, cmpKey);
        while (reverse_matches.next()) |node| {
            const entry: *const RbDuplicateEntry = @fieldParentPtr("node", node);
            duplicate_checksum +%= entry.serial + 53;
        }
        duplicate_checksum +%= @intFromBool(rbtree.find(&wanted, &duplicate_root, cmpKey) != null);
        duplicate_checksum +%= @intFromBool(rbtree.findFirst(&wanted, &duplicate_root, cmpKey) != null);
        duplicate_checksum +%= @intFromBool(rbtree.findLast(&wanted, &duplicate_root, cmpKey) != null);

        var cached_entries = [_]RbDuplicateEntry{
            .{ .key = 5, .serial = 0 },
            .{ .key = 10, .serial = 1 },
            .{ .key = 5, .serial = 2 },
            .{ .key = 15, .serial = 3 },
        };
        var cached_replacement = RbDuplicateEntry{ .key = 12, .serial = 4 };
        var cached_root = rbtree.RootCached.init();
        for (&cached_entries) |*entry| {
            _ = rbtree.addCached(&entry.node, &cached_root, duplicateLess);
            const leftmost_entry: *const RbDuplicateEntry = @fieldParentPtr("node", rbtree.firstCached(&cached_root).?);
            cached_checksum +%= @intCast(leftmost_entry.key + @as(i32, @intCast(leftmost_entry.serial)));
        }

        rbtree.eraseCached(&cached_entries[0].node, &cached_root);
        const after_first_erase: *const RbDuplicateEntry = @fieldParentPtr("node", rbtree.firstCached(&cached_root).?);
        cached_checksum +%= @intCast(after_first_erase.key + @as(i32, @intCast(after_first_erase.serial)));

        rbtree.eraseCached(&cached_entries[2].node, &cached_root);
        const after_second_erase: *const RbDuplicateEntry = @fieldParentPtr("node", rbtree.firstCached(&cached_root).?);
        cached_checksum +%= @intCast(after_second_erase.key + @as(i32, @intCast(after_second_erase.serial)));

        rbtree.replaceNodeCached(&cached_entries[3].node, &cached_replacement.node, &cached_root);
        const after_replace: *const RbDuplicateEntry = @fieldParentPtr("node", rbtree.firstCached(&cached_root).?);
        cached_checksum +%= @intCast(after_replace.key + @as(i32, @intCast(after_replace.serial)));

        var find_add_entries = [_]RbDuplicateEntry{
            .{ .key = 10, .serial = 0 },
            .{ .key = 20, .serial = 1 },
            .{ .key = 5, .serial = 2 },
            .{ .key = 10, .serial = 3 },
            .{ .key = 3, .serial = 4 },
        };
        var find_add_root = rbtree.Root.init();
        for (find_add_entries[0..3]) |*entry| {
            find_add_checksum +%= @intFromBool(rbtree.findAdd(&entry.node, &find_add_root, cmpNode) == null);
        }
        const duplicate_existing = rbtree.findAdd(&find_add_entries[3].node, &find_add_root, cmpNode) orelse unreachable;
        const duplicate_existing_entry: *const RbDuplicateEntry = @fieldParentPtr("node", duplicate_existing);
        find_add_checksum +%= duplicate_existing_entry.serial + 61;
        find_add_checksum +%= @intFromBool(rbtree.findAdd(&find_add_entries[4].node, &find_add_root, cmpNode) == null);
        var find_add_current = rbtree.first(&find_add_root);
        while (find_add_current) |node| : (find_add_current = rbtree.next(node)) {
            const entry: *const RbDuplicateEntry = @fieldParentPtr("node", node);
            find_add_checksum +%= entry.serial + @as(u64, @intCast(entry.key + 67));
        }

        var find_add_cached_entries = [_]RbDuplicateEntry{
            .{ .key = 10, .serial = 0 },
            .{ .key = 20, .serial = 1 },
            .{ .key = 5, .serial = 2 },
            .{ .key = 10, .serial = 3 },
            .{ .key = 3, .serial = 4 },
        };
        var find_add_cached_root = rbtree.RootCached.init();
        for (find_add_cached_entries[0..3]) |*entry| {
            find_add_checksum +%= @intFromBool(rbtree.findAddCached(&entry.node, &find_add_cached_root, cmpNode) == null);
            const leftmost_entry: *const RbDuplicateEntry = @fieldParentPtr("node", rbtree.firstCached(&find_add_cached_root).?);
            find_add_checksum +%= leftmost_entry.serial + @as(u64, @intCast(leftmost_entry.key + 71));
        }
        const cached_existing = rbtree.findAddCached(&find_add_cached_entries[3].node, &find_add_cached_root, cmpNode) orelse unreachable;
        const cached_existing_entry: *const RbDuplicateEntry = @fieldParentPtr("node", cached_existing);
        find_add_checksum +%= cached_existing_entry.serial + 73;
        const cached_leftmost_before_new: *const RbDuplicateEntry = @fieldParentPtr("node", rbtree.firstCached(&find_add_cached_root).?);
        find_add_checksum +%= cached_leftmost_before_new.serial + @as(u64, @intCast(cached_leftmost_before_new.key + 79));
        find_add_checksum +%= @intFromBool(rbtree.findAddCached(&find_add_cached_entries[4].node, &find_add_cached_root, cmpNode) == null);
        const cached_leftmost_after_new: *const RbDuplicateEntry = @fieldParentPtr("node", rbtree.firstCached(&find_add_cached_root).?);
        find_add_checksum +%= cached_leftmost_after_new.serial + @as(u64, @intCast(cached_leftmost_after_new.key + 83));
    }

    return .{
        .checksum = checksum,
        .duplicate_checksum = duplicate_checksum,
        .cached_checksum = cached_checksum,
        .find_add_checksum = find_add_checksum,
        .postorder_safe_checksum = postorder_safe_checksum,
    };
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var stdout_buffer: [2048]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);

    const bitmap_result = bitmapBench();
    const bitmap_window_result = bitmapWindowBench();
    const bitmap_copy_result = bitmapCopyBench();
    const bitmap_scnprintf_result = bitmapScnprintfBench();
    const find_bit_result = findBitBench();
    const find_zero_bit_result = findZeroBitBench();
    const find_and_bit_result = findAndBitBench();
    const string_result = try stringBench();
    const hweight_result = hweightBench();
    const list_sort_result = listSortBench();
    const rbtree_result = rbtreeBench();

    std.debug.assert(bitmap_result.checksum != 0);
    std.debug.assert(bitmap_window_result.checksum != 0);
    std.debug.assert(bitmap_copy_result.checksum != 0);
    std.debug.assert(bitmap_scnprintf_result.checksum != 0);
    std.debug.assert(find_bit_result.next_checksum != 0);
    std.debug.assert(find_bit_result.family_checksum != 0);
    std.debug.assert(find_bit_result.tail_window_checksum != 0);
    std.debug.assert(find_bit_result.same_word_checksum != 0);
    std.debug.assert(find_zero_bit_result.checksum != 0);
    std.debug.assert(find_and_bit_result.checksum != 0);
    std.debug.assert(string_result.checksum != 0);
    std.debug.assert(string_result.bool_trim_checksum != 0);
    std.debug.assert(string_result.memchr_checksum != 0);
    std.debug.assert(string_result.compare_checksum != 0);
    std.debug.assert(string_result.memparse_checksum != 0);
    std.debug.assert(hweight_result.checksum != 0);
    std.debug.assert(list_sort_result.checksum != 0);
    std.debug.assert(rbtree_result.checksum != 0);
    std.debug.assert(rbtree_result.duplicate_checksum != 0);
    std.debug.assert(rbtree_result.cached_checksum != 0);
    std.debug.assert(rbtree_result.find_add_checksum != 0);
    std.debug.assert(rbtree_result.postorder_safe_checksum != 0);

    try stdout_writer.interface.print("PHASE1_BENCH=pass\n", .{});
    try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS={d}\n", .{iterations_bitmap});
    try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM={d}\n", .{bitmap_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS={d}\n", .{iterations_bitmap_window});
    try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM={d}\n", .{bitmap_window_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_COPY_ITERATIONS={d}\n", .{iterations_bitmap_copy});
    try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_COPY_CHECKSUM={d}\n", .{bitmap_copy_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_SCNPRINTF_ITERATIONS={d}\n", .{iterations_bitmap_scnprintf});
    try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_SCNPRINTF_CHECKSUM={d}\n", .{bitmap_scnprintf_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS={d}\n", .{iterations_find_bit});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM={d}\n", .{find_bit_result.next_checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_FAMILY_CHECKSUM={d}\n", .{find_bit_result.family_checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_TAIL_WINDOW_CHECKSUM={d}\n", .{find_bit_result.tail_window_checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_SAME_WORD_ITERATIONS={d}\n", .{iterations_find_bit_same_word});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_SAME_WORD_CHECKSUM={d}\n", .{find_bit_result.same_word_checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_ZERO_BIT_ITERATIONS={d}\n", .{iterations_find_zero_bit});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_ZERO_BIT_CHECKSUM={d}\n", .{find_zero_bit_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_AND_BIT_ITERATIONS={d}\n", .{iterations_find_and_bit});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_AND_BIT_CHECKSUM={d}\n", .{find_and_bit_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_STRING_ITERATIONS={d}\n", .{iterations_string});
    try stdout_writer.interface.print("PHASE1_BENCH_STRING_CHECKSUM={d}\n", .{string_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_STRING_BOOL_TRIM_CHECKSUM={d}\n", .{string_result.bool_trim_checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_STRING_MEMCHR_CHECKSUM={d}\n", .{string_result.memchr_checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_STRING_COMPARE_CHECKSUM={d}\n", .{string_result.compare_checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_STRING_MEMPARSE_CHECKSUM={d}\n", .{string_result.memparse_checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_HWEIGHT_ITERATIONS={d}\n", .{iterations_hweight});
    try stdout_writer.interface.print("PHASE1_BENCH_HWEIGHT_CHECKSUM={d}\n", .{hweight_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_LIST_SORT_ITERATIONS={d}\n", .{iterations_list_sort});
    try stdout_writer.interface.print("PHASE1_BENCH_LIST_SORT_CHECKSUM={d}\n", .{list_sort_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_ITERATIONS={d}\n", .{iterations_rbtree});
    try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CHECKSUM={d}\n", .{rbtree_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM={d}\n", .{rbtree_result.duplicate_checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\n", .{rbtree_result.cached_checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM={d}\n", .{rbtree_result.find_add_checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM={d}\n", .{rbtree_result.postorder_safe_checksum});
    try stdout_writer.interface.flush();
}
