const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

fn cmpKey(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn cmpModuloBucket(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_bucket = @mod(lhs.key, 3);
    const rhs_bucket = @mod(rhs.key, 3);
    if (lhs_bucket == rhs_bucket) return 0;
    return if (lhs_bucket < rhs_bucket) -1 else 1;
}

fn expectDetached(node: *const ListHead) !void {
    try std.testing.expect(node.next == null);
    try std.testing.expect(node.prev == null);
}

fn expectHeadLinks(head: *const ListHead) !void {
    try std.testing.expect(head.next.?.prev == head);
    try std.testing.expect(head.prev.?.next == head);
}

fn collectOrdinals(head: *const ListHead, out: []usize) ![]usize {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        idx += 1;
    }
    return out[0..idx];
}

fn collectKeys(head: *const ListHead, out: []i32) []i32 {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.key;
        idx += 1;
    }
    return out[0..idx];
}

test "list sort survives reverse-pair staging before stable bucket replay" {
    var head: ListHead = .{};
    head.init();
    var pair_heads = [_]ListHead{.{}} ** 5;
    for (&pair_heads) |*pair_head| pair_head.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 8, .ordinal = 2 },
        .{ .key = 2, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 1, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
        .{ .key = 5, .ordinal = 7 },
        .{ .key = 3, .ordinal = 8 },
        .{ .key = 7, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);

    list_sort.listSort(null, &head, cmpKey);

    var ordinals: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(usize, &.{ 5, 1, 3, 8, 6, 4, 7, 0, 9, 2 }, try collectOrdinals(&head, &ordinals));
    try expectHeadLinks(&head);

    for (&pair_heads) |*pair_head| {
        const first = head.next.?;
        list_sort.listDel(first);
        try expectDetached(first);

        const second = head.next.?;
        list_sort.listDel(second);
        try expectDetached(second);

        list_sort.listAddTail(first, pair_head);
        list_sort.listAdd(second, pair_head);
        try expectHeadLinks(pair_head);
    }

    try std.testing.expect(list_sort.listEmpty(&head));

    for (&pair_heads) |*pair_head| {
        while (!list_sort.listEmpty(pair_head)) {
            const node = pair_head.next.?;
            list_sort.listDel(node);
            try expectDetached(node);
            list_sort.listAddTail(node, &head);
        }
        try std.testing.expect(list_sort.listEmpty(pair_head));
    }

    try std.testing.expectEqualSlices(usize, &.{ 1, 5, 8, 3, 4, 6, 0, 7, 2, 9 }, try collectOrdinals(&head, &ordinals));
    try expectHeadLinks(&head);

    list_sort.listSort(null, &head, cmpModuloBucket);

    var keys: [entries.len]i32 = undefined;
    try std.testing.expectEqualSlices(usize, &.{ 8, 0, 5, 6, 9, 1, 3, 4, 7, 2 }, try collectOrdinals(&head, &ordinals));
    try std.testing.expectEqualSlices(i32, &.{ 3, 6, 1, 4, 7, 2, 2, 5, 5, 8 }, collectKeys(&head, &keys));
    try std.testing.expect(head.next == &entries[8].node);
    try std.testing.expect(head.prev == &entries[2].node);
    try expectHeadLinks(&head);
}
