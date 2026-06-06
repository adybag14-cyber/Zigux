const std = @import("std");
const list_sort = @import("list_sort");

const ListHead = list_sort.ListHead;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: ListHead = .{},
};

fn entryFromNode(node: *const ListHead) *const Entry {
    return @fieldParentPtr("node", node);
}

fn cmpKeyAsc(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    return 0;
}

fn cmpKeyDesc(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    return cmpKeyAsc(null, b, a);
}

fn cmpKeyAscOrdinalDesc(_: ?*anyopaque, a: *const ListHead, b: *const ListHead) i32 {
    const lhs = entryFromNode(a);
    const rhs = entryFromNode(b);
    if (lhs.key < rhs.key) return -1;
    if (lhs.key > rhs.key) return 1;
    if (lhs.ordinal > rhs.ordinal) return -1;
    if (lhs.ordinal < rhs.ordinal) return 1;
    return 0;
}

fn cmpAllTies(_: ?*anyopaque, _: *const ListHead, _: *const ListHead) i32 {
    return 0;
}

fn collectOrdinals(head: *const ListHead, out: []usize) usize {
    var count: usize = 0;
    var current = head.next;
    while (current != head) : (current = current.?.next) {
        out[count] = entryFromNode(current.?).ordinal;
        count += 1;
    }
    return count;
}

fn expectOrdinals(head: *const ListHead, expected: []const usize) !void {
    var actual: [16]usize = undefined;
    const count = collectOrdinals(head, &actual);
    try std.testing.expectEqual(expected.len, count);
    try std.testing.expectEqualSlices(usize, expected, actual[0..count]);
}

fn expectCircularLinks(head: *const ListHead, expected_len: usize) !void {
    var forward_count: usize = 0;
    var current = head.next;
    var previous: *const ListHead = head;
    while (current != head) : (current = current.?.next) {
        try std.testing.expectEqual(previous, current.?.prev.?);
        previous = current.?;
        forward_count += 1;
    }
    try std.testing.expectEqual(expected_len, forward_count);
    try std.testing.expectEqual(previous, head.prev.?);

    var reverse_count: usize = 0;
    current = head.prev;
    previous = head;
    while (current != head) : (current = current.?.prev) {
        try std.testing.expectEqual(previous, current.?.next.?);
        previous = current.?;
        reverse_count += 1;
    }
    try std.testing.expectEqual(expected_len, reverse_count);
    try std.testing.expectEqual(previous, head.next.?);
}

fn popFront(head: *ListHead) ?*ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.next.?;
    list_sort.listDel(node);
    return node;
}

fn popBack(head: *ListHead) ?*ListHead {
    if (list_sort.listEmpty(head)) return null;
    const node = head.prev.?;
    list_sort.listDel(node);
    return node;
}

test "list sort pivot ladder detach rejoin replay" {
    var head: ListHead = .{};
    var low: ListHead = .{};
    var pivot: ListHead = .{};
    var high: ListHead = .{};
    head.init();
    low.init();
    pivot.init();
    high.init();

    var entries = [_]Entry{
        .{ .key = 5, .ordinal = 0 },
        .{ .key = 2, .ordinal = 1 },
        .{ .key = 4, .ordinal = 2 },
        .{ .key = 1, .ordinal = 3 },
        .{ .key = 6, .ordinal = 4 },
        .{ .key = 4, .ordinal = 5 },
        .{ .key = 3, .ordinal = 6 },
        .{ .key = 6, .ordinal = 7 },
        .{ .key = 2, .ordinal = 8 },
        .{ .key = 5, .ordinal = 9 },
    };

    for (&entries) |*entry| list_sort.listAddTail(&entry.node, &head);
    list_sort.listSort(null, &head, cmpKeyAsc);
    try expectOrdinals(&head, &.{ 3, 1, 8, 6, 2, 5, 0, 9, 4, 7 });
    try expectCircularLinks(&head, entries.len);

    while (!list_sort.listEmpty(&head)) {
        const node = head.next.?;
        const entry = entryFromNode(node);
        list_sort.listDel(node);
        try std.testing.expectEqual(@as(?*ListHead, null), node.next);
        try std.testing.expectEqual(@as(?*ListHead, null), node.prev);

        if (entry.key < 4) {
            list_sort.listAddTail(node, &low);
        } else if (entry.key == 4) {
            list_sort.listAddTail(node, &pivot);
        } else {
            list_sort.listAddTail(node, &high);
        }
    }
    try std.testing.expect(list_sort.listEmpty(&head));
    try expectOrdinals(&low, &.{ 3, 1, 8, 6 });
    try expectOrdinals(&pivot, &.{ 2, 5 });
    try expectOrdinals(&high, &.{ 0, 9, 4, 7 });

    list_sort.listSort(null, &low, cmpKeyDesc);
    list_sort.listSort(null, &pivot, cmpAllTies);
    list_sort.listSort(null, &high, cmpKeyAscOrdinalDesc);
    try expectOrdinals(&low, &.{ 6, 1, 8, 3 });
    try expectOrdinals(&pivot, &.{ 2, 5 });
    try expectOrdinals(&high, &.{ 9, 0, 7, 4 });

    while (!list_sort.listEmpty(&low) or !list_sort.listEmpty(&pivot) or !list_sort.listEmpty(&high)) {
        if (popFront(&low)) |node| list_sort.listAddTail(node, &head);
        if (popFront(&pivot)) |node| list_sort.listAddTail(node, &head);
        if (popBack(&high)) |node| list_sort.listAddTail(node, &head);
        if (popFront(&high)) |node| list_sort.listAddTail(node, &head);
    }

    try std.testing.expect(list_sort.listEmpty(&low));
    try std.testing.expect(list_sort.listEmpty(&pivot));
    try std.testing.expect(list_sort.listEmpty(&high));
    try expectOrdinals(&head, &.{ 6, 2, 4, 9, 1, 5, 7, 0, 8, 3 });
    try expectCircularLinks(&head, entries.len);

    list_sort.listSort(null, &head, cmpAllTies);
    try expectOrdinals(&head, &.{ 6, 2, 4, 9, 1, 5, 7, 0, 8, 3 });
    try expectCircularLinks(&head, entries.len);
}
