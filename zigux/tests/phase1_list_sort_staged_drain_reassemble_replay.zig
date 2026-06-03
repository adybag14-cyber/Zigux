const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

fn cmpAscending(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs: *const Entry = @fieldParentPtr("node", a);
    const rhs: *const Entry = @fieldParentPtr("node", b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn cmpDescending(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    return -cmpAscending(null, a, b);
}

fn collect(head: *const ListHead, keys: []i32, ordinals: []usize) !usize {
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        keys[count] = entry.key;
        ordinals[count] = entry.ordinal;
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        count += 1;
    }
    return count;
}

test "list sort survives alternating staged drain and reassembly" {
    var head: ListHead = .{};
    head.init();
    var staging: ListHead = .{};
    staging.init();

    var entries = [_]Entry{
        .{ .key = 6, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 6, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 5, .ordinal = 4 },
        .{ .key = 2, .ordinal = 5 },
        .{ .key = 4, .ordinal = 6 },
        .{ .key = 1, .ordinal = 7 },
        .{ .key = 5, .ordinal = 8 },
        .{ .key = 3, .ordinal = 9 },
    };

    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    var index: usize = 0;
    var current = head.next;
    while (current != &head) {
        const next = current.?.next;
        if ((index & 1) == 1) {
            list_sort.listDel(current.?);
            list_sort.listAddTail(current.?, &staging);
        }
        index += 1;
        current = next;
    }

    list_sort.listSort(null, &staging, cmpDescending);

    while (!list_sort.listEmpty(&staging)) {
        const node = staging.next.?;
        list_sort.listDel(node);
        list_sort.listAddTail(node, &head);
    }

    list_sort.listSort(null, &head, cmpAscending);

    var keys: [entries.len]i32 = undefined;
    var ordinals: [entries.len]usize = undefined;
    const count = try collect(&head, &keys, &ordinals);

    try std.testing.expectEqual(@as(usize, entries.len), count);
    try std.testing.expectEqualSlices(i32, &.{ 1, 1, 2, 2, 3, 4, 5, 5, 6, 6 }, keys[0..count]);
    try std.testing.expectEqualSlices(usize, &.{ 3, 7, 1, 5, 9, 6, 4, 8, 0, 2 }, ordinals[0..count]);
    try std.testing.expect(head.next == &entries[3].node);
    try std.testing.expect(head.prev == &entries[2].node);
    try std.testing.expect(list_sort.listEmpty(&staging));
}
