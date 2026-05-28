const std = @import("std");
const find_bit = @import("find_bit");
const bitmap = @import("bitmap");
const hweight = @import("hweight");
const list_sort = @import("list_sort");
const rbtree = @import("rbtree");
const string = @import("string");

const iterations_bitmap_weight: u64 = 20000;
const iterations_bitmap_window: u64 = 20000;
const iterations_find_bit: u64 = 20000;
const iterations_find_bit_edge: u64 = 20000;
const iterations_string: u64 = 40000;
const iterations_hweight: u64 = 100000;
const iterations_list_sort: u64 = 1000;
const iterations_rbtree: u64 = 4000;

const ListEntry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const TreeEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),

    fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
        const lhs_entry: *const TreeEntry = @fieldParentPtr("node", lhs);
        const rhs_entry: *const TreeEntry = @fieldParentPtr("node", rhs);
        if (lhs_entry.key != rhs_entry.key) {
            return lhs_entry.key < rhs_entry.key;
        }
        return lhs_entry.serial < rhs_entry.serial;
    }

    fn cmp(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
        const lhs_entry: *const TreeEntry = @fieldParentPtr("node", lhs);
        const rhs_entry: *const TreeEntry = @fieldParentPtr("node", rhs);
        if (lhs_entry.key < rhs_entry.key) return -1;
        if (lhs_entry.key > rhs_entry.key) return 1;
        return 0;
    }

    fn keyCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
        const wanted: *const i32 = @ptrCast(@alignCast(key));
        const entry: *const TreeEntry = @fieldParentPtr("node", node);
        if (wanted.* < entry.key) return -1;
        if (wanted.* > entry.key) return 1;
        return 0;
    }
};

fn bitmapWeightBench() struct { checksum: u64 } {
    const nbits = find_bit.bits_per_long + 5;
    const map = [_]find_bit.Word{ 0b1111, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 8) };
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_bitmap_weight) : (idx += 1) {
        checksum +%= @intCast(bitmap.weight(&map, nbits));
    }
    return .{ .checksum = checksum };
}

fn bitmapWindowBench() struct { checksum: u64 } {
    const nbits = find_bit.bits_per_long + 5;
    const lhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 1) | (@as(find_bit.Word, 1) << 8) };
    const rhs = [_]find_bit.Word{ 0, (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 9) };
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_bitmap_window) : (idx += 1) {
        var dst = [_]find_bit.Word{ 0, 0 };
        checksum +%= @intCast(bitmap.weightedOr(&dst, &lhs, &rhs, nbits));
        checksum +%= @intCast(bitmap.weightedXor(&dst, &lhs, &rhs, nbits));
        checksum +%= @intCast(bitmap.weight(&dst, nbits));
    }
    return .{ .checksum = checksum };
}

fn findBitBench() struct { checksum: u64 } {
    const head_nbits = find_bit.bits_per_long * 2;
    const boundary = find_bit.bits_per_long - 1;
    const boundary_set = [_]find_bit.Word{
        @as(find_bit.Word, 1) << @intCast(boundary),
        (@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 5),
    };
    const boundary_zero = [_]find_bit.Word{
        0,
        ~((@as(find_bit.Word, 1) << 0) | (@as(find_bit.Word, 1) << 5)),
    };
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_find_bit) : (idx += 1) {
        checksum +%= @intCast(find_bit.findNextBit(&boundary_set, head_nbits, boundary));
        checksum +%= @intCast(find_bit.findNextAndBit(&boundary_set, &boundary_set, head_nbits, boundary));
        checksum +%= @intCast(find_bit.findNextZeroBit(&boundary_zero, head_nbits, boundary));
    }
    return .{ .checksum = checksum };
}

fn findBitEdgeBench() struct { checksum: u64 } {
    const tail_nbits = find_bit.bits_per_long + 5;
    const tail_set = [_]find_bit.Word{
        0,
        (@as(find_bit.Word, 1) << 3) | (@as(find_bit.Word, 1) << 7),
    };
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_find_bit_edge) : (idx += 1) {
        checksum +%= @intCast(find_bit.findFirstBit(&tail_set, tail_nbits));
        checksum +%= @intCast(find_bit.findFirstAndBit(&tail_set, &tail_set, tail_nbits));
        checksum +%= @intCast(find_bit.findLastBit(&tail_set, tail_nbits));
    }
    return .{ .checksum = checksum };
}

fn stringBench() struct { checksum: u64 } {
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_string) : (idx += 1) {
        var appended = [_]u8{ 'h', 'i', 0, 'x', 'x', 'x' };
        checksum +%= @intCast(string.strlcat(appended[0..], "all"));
        checksum +%= @intCast(string.strspn("abba!", "ab"));
        checksum +%= @intCast(string.sysfsMatchString(&[_][]const u8{ "disabled", "auto\n", "manual" }, "auto").?);
    }
    return .{ .checksum = checksum };
}

fn hweightBench() struct { checksum: u64 } {
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_hweight) : (idx += 1) {
        checksum +%= hweight.swHweight8(0xf0);
        checksum +%= hweight.swHweight16(0xf0f0);
        checksum +%= hweight.swHweight32(0xf0f0_f0f0);
        checksum +%= hweight.swHweight64(0xf0f0_f0f0_f0f0_f0f0);
        checksum +%= @intCast(hweight.hweightLong(0xf0f0));
    }
    return .{ .checksum = checksum };
}

fn listSortBench() struct { checksum: u64 } {
    const cmp = struct {
        fn less(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
            const lhs: *const ListEntry = @fieldParentPtr("node", a);
            const rhs: *const ListEntry = @fieldParentPtr("node", b);
            if (lhs.key < rhs.key) return -1;
            if (lhs.key > rhs.key) return 1;
            return 0;
        }
    }.less;

    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_list_sort) : (idx += 1) {
        var head: list_sort.ListHead = .{};
        head.init();
        var entries = [_]ListEntry{
            .{ .key = 2, .ordinal = 0 },
            .{ .key = 1, .ordinal = 1 },
            .{ .key = 3, .ordinal = 2 },
            .{ .key = 1, .ordinal = 3 },
            .{ .key = 3, .ordinal = 4 },
        };
        for (&entries) |*entry| {
            list_sort.listAddTail(&entry.node, &head);
        }
        list_sort.listSort(null, &head, cmp);
        var current = head.next;
        while (current != &head) : (current = current.?.next) {
            const entry: *const ListEntry = @fieldParentPtr("node", current.?);
            checksum +%= @intCast(entry.ordinal);
        }
    }
    return .{ .checksum = checksum };
}

fn rbtreeBench() struct { checksum: u64 } {
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_rbtree) : (idx += 1) {
        var entries = [_]TreeEntry{
            .{ .key = 2, .serial = 0 },
            .{ .key = 1, .serial = 1 },
            .{ .key = 3, .serial = 2 },
        };
        var root = rbtree.Root.init();
        for (&entries) |*entry| {
            rbtree.add(&entry.node, &root, TreeEntry.less);
        }
        var node = rbtree.first(&root);
        while (node) |current| : (node = rbtree.next(current)) {
            const entry: *const TreeEntry = @fieldParentPtr("node", current);
            checksum +%= @intCast(entry.key);
        }
    }
    return .{ .checksum = checksum };
}

fn rbtreePostorderSafeBench() struct { checksum: u64 } {
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_rbtree) : (idx += 1) {
        var entries = [_]TreeEntry{
            .{ .key = 2, .serial = 0 },
            .{ .key = 1, .serial = 1 },
            .{ .key = 3, .serial = 2 },
        };
        var root = rbtree.Root.init();
        for (&entries) |*entry| {
            rbtree.add(&entry.node, &root, TreeEntry.less);
        }
        var node = rbtree.firstPostorder(&root);
        while (node) |current| : (node = rbtree.nextPostorder(current)) {
            const entry: *const TreeEntry = @fieldParentPtr("node", current);
            checksum +%= @intCast(entry.key);
        }
    }
    return .{ .checksum = checksum };
}

fn rbtreeFindAddBench() struct { checksum: u64 } {
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_rbtree) : (idx += 1) {
        var entries = [_]TreeEntry{
            .{ .key = 10, .serial = 0 },
            .{ .key = 5, .serial = 1 },
            .{ .key = 15, .serial = 2 },
        };
        var probe = TreeEntry{ .key = 15, .serial = 3 };
        var root = rbtree.Root.init();
        for (&entries) |*entry| {
            rbtree.add(&entry.node, &root, TreeEntry.less);
        }
        const existing = rbtree.findAdd(&probe.node, &root, TreeEntry.cmp);
        const found = existing orelse unreachable;
        const entry: *const TreeEntry = @fieldParentPtr("node", found);
        checksum +%= @intCast(entry.serial);
    }
    return .{ .checksum = checksum };
}

fn rbtreeDuplicateBench() struct { checksum: u64 } {
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_rbtree) : (idx += 1) {
        var entries = [_]TreeEntry{
            .{ .key = 10, .serial = 0 },
            .{ .key = 20, .serial = 1 },
            .{ .key = 10, .serial = 2 },
            .{ .key = 5, .serial = 3 },
            .{ .key = 10, .serial = 4 },
        };
        var root = rbtree.Root.init();
        for (&entries) |*entry| {
            rbtree.add(&entry.node, &root, TreeEntry.less);
        }
        const duplicate_key = @as(i32, 10);
        var iter = rbtree.matchIterator(&duplicate_key, &root, TreeEntry.keyCmp);
        while (iter.next()) |current| {
            const entry: *const TreeEntry = @fieldParentPtr("node", current);
            checksum +%= @intCast(entry.serial);
        }
    }
    return .{ .checksum = checksum };
}

fn rbtreeCachedBench() struct { checksum: u64 } {
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_rbtree) : (idx += 1) {
        var entries = [_]TreeEntry{
            .{ .key = 10, .serial = 0 },
            .{ .key = 5, .serial = 1 },
            .{ .key = 15, .serial = 2 },
        };
        var cached_root = rbtree.RootCached.init();
        for (&entries) |*entry| {
            _ = rbtree.addCached(&entry.node, &cached_root, TreeEntry.less);
        }
        const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &cached_root);
        const promoted = promoted_leftmost orelse unreachable;
        const entry: *const TreeEntry = @fieldParentPtr("node", promoted);
        checksum +%= @intCast(entry.serial + 1);
    }
    return .{ .checksum = checksum };
}

pub fn main() !void {
    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = std.fs.File.stdout().writer(&stdout_buffer);

    const bitmap_weight_result = bitmapWeightBench();
    const bitmap_window_result = bitmapWindowBench();
    const find_bit_result = findBitBench();
    const find_bit_edge_result = findBitEdgeBench();
    const string_result = stringBench();
    const hweight_result = hweightBench();
    const list_sort_result = listSortBench();
    const rbtree_result = rbtreeBench();
    const rbtree_postorder_safe_result = rbtreePostorderSafeBench();
    const rbtree_find_add_result = rbtreeFindAddBench();
    const rbtree_duplicate_result = rbtreeDuplicateBench();
    const rbtree_cached_result = rbtreeCachedBench();

    try stdout_writer.interface.print("PHASE1_BENCH=pass\n", .{});
    try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS={d}\n", .{iterations_bitmap_weight});
    try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS={d}\n", .{iterations_bitmap_window});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS={d}\n", .{iterations_find_bit});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS={d}\n", .{iterations_find_bit_edge});
    try stdout_writer.interface.print("PHASE1_BENCH_STRING_ITERATIONS={d}\n", .{iterations_string});
    try stdout_writer.interface.print("PHASE1_BENCH_HWEIGHT_ITERATIONS={d}\n", .{iterations_hweight});
    try stdout_writer.interface.print("PHASE1_BENCH_LIST_SORT_ITERATIONS={d}\n", .{iterations_list_sort});
    try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_ITERATIONS={d}\n", .{iterations_rbtree});
    try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM={d}\n", .{bitmap_weight_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM={d}\n", .{bitmap_window_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM={d}\n", .{find_bit_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}\n", .{find_bit_edge_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_STRING_CHECKSUM={d}\n", .{string_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_HWEIGHT_CHECKSUM={d}\n", .{hweight_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_LIST_SORT_CHECKSUM={d}\n", .{list_sort_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CHECKSUM={d}\n", .{rbtree_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM={d}\n", .{rbtree_postorder_safe_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM={d}\n", .{rbtree_find_add_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM={d}\n", .{rbtree_duplicate_result.checksum});
    try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\n", .{rbtree_cached_result.checksum});
    try stdout_writer.interface.flush();
}
