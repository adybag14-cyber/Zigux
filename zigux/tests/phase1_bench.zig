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

const RbtreeBench = struct {
    checksum: u64,
    postorder_safe_checksum: u64,
    find_add_checksum: u64,
    duplicate_checksum: u64,
    cached_checksum: u64,
};

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

        bitmap.__bitmap_or(&dst, &lhs, &rhs, nbits);
        checksum +%= @intCast(bitmap.__bitmap_weight(&dst, nbits));

        checksum +%= @as(u64, @intFromBool(bitmap.__bitmap_and(&dst, &lhs, &rhs, nbits)));
        checksum +%= @intCast(bitmap.__bitmap_weight(&dst, nbits));

        checksum +%= @as(u64, @intFromBool(bitmap.__bitmap_andnot(&dst, &lhs, &rhs, nbits)));
        checksum +%= @intCast(bitmap.__bitmap_weight(&dst, nbits));

        bitmap.__bitmap_xor(&dst, &lhs, &rhs, nbits);
        checksum +%= @intCast(bitmap.__bitmap_weight(&dst, nbits));
        checksum +%= @as(u64, @intFromBool(bitmap.__bitmap_intersects(&lhs, &rhs, nbits)));
        checksum +%= @as(u64, @intFromBool(bitmap.__bitmap_subset(&rhs, &dst, nbits)));
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
    const past_nbits = 7;
    const boundary_set = [_]find_bit.Word{(@as(find_bit.Word, 1) << @intCast(boundary)), 0};
    const boundary_zero = [_]find_bit.Word{~(@as(find_bit.Word, 1) << @intCast(boundary)), ~@as(find_bit.Word, 0)};
    const tail_set = [_]find_bit.Word{0, @as(find_bit.Word, 1) << 3};
    const tail_full = [_]find_bit.Word{~@as(find_bit.Word, 0), find_bit.lastWordMask(tail_nbits)};
    const empty = [_]find_bit.Word{};

    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_find_bit_edge) : (idx += 1) {
        checksum +%= @intCast(find_bit.findNextBit(&boundary_set, head_nbits, boundary));
        checksum +%= @intCast(find_bit.findNextAndBit(&boundary_set, &boundary_set, head_nbits, boundary));
        checksum +%= @intCast(find_bit.findNextZeroBit(&boundary_zero, head_nbits, boundary));
        checksum +%= @intCast(find_bit._find_next_bit(&boundary_set, head_nbits, boundary));
        checksum +%= @intCast(find_bit._find_next_and_bit(&boundary_set, &boundary_set, head_nbits, boundary));
        checksum +%= @intCast(find_bit._find_next_zero_bit(&boundary_zero, head_nbits, boundary));
        checksum +%= @intCast(find_bit.find_next_bit(&boundary_set, head_nbits, boundary));
        checksum +%= @intCast(find_bit.find_next_and_bit(&boundary_set, &boundary_set, head_nbits, boundary));
        checksum +%= @intCast(find_bit.find_next_zero_bit(&boundary_zero, head_nbits, boundary));
        checksum +%= @intCast(find_bit.findFirstBit(&tail_set, tail_nbits));
        checksum +%= @intCast(find_bit._find_first_bit(&tail_set, tail_nbits));
        checksum +%= @intCast(find_bit.find_first_bit(&tail_set, tail_nbits));
        checksum +%= @intCast(find_bit.findNextBit(&tail_set, tail_nbits, find_bit.bits_per_long + 4));
        checksum +%= @intCast(find_bit.find_next_bit(&tail_set, tail_nbits, find_bit.bits_per_long + 4));
        checksum +%= @intCast(find_bit.findFirstZeroBit(&tail_full, tail_nbits));
        checksum +%= @intCast(find_bit._find_first_zero_bit(&tail_full, tail_nbits));
        checksum +%= @intCast(find_bit.find_first_zero_bit(&tail_full, tail_nbits));
        checksum +%= @intCast(find_bit.findNextZeroBit(&tail_full, tail_nbits, find_bit.bits_per_long));
        checksum +%= @intCast(find_bit.find_next_zero_bit(&tail_full, tail_nbits, find_bit.bits_per_long));
        checksum +%= @intCast(find_bit.findFirstAndBit(&tail_set, &tail_set, tail_nbits));
        checksum +%= @intCast(find_bit._find_first_and_bit(&tail_set, &tail_set, tail_nbits));
        checksum +%= @intCast(find_bit.find_first_and_bit(&tail_set, &tail_set, tail_nbits));
        checksum +%= @intCast(find_bit.findNextAndBit(&tail_set, &tail_set, tail_nbits, find_bit.bits_per_long + 4));
        checksum +%= @intCast(find_bit.find_next_and_bit(&tail_set, &tail_set, tail_nbits, find_bit.bits_per_long + 4));
        checksum +%= @intCast(find_bit.findLastBit(&tail_set, tail_nbits));
        checksum +%= @intCast(find_bit._find_last_bit(&tail_set, tail_nbits));
        checksum +%= @intCast(find_bit.find_last_bit(&tail_set, tail_nbits));
        checksum +%= @intCast(find_bit.findNextBit(&empty, past_nbits, past_nbits));
        checksum +%= @intCast(find_bit.findNextBit(&empty, past_nbits, past_nbits + 4));
        checksum +%= @intCast(find_bit.findNextZeroBit(&empty, past_nbits, past_nbits));
        checksum +%= @intCast(find_bit.findNextZeroBit(&empty, past_nbits, past_nbits + 4));
        checksum +%= @intCast(find_bit.findNextAndBit(&empty, &empty, past_nbits, past_nbits));
        checksum +%= @intCast(find_bit.findNextAndBit(&empty, &empty, past_nbits, past_nbits + 4));
        checksum +%= @intCast(find_bit.find_next_bit(&empty, past_nbits, past_nbits));
        checksum +%= @intCast(find_bit.find_next_bit(&empty, past_nbits, past_nbits + 4));
        checksum +%= @intCast(find_bit.find_next_zero_bit(&empty, past_nbits, past_nbits));
        checksum +%= @intCast(find_bit.find_next_zero_bit(&empty, past_nbits, past_nbits + 4));
        checksum +%= @intCast(find_bit.find_next_and_bit(&empty, &empty, past_nbits, past_nbits));
        checksum +%= @intCast(find_bit.find_next_and_bit(&empty, &empty, past_nbits, past_nbits + 4));
    }

    return .{ .checksum = checksum };
}

fn stringBench() !struct { checksum: u64 } {
    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_string) : (idx += 1) {
        const even = (idx & 1) == 0;
        const enabled = try string.strtobool(if (even) "on" else "0");
        var trim_buf = [_]u8{ ' ', '\t', 'h', 'i', ' ', '\n' };
        const trimmed = string.trimSpaces(&trim_buf);
        const parsed = string.memparse(if (even) "64K rest" else "-17 tail");
        const dirty = if (even)
            string.memchrInv("aaaaXaaa", 'a')
        else
            string.memchrInv("bbbb", 'b');
        checksum +%= @as(u64, @intFromBool(enabled));
        checksum +%= @intCast(trimmed.len);
        checksum +%= @intCast(parsed.rest.len);
        checksum +%= @as(u64, @intFromBool(dirty != null));
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

fn rbtreeBench() RbtreeBench {
    const RbEntry = struct {
        key: i32,
        serial: usize = 0,
        node: rbtree.Node = rbtree.Node.init(),
    };

    const less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const RbEntry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const RbEntry = @fieldParentPtr("node", rhs);
            return lhs_entry.key < rhs_entry.key;
        }
    }.compare;

    const duplicate_less = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
            const lhs_entry: *const RbEntry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const RbEntry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key != rhs_entry.key) {
                return lhs_entry.key < rhs_entry.key;
            }
            return lhs_entry.serial < rhs_entry.serial;
        }
    }.compare;

    const cmpNode = struct {
        fn compare(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
            const lhs_entry: *const RbEntry = @fieldParentPtr("node", lhs);
            const rhs_entry: *const RbEntry = @fieldParentPtr("node", rhs);
            if (lhs_entry.key < rhs_entry.key) return -1;
            if (lhs_entry.key > rhs_entry.key) return 1;
            return 0;
        }
    }.compare;

    const cmpKey = struct {
        fn compare(key: *const anyopaque, node: *const rbtree.Node) i32 {
            const wanted: *const i32 = @ptrCast(@alignCast(key));
            const entry: *const RbEntry = @fieldParentPtr("node", node);
            if (wanted.* < entry.key) return -1;
            if (wanted.* > entry.key) return 1;
            return 0;
        }
    }.compare;

    var postorder_safe_checksum: u64 = 0;
    var find_add_checksum: u64 = 0;
    var duplicate_checksum: u64 = 0;
    var cached_checksum: u64 = 0;
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
            postorder_safe_checksum +%= @intCast(entry.key + 31);
        }

        rbtree.erase(&entries[1].node, &root);
        rbtree.replaceNode(&entries[0].node, &replacement.node, &root);
        rbtree.eraseInit(&replacement.node, &root);
        postorder_safe_checksum +%= @as(u64, @intFromBool(rbtree.emptyNode(&replacement.node)));

        current = rbtree.firstPostorder(&root);
        while (current) |node| : (current = rbtree.nextPostorder(node)) {
            const entry: *const RbEntry = @fieldParentPtr("node", node);
            postorder_safe_checksum +%= @intCast(entry.key + 17);
        }

        var find_add_entries = [_]RbEntry{
            .{ .key = 10, .serial = 0 },
            .{ .key = 20, .serial = 1 },
            .{ .key = 5, .serial = 2 },
            .{ .key = 10, .serial = 3 },
            .{ .key = 15, .serial = 4 },
        };
        var find_add_root = rbtree.Root.init();
        find_add_checksum +%= @as(u64, @intFromBool(rbtree.findAdd(&find_add_entries[0].node, &find_add_root, cmpNode) == null));
        find_add_checksum +%= @as(u64, @intFromBool(rbtree.findAdd(&find_add_entries[1].node, &find_add_root, cmpNode) == null));
        find_add_checksum +%= @as(u64, @intFromBool(rbtree.findAdd(&find_add_entries[2].node, &find_add_root, cmpNode) == null));
        const existing = rbtree.findAdd(&find_add_entries[3].node, &find_add_root, cmpNode) orelse unreachable;
        const existing_entry: *const RbEntry = @fieldParentPtr("node", existing);
        find_add_checksum +%= @intCast(existing_entry.key + @as(i32, @intCast(existing_entry.serial)));
        find_add_checksum +%= @as(u64, @intFromBool(rbtree.findAdd(&find_add_entries[4].node, &find_add_root, cmpNode) == null));

        var duplicate_entries = [_]RbEntry{
            .{ .key = 10, .serial = 0 },
            .{ .key = 20, .serial = 1 },
            .{ .key = 10, .serial = 2 },
            .{ .key = 5, .serial = 3 },
            .{ .key = 10, .serial = 4 },
            .{ .key = 15, .serial = 5 },
        };
        var duplicate_root = rbtree.Root.init();
        for (&duplicate_entries) |*entry| {
            rbtree.add(&entry.node, &duplicate_root, duplicate_less);
        }

        const wanted = @as(i32, 10);
        const found = rbtree.find(&wanted, &duplicate_root, cmpKey) orelse unreachable;
        const found_entry: *const RbEntry = @fieldParentPtr("node", found);
        duplicate_checksum +%= @intCast(found_entry.key + @as(i32, @intCast(found_entry.serial)));

        const missing = @as(i32, 17);
        duplicate_checksum +%= @as(u64, @intFromBool(rbtree.find(&missing, &duplicate_root, cmpKey) == null));

        const first_match = rbtree.findFirst(&wanted, &duplicate_root, cmpKey) orelse unreachable;
        var cursor = first_match;
        while (true) {
            const entry: *const RbEntry = @fieldParentPtr("node", cursor);
            duplicate_checksum +%= @intCast(entry.key + @as(i32, @intCast(entry.serial)));
            cursor = rbtree.nextMatch(&wanted, cursor, cmpKey) orelse break;
        }

        var duplicate_mutation_entries = [_]RbEntry{
            .{ .key = 10, .serial = 0 },
            .{ .key = 5, .serial = 1 },
            .{ .key = 10, .serial = 2 },
            .{ .key = 20, .serial = 3 },
            .{ .key = 10, .serial = 4 },
            .{ .key = 15, .serial = 5 },
        };
        var replacement_duplicate = RbEntry{ .key = 10, .serial = 6 };
        var duplicate_mutation_root = rbtree.Root.init();
        for (&duplicate_mutation_entries) |*entry| {
            rbtree.add(&entry.node, &duplicate_mutation_root, duplicate_less);
        }

        rbtree.erase(&duplicate_mutation_entries[2].node, &duplicate_mutation_root);
        var after_erase = rbtree.findFirst(&wanted, &duplicate_mutation_root, cmpKey) orelse unreachable;
        while (true) {
            const entry: *const RbEntry = @fieldParentPtr("node", after_erase);
            duplicate_checksum +%= entry.serial + 97;
            after_erase = rbtree.nextMatch(&wanted, after_erase, cmpKey) orelse break;
        }

        rbtree.replaceNode(&duplicate_mutation_entries[4].node, &replacement_duplicate.node, &duplicate_mutation_root);
        var after_replace = rbtree.findFirst(&wanted, &duplicate_mutation_root, cmpKey) orelse unreachable;
        while (true) {
            const entry: *const RbEntry = @fieldParentPtr("node", after_replace);
            duplicate_checksum +%= entry.serial + 107;
            after_replace = rbtree.nextMatch(&wanted, after_replace, cmpKey) orelse break;
        }

        var cached_entries = [_]RbEntry{
            .{ .key = 10 },
            .{ .key = 5 },
            .{ .key = 20 },
            .{ .key = 15 },
        };
        var cached_replacement = RbEntry{ .key = 10 };
        var new_leftmost = RbEntry{ .key = 3 };
        var cached_root = rbtree.RootCached.init();

        for (&cached_entries) |*entry| {
            rbtree.addCached(&entry.node, &cached_root, less);
        }

        cached_checksum +%= @as(u64, @intFromBool(rbtree.first(&cached_root.root) == rbtree.firstCached(&cached_root)));
        const initial_leftmost_entry: *const RbEntry = @fieldParentPtr("node", rbtree.firstCached(&cached_root).?);
        cached_checksum +%= @intCast(initial_leftmost_entry.key);
        cached_checksum +%= @as(u64, @intFromBool(rbtree.eraseCached(&cached_entries[2].node, &cached_root) == null));
        const still_leftmost_entry: *const RbEntry = @fieldParentPtr("node", rbtree.firstCached(&cached_root).?);
        cached_checksum +%= @intCast(still_leftmost_entry.key);

        const promoted_leftmost = rbtree.eraseCached(&cached_entries[1].node, &cached_root) orelse unreachable;
        const promoted_leftmost_entry: *const RbEntry = @fieldParentPtr("node", promoted_leftmost);
        cached_checksum +%= @intCast(promoted_leftmost_entry.key);
        cached_checksum +%= @as(u64, @intFromBool(rbtree.first(&cached_root.root) == rbtree.firstCached(&cached_root)));

        rbtree.replaceNodeCached(&cached_entries[0].node, &cached_replacement.node, &cached_root);
        const replacement_leftmost_entry: *const RbEntry = @fieldParentPtr("node", rbtree.firstCached(&cached_root).?);
        cached_checksum +%= @intCast(replacement_leftmost_entry.key);

        rbtree.addCached(&new_leftmost.node, &cached_root, less);
        const new_leftmost_entry: *const RbEntry = @fieldParentPtr("node", rbtree.firstCached(&cached_root).?);
        cached_checksum +%= @intCast(new_leftmost_entry.key);
        cached_checksum +%= @as(u64, @intFromBool(rbtree.first(&cached_root.root) == rbtree.firstCached(&cached_root)));
    }

    const checksum = postorder_safe_checksum +% find_add_checksum +% duplicate_checksum +% cached_checksum;
    return .{
        .checksum = checksum,
        .postorder_safe_checksum = postorder_safe_checksum,
        .find_add_checksum = find_add_checksum,
        .duplicate_checksum = duplicate_checksum,
        .cached_checksum = cached_checksum,
    };
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
    std.debug.assert(rbtree_result.postorder_safe_checksum != 0);
    std.debug.assert(rbtree_result.find_add_checksum != 0);
    std.debug.assert(rbtree_result.duplicate_checksum != 0);
    std.debug.assert(rbtree_result.cached_checksum != 0);

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
    try stdout_writer.interface.print(
        "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM={d}\n",
        .{rbtree_result.postorder_safe_checksum},
    );
    try stdout_writer.interface.print(
        "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM={d}\n",
        .{rbtree_result.find_add_checksum},
    );
    try stdout_writer.interface.print(
        "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM={d}\n",
        .{rbtree_result.duplicate_checksum},
    );
    try stdout_writer.interface.print(
        "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\n",
        .{rbtree_result.cached_checksum},
    );
    try stdout_writer.interface.flush();
}
