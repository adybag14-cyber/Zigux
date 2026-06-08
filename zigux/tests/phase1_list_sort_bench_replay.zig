const std = @import("std");
const list_sort = @import("list_sort");

const iterations_list_sort: u64 = 1000;

const ListEntry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn benchLess(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const ListEntry = @fieldParentPtr("node", a);
    const rhs: *const ListEntry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn runOnePass() struct {
    keys: [5]i32,
    ordinals: [5]usize,
    checksum: u64,
} {
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

    list_sort.listSort(null, &head, benchLess);

    var keys: [5]i32 = undefined;
    var ordinals: [5]usize = undefined;
    var checksum: u64 = 0;
    var idx: usize = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const ListEntry = @fieldParentPtr("node", current.?);
        keys[idx] = entry.key;
        ordinals[idx] = entry.ordinal;
        checksum +%= @intCast(entry.ordinal);
        tryLinks(current.?);
        idx += 1;
    }

    std.debug.assert(idx == keys.len);
    return .{
        .keys = keys,
        .ordinals = ordinals,
        .checksum = checksum,
    };
}

fn tryLinks(node: *const list_sort.ListHead) void {
    std.debug.assert(node.next.?.prev == node);
    std.debug.assert(node.prev.?.next == node);
}

fn listSortBenchChecksum() u64 {
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_list_sort) : (idx += 1) {
        checksum +%= runOnePass().checksum;
    }
    return checksum;
}

test "list_sort bench replay preserves stable key and ordinal order" {
    const pass = runOnePass();
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 3, 3 }, &pass.keys);
    try std.testing.expectEqualSlices(usize, &.{ 1, 3, 0, 2, 4 }, &pass.ordinals);
    try std.testing.expectEqual(@as(u64, 10), pass.checksum);
}

test "list_sort bench replay matches aggregate Phase 1 checksum" {
    try std.testing.expectEqual(@as(u64, 10000), listSortBenchChecksum());
}
