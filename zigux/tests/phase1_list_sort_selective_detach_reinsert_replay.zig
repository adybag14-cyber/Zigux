const std = @import("std");
const list_sort = @import("list_sort");

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

fn keyCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);

    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn descendingKeyCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    return -keyCmp(null, a, b);
}

fn moduloBucketCmp(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    const lhs_bucket = @mod(lhs.key, 4);
    const rhs_bucket = @mod(rhs.key, 4);

    if (lhs_bucket < rhs_bucket) return -1;
    if (lhs_bucket > rhs_bucket) return 1;
    return 0;
}

fn collectOrdinals(head: *const list_sort.ListHead, out: []usize) ![]usize {
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

fn collectKeys(head: *const list_sort.ListHead, out: []i32) []i32 {
    var idx: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        out[idx] = entry.key;
        idx += 1;
    }
    return out[0..idx];
}

test "selective detach and reinsert preserves stable bucket order" {
    var head: list_sort.ListHead = .{};
    head.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 1, .ordinal = 1 },
        .{ .key = 9, .ordinal = 2 },
        .{ .key = 4, .ordinal = 3 },
        .{ .key = 13, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 8, .ordinal = 6 },
        .{ .key = 5, .ordinal = 7 },
        .{ .key = 10, .ordinal = 8 },
        .{ .key = 0, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);
    list_sort.listSort(null, &head, keyCmp);

    var staging: list_sort.ListHead = .{};
    staging.init();

    for (&[_]usize{ 1, 4, 7 }) |entry_idx| {
        list_sort.listDel(&entries[entry_idx].node);
        try std.testing.expect(entries[entry_idx].node.next == null);
        try std.testing.expect(entries[entry_idx].node.prev == null);
        list_sort.listAddTail(&entries[entry_idx].node, &staging);
    }

    list_sort.listSort(null, &head, descendingKeyCmp);
    list_sort.listSort(null, &staging, descendingKeyCmp);

    while (!list_sort.listEmpty(&staging)) {
        const node = staging.next.?;
        list_sort.listDel(node);
        list_sort.listAddTail(node, &head);
    }

    var pre_bucket_ordinals: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(
        usize,
        &.{ 8, 2, 6, 0, 3, 5, 9, 4, 7, 1 },
        try collectOrdinals(&head, &pre_bucket_ordinals),
    );

    list_sort.listSort(null, &head, moduloBucketCmp);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    try std.testing.expectEqualSlices(
        i32,
        &.{ 8, 4, 0, 9, 13, 5, 1, 10, 6, 2 },
        collectKeys(&head, &keys),
    );
    try std.testing.expectEqualSlices(
        usize,
        &.{ 6, 3, 9, 2, 4, 7, 1, 8, 0, 5 },
        try collectOrdinals(&head, &ordinals),
    );
    try std.testing.expect(head.next == &entries[6].node);
    try std.testing.expect(head.prev == &entries[5].node);
}
