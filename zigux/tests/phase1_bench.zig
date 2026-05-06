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
const iterations_find_bit = 20_000;
const iterations_find_bit_edge = 20_000;
const iterations_string = 40_000;
const iterations_hweight = 100_000;
const iterations_list_sort = 1_000;
const iterations_rbtree = 4_000;

fn bitmapBench() struct { checksum: u64 } {
    var map = std.mem.zeroes([bitmap.bitsToWords(4096)]bitmap.Word);
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
    var lhs = std.mem.zeroes([bitmap.bitsToWords(nbits)]bitmap.Word);
    var rhs = std.mem.zeroes([bitmap.bitsToWords(nbits)]bitmap.Word);
    var dst = std.mem.zeroes([bitmap.bitsToWords(nbits)]bitmap.Word);

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

fn findBitBench() struct { checksum: u64 } {
    var map = std.mem.zeroes([find_bit.bitsToWords(4096)]find_bit.Word);
    map[0] |= (@as(find_bit.Word, 1) << 3);
    map[7] |= (@as(find_bit.Word, 1) << 9);
    map[15] |= (@as(find_bit.Word, 1) << 17);
    map[31] |= (@as(find_bit.Word, 1) << 1);

    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_find_bit) : (idx += 1) {
        checksum +%= @intCast(find_bit.findNextBit(&map, 4096, idx % 1024));
    }

    return .{ .checksum = checksum };
}

fn findBitEdgeBench() struct { checksum: u64 } {
    const boundary = find_bit.bits_per_long - 1;
    const head_nbits = find_bit.bits_per_long * 2;
    const tail_nbits = find_bit.bits_per_long + 5;
    const boundary_set = [_]find_bit.Word{(@as(find_bit.Word, 1) << @intCast(boundary)), 0};
    const boundary_zero = [_]find_bit.Word{~(@as(find_bit.Word, 1) << @intCast(boundary)), ~@as(find_bit.Word, 0)};
    const tail_set = [_]find_bit.Word{0, @as(find_bit.Word, 1) << 3};
    const tail_full = [_]find_bit.Word{~@as(find_bit.Word, 0), find_bit.lastWordMask(tail_nbits)};

    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_find_bit_edge) : (idx += 1) {
        checksum +%= @intCast(find_bit.findNextBit(&boundary_set, head_nbits, boundary));
        checksum +%= @intCast(find_bit.findNextAndBit(&boundary_set, &boundary_set, head_nbits, boundary));
        checksum +%= @intCast(find_bit.findNextZeroBit(&boundary_zero, head_nbits, boundary));
        checksum +%= @intCast(find_bit.findFirstBit(&tail_set, tail_nbits));
        checksum +%= @intCast(find_bit.findNextBit(&tail_set, tail_nbits, find_bit.bits_per_long + 4));
        checksum +%= @intCast(find_bit.findFirstZeroBit(&tail_full, tail_nbits));
        checksum +%= @intCast(find_bit.findNextZeroBit(&tail_full, tail_nbits, find_bit.bits_per_long));
        checksum +%= @intCast(find_bit.findFirstAndBit(&tail_set, &tail_set, tail_nbits));
        checksum +%= @intCast(find_bit.findNextAndBit(&tail_set, &tail_set, tail_nbits, find_bit.bits_per_long + 4));
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
    const find_bit_result = findBitBench();
    const find_bit_edge_result = findBitEdgeBench();
    const string_result = try stringBench();
    const hweight_result = hweightBench();
    const list_sort_result = listSortBench();
    const rbtree_result = rbtreeBench();

    std.debug.assert(bitmap_result.checksum != 0);
    std.debug.assert(bitmap_window_result.checksum != 0);
    std.debug.assert(find_bit_result.checksum != 0);
    std.debug.assert(find_bit_edge_result.checksum != 0);
    std.debug.assert(string_result.checksum != 0);
    std.debug.assert(hweight_result.checksum != 0);
    std.debug.assert(list_sort_result.checksum != 0);
    std.debug.assert(rbtree_result.checksum != 0);

    try stdout_writer.interface.print("PHASE1_BENCH=pass\n", .{});
    try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS={d}\n", .{iterations_bitmap});
    try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM={d}\n", .{bitmap_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS={d}\n", .{iterations_bitmap_window});
    try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM={d}\n", .{bitmap_window_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS={d}\n", .{iterations_find_bit});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM={d}\n", .{find_bit_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS={d}\n", .{iterations_find_bit_edge});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}\n", .{find_bit_edge_result.checksum});
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
