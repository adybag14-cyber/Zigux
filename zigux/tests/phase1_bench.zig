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

        checksum +%= @as(u64, @intFromBool(bitmap.andNotBits(&dst, &lhs, &rhs, nbits)));
        checksum +%= @intCast(bitmap.weight(&dst, nbits));

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

    var sparse_src = [_]bitmap.Word{0} ** bitmap.bitsToWords(full_nbits);
    var dense_src = [_]bitmap.Word{
        ~@as(bitmap.Word, 0),
        ~@as(bitmap.Word, 0),
        0,
    };
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

fn stringBench() !struct { checksum: u64 } {
    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_string) : (idx += 1) {
        const enabled = try string.strtobool(if ((idx & 1) == 0) "on" else "0");
        var trim_buf = [_]u8{ ' ', '\t', 'h', 'i', ' ', '\n' };
        const trimmed = string.trimSpaces(&trim_buf);
        checksum +%= @as(u64, @intFromBool(enabled));
        checksum +%= @intCast(trimmed.len);
    }

    return .{ .checksum = checksum };
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

fn rbtreeBench() struct { checksum: u64 } {
    const RbEntry = struct {
        key: i32,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const RbEntry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const RbEntry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    var checksum: u64 = 0;
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
    }

    return .{ .checksum = checksum };
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
    std.debug.assert(hweight_result.checksum != 0);
    std.debug.assert(list_sort_result.checksum != 0);
    std.debug.assert(rbtree_result.checksum != 0);

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
    try stdout_writer.interface.print("PHASE1_BENCH_HWEIGHT_ITERATIONS={d}\n", .{iterations_hweight});
    try stdout_writer.interface.print("PHASE1_BENCH_HWEIGHT_CHECKSUM={d}\n", .{hweight_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_LIST_SORT_ITERATIONS={d}\n", .{iterations_list_sort});
    try stdout_writer.interface.print("PHASE1_BENCH_LIST_SORT_CHECKSUM={d}\n", .{list_sort_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_ITERATIONS={d}\n", .{iterations_rbtree});
    try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CHECKSUM={d}\n", .{rbtree_result.checksum});
    try stdout_writer.interface.flush();
}
